from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin, require_companion, require_family_member
from ..database import get_db
from ..models import (
    AuditLog,
    CompanionAvailability,
    CompanionProfile,
    FamilyParent,
    ParentAuthorization,
    ParentConsent,
    ParentProfile,
    User,
    Visit,
)
from ..schemas import (
    ParentLinkRequest,
    VisitActionRequest,
    VisitAssignmentRequest,
    VisitCreateRequest,
    VisitResponse,
)


router = APIRouter(prefix="/api/v1/carecircle", tags=["visits"])

ACTIVE_VISIT_STATUSES = ("assigned", "accepted", "in_progress")
FAMILY_CANCELLABLE_STATUSES = ("requested", "assigned", "accepted")


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def require_parent_booking_access(db: Session, user: User, parent_id: str):
    membership = require_family_member(db, user)
    authorization = (
        db.query(ParentAuthorization)
        .join(FamilyParent, FamilyParent.parent_id == ParentAuthorization.parent_id)
        .filter(
            ParentAuthorization.parent_id == parent_id,
            ParentAuthorization.family_member_id == membership.id,
            ParentAuthorization.status == "active",
            ParentAuthorization.can_view_visits.is_(True),
            FamilyParent.family_id == membership.family_id,
            FamilyParent.status == "active",
        )
        .first()
    )
    if authorization is None:
        raise HTTPException(status_code=403, detail="Visit booking is not authorized for this parent")
    return membership, authorization


def require_active_parent_consent(db: Session, parent_id: str) -> ParentConsent:
    now = datetime.now(timezone.utc)
    consents = db.query(ParentConsent).filter(
        ParentConsent.parent_id == parent_id,
        ParentConsent.consent_source == "parent",
        ParentConsent.status == "active",
    ).order_by(ParentConsent.created_at.desc()).all()
    for consent in consents:
        if consent.effective_at and as_utc(consent.effective_at) > now:
            continue
        if consent.expires_at and as_utc(consent.expires_at) <= now:
            continue
        return consent
    raise HTTPException(status_code=409, detail="Current personal consent from the parent is required for visits")


def get_family_visit(db: Session, user: User, visit_id: str) -> Visit:
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if visit is None:
        raise HTTPException(status_code=404, detail="Visit not found")
    membership, _ = require_parent_booking_access(db, user, visit.parent_id)
    if visit.family_id != membership.family_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this visit")
    return visit


def get_assigned_visit(db: Session, user: User, visit_id: str) -> Visit:
    require_companion(user)
    visit = db.query(Visit).join(CompanionProfile, Visit.companion_id == CompanionProfile.id).filter(
        Visit.id == visit_id,
        CompanionProfile.user_id == user.id,
    ).first()
    if visit is None:
        raise HTTPException(status_code=404, detail="Assigned visit not found")
    return visit


@router.post("/visits", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
def request_visit(
    payload: VisitCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = db.query(ParentProfile).filter(
        ParentProfile.id == payload.parent_id,
        ParentProfile.status == "active",
    ).first()
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent profile not found")
    membership, _ = require_parent_booking_access(db, current_user, parent.id)
    require_active_parent_consent(db, parent.id)
    visit = Visit(
        family_id=membership.family_id,
        parent_id=parent.id,
        booked_by_user_id=current_user.id,
        scheduled_start=payload.scheduled_start,
        duration_minutes=payload.duration_minutes,
        requirements=payload.requirements,
        status="requested",
    )
    db.add(visit)
    db.flush()
    db.add(AuditLog(
        user_id=current_user.id,
        action="request_visit",
        entity_type="visit",
        entity_id=visit.id,
    ))
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/visits", response_model=list[VisitResponse])
def family_visit_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = require_family_member(db, current_user)
    return (
        db.query(Visit)
        .join(FamilyParent, FamilyParent.parent_id == Visit.parent_id)
        .join(
            ParentAuthorization,
            (ParentAuthorization.parent_id == Visit.parent_id)
            & (ParentAuthorization.family_member_id == membership.id),
        )
        .filter(
            Visit.family_id == membership.family_id,
            FamilyParent.family_id == membership.family_id,
            FamilyParent.status == "active",
            ParentAuthorization.status == "active",
            ParentAuthorization.can_view_visits.is_(True),
        )
        .order_by(Visit.scheduled_start.desc())
        .all()
    )


@router.get("/companion/visits", response_model=list[VisitResponse])
def companion_visits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_companion(current_user)
    profile = db.query(CompanionProfile).filter(CompanionProfile.user_id == current_user.id).first()
    if profile is None:
        return []
    return db.query(Visit).filter(
        Visit.companion_id == profile.id,
        Visit.status.in_(("assigned", "accepted", "in_progress", "completed")),
    ).order_by(Visit.scheduled_start).all()


@router.post("/visits/{visit_id}/accept", response_model=VisitResponse)
def accept_visit(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = get_assigned_visit(db, current_user, visit_id)
    if visit.status != "assigned":
        raise HTTPException(status_code=409, detail="Only assigned visits can be accepted")
    require_active_parent_consent(db, visit.parent_id)
    visit.status = "accepted"
    visit.updated_at = datetime.now(timezone.utc)
    db.add(AuditLog(user_id=current_user.id, action="accept_visit", entity_type="visit", entity_id=visit.id))
    db.commit()
    db.refresh(visit)
    return visit


@router.post("/visits/{visit_id}/reject", response_model=VisitResponse)
def reject_visit(
    visit_id: str,
    payload: VisitActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = get_assigned_visit(db, current_user, visit_id)
    if visit.status != "assigned":
        raise HTTPException(status_code=409, detail="Only assigned visits can be rejected")
    previous_companion_id = visit.companion_id
    visit.companion_id = None
    visit.assigned_by_user_id = None
    visit.assigned_at = None
    visit.rejection_reason = payload.reason
    visit.status = "requested"
    db.add(AuditLog(
        user_id=current_user.id,
        action="reject_visit",
        entity_type="visit",
        entity_id=visit.id,
        reason=payload.reason or previous_companion_id,
    ))
    db.commit()
    db.refresh(visit)
    return visit


@router.post("/visits/{visit_id}/check-in", response_model=VisitResponse)
def check_in(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = get_assigned_visit(db, current_user, visit_id)
    if visit.status != "accepted":
        raise HTTPException(status_code=409, detail="Only accepted visits can be checked in")
    require_active_parent_consent(db, visit.parent_id)
    visit.status = "in_progress"
    visit.checked_in_at = datetime.now(timezone.utc)
    db.add(AuditLog(user_id=current_user.id, action="check_in_visit", entity_type="visit", entity_id=visit.id))
    db.commit()
    db.refresh(visit)
    return visit


@router.post("/visits/{visit_id}/check-out", response_model=VisitResponse)
def check_out(
    visit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = get_assigned_visit(db, current_user, visit_id)
    if visit.status != "in_progress":
        raise HTTPException(status_code=409, detail="Only in-progress visits can be checked out")
    visit.status = "completed"
    visit.checked_out_at = datetime.now(timezone.utc)
    db.add(AuditLog(user_id=current_user.id, action="check_out_visit", entity_type="visit", entity_id=visit.id))
    db.commit()
    db.refresh(visit)
    return visit


@router.post("/visits/{visit_id}/cancel", response_model=VisitResponse)
def cancel_visit(
    visit_id: str,
    payload: VisitActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visit = get_family_visit(db, current_user, visit_id)
    if visit.status not in FAMILY_CANCELLABLE_STATUSES:
        raise HTTPException(status_code=409, detail="This visit can no longer be cancelled by the family")
    visit.status = "cancelled"
    visit.cancellation_reason = payload.reason
    db.add(AuditLog(
        user_id=current_user.id,
        action="cancel_visit",
        entity_type="visit",
        entity_id=visit.id,
        reason=payload.reason,
    ))
    db.commit()
    db.refresh(visit)
    return visit


@router.get("/admin/visits", response_model=list[VisitResponse])
def admin_visit_queue(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    query = db.query(Visit)
    if status_filter:
        if status_filter not in {
            "requested", "assigned", "accepted", "in_progress", "completed", "cancelled",
        }:
            raise HTTPException(status_code=400, detail="Invalid visit status")
        query = query.filter(Visit.status == status_filter)
    return query.order_by(Visit.scheduled_start).all()


@router.post("/admin/visits/{visit_id}/assign", response_model=VisitResponse)
def assign_companion(
    visit_id: str,
    payload: VisitAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if visit is None:
        raise HTTPException(status_code=404, detail="Visit not found")
    if visit.status != "requested":
        raise HTTPException(status_code=409, detail="Only requested visits can be assigned")
    require_active_parent_consent(db, visit.parent_id)

    companion = db.query(CompanionProfile).filter(
        CompanionProfile.id == payload.companion_id,
        CompanionProfile.identity_status == "verified",
        CompanionProfile.approval_status == "approved",
    ).first()
    if companion is None:
        raise HTTPException(status_code=409, detail="Companion must be verified and approved before assignment")
    try:
        local_start = as_utc(visit.scheduled_start).astimezone(ZoneInfo(companion.timezone_name))
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=409, detail="Companion profile has an invalid time zone")
    local_end = local_start + timedelta(minutes=visit.duration_minutes)
    availability = db.query(CompanionAvailability).filter(
        CompanionAvailability.companion_id == companion.id,
        CompanionAvailability.weekday == local_start.weekday(),
    ).first()
    if availability is None or not (
        availability.start_time <= local_start.time().replace(tzinfo=None)
        and availability.end_time >= local_end.time().replace(tzinfo=None)
        and local_start.date() == local_end.date()
    ):
        raise HTTPException(status_code=409, detail="Companion is not available for the requested time")

    new_start = as_utc(visit.scheduled_start)
    new_end = new_start + timedelta(minutes=visit.duration_minutes)
    existing_visits = db.query(Visit).filter(
        Visit.companion_id == companion.id,
        Visit.status.in_(ACTIVE_VISIT_STATUSES),
    ).all()
    for existing in existing_visits:
        existing_start = as_utc(existing.scheduled_start)
        existing_end = existing_start + timedelta(minutes=existing.duration_minutes)
        if new_start < existing_end and existing_start < new_end:
            raise HTTPException(status_code=409, detail="Companion already has an overlapping visit")

    visit.companion_id = companion.id
    visit.status = "assigned"
    visit.assigned_by_user_id = current_user.id
    visit.assigned_at = datetime.now(timezone.utc)
    visit.rejection_reason = None
    db.add(AuditLog(
        user_id=current_user.id,
        action="assign_companion",
        entity_type="visit",
        entity_id=visit.id,
    ))
    db.commit()
    db.refresh(visit)
    return visit


@router.post("/admin/parents/{parent_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def link_parent_identity(
    parent_id: str,
    payload: ParentLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    parent = db.query(ParentProfile).filter(ParentProfile.id == parent_id).first()
    linked_user = db.query(User).filter(User.id == payload.parent_user_id).first()
    if parent is None or linked_user is None:
        raise HTTPException(status_code=404, detail="Parent profile or platform user not found")
    if linked_user.account_type != "parent":
        raise HTTPException(status_code=409, detail="Only a parent account can be linked to a parent profile")
    if parent.parent_user_id and parent.parent_user_id != linked_user.id:
        raise HTTPException(status_code=409, detail="Parent profile is already linked to another platform user")
    parent.parent_user_id = linked_user.id
    db.add(AuditLog(
        user_id=current_user.id,
        action="link_parent_identity",
        entity_type="parent_profile",
        entity_id=parent.id,
    ))
    db.commit()
    return None
