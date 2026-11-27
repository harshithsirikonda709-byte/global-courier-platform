from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin, require_companion
from ..database import get_db
from ..models import AuditLog, CompanionAvailability, CompanionProfile, User
from ..schemas import (
    AvailabilityResponse,
    AvailabilityUpdateRequest,
    CompanionAdminResponse,
    CompanionProfileInput,
    CompanionProfileResponse,
    CompanionReviewRequest,
)


router = APIRouter(prefix="/api/v1/carecircle", tags=["companions"])
admin_router = APIRouter(prefix="/api/v1/carecircle/admin", tags=["companion administration"])


def get_companion_profile(db: Session, user: User) -> CompanionProfile:
    require_companion(user)
    profile = db.query(CompanionProfile).filter(CompanionProfile.user_id == user.id).first()
    if profile is None:
        profile = CompanionProfile(
            user_id=user.id,
            display_name=user.full_name,
            bio="",
            languages=[],
            service_area="",
            timezone_name="Asia/Kolkata",
            identity_document_type="",
            identity_status="pending",
            approval_status="pending",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/companions/me", response_model=CompanionProfileResponse)
def companion_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_companion_profile(db, current_user)


@router.put("/companions/me", response_model=CompanionProfileResponse)
def update_companion_profile(
    payload: CompanionProfileInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_companion_profile(db, current_user)
    for field_name, value in payload.model_dump().items():
        setattr(profile, field_name, value)
    profile.updated_at = datetime.now(timezone.utc)
    db.add(AuditLog(
        user_id=current_user.id,
        action="update_companion_profile",
        entity_type="companion_profile",
        entity_id=profile.id,
    ))
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/companions/me/availability", response_model=list[AvailabilityResponse])
def get_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_companion_profile(db, current_user)
    return db.query(CompanionAvailability).filter(
        CompanionAvailability.companion_id == profile.id,
    ).order_by(CompanionAvailability.weekday).all()


@router.put("/companions/me/availability", response_model=list[AvailabilityResponse])
def update_availability(
    payload: AvailabilityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = get_companion_profile(db, current_user)
    db.query(CompanionAvailability).filter(
        CompanionAvailability.companion_id == profile.id,
    ).delete(synchronize_session=False)
    availability = [
        CompanionAvailability(
            companion_id=profile.id,
            weekday=item.weekday,
            start_time=item.start_time,
            end_time=item.end_time,
        )
        for item in payload.availability
    ]
    db.add_all(availability)
    db.add(AuditLog(
        user_id=current_user.id,
        action="update_companion_availability",
        entity_type="companion_profile",
        entity_id=profile.id,
    ))
    db.commit()
    return db.query(CompanionAvailability).filter(
        CompanionAvailability.companion_id == profile.id,
    ).order_by(CompanionAvailability.weekday).all()


@admin_router.get("/companions", response_model=list[CompanionAdminResponse])
def list_companions(
    approval_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    query = db.query(CompanionProfile).join(User, User.id == CompanionProfile.user_id)
    if approval_status:
        if approval_status not in {"pending", "approved", "rejected", "suspended"}:
            raise HTTPException(status_code=400, detail="Invalid approval status")
        query = query.filter(CompanionProfile.approval_status == approval_status)
    profiles = query.order_by(CompanionProfile.created_at).all()
    return [
        CompanionAdminResponse(
            **CompanionProfileResponse.model_validate(profile).model_dump(),
            user_id=profile.user_id,
            email=profile.user.email,
            phone=profile.user.phone,
        )
        for profile in profiles
    ]


@admin_router.post("/companions/{companion_id}/review", response_model=CompanionAdminResponse)
def review_companion(
    companion_id: str,
    payload: CompanionReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    profile = db.query(CompanionProfile).filter(CompanionProfile.id == companion_id).first()
    if profile is None:
        raise HTTPException(status_code=404, detail="Companion profile not found")
    if not (
        profile.display_name.strip()
        and len(profile.bio.strip()) >= 20
        and profile.languages
        and profile.service_area.strip()
        and profile.identity_document_type.strip()
    ):
        raise HTTPException(status_code=409, detail="Complete the companion profile before identity review")

    if payload.action == "verify_identity":
        if profile.identity_status != "pending":
            raise HTTPException(status_code=409, detail="Identity is not pending review")
        profile.identity_status = "verified"
    elif payload.action == "reject_identity":
        if profile.identity_status != "pending":
            raise HTTPException(status_code=409, detail="Identity is not pending review")
        profile.identity_status = "rejected"
        profile.approval_status = "rejected"
    elif payload.action == "approve":
        if profile.identity_status != "verified":
            raise HTTPException(status_code=409, detail="Verify companion identity before approval")
        if profile.approval_status != "pending":
            raise HTTPException(status_code=409, detail="Companion is not pending approval")
        profile.approval_status = "approved"
    else:
        if profile.approval_status != "pending":
            raise HTTPException(status_code=409, detail="Companion is not pending approval")
        profile.approval_status = "rejected"

    profile.admin_notes = payload.notes
    profile.reviewed_by_user_id = current_user.id
    profile.reviewed_at = datetime.now(timezone.utc)
    db.add(AuditLog(
        user_id=current_user.id,
        action=f"companion_{payload.action}",
        entity_type="companion_profile",
        entity_id=profile.id,
        reason=payload.notes,
    ))
    db.commit()
    db.refresh(profile)
    return CompanionAdminResponse(
        **CompanionProfileResponse.model_validate(profile).model_dump(),
        user_id=profile.user_id,
        email=profile.user.email,
        phone=profile.user.phone,
    )
