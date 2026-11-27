from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_family_member
from ..database import get_db
from ..models import (
    AuditLog,
    EmergencyContact,
    FamilyParent,
    ParentAuthorization,
    ParentConsent,
    ParentProfile,
    Visit,
)
from ..models import User
from ..schemas import (
    ConsentCreateRequest,
    ConsentResponse,
    ParentCreateRequest,
    ParentResponse,
    ParentUpdateRequest,
    WithdrawalRequest,
)


router = APIRouter(prefix="/api/v1/carecircle/parents", tags=["parent profiles"])


def require_parent_access(db: Session, current_user: User, parent_id: str) -> ParentProfile:
    parent = db.query(ParentProfile).filter(ParentProfile.id == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found")
    if parent.status != "active":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found")
    if parent.parent_user_id == current_user.id:
        return parent

    membership = require_family_member(db, current_user)
    parent_link = (
        db.query(FamilyParent)
        .join(ParentAuthorization, ParentAuthorization.family_member_id == membership.id)
        .filter(
            FamilyParent.family_id == membership.family_id,
            FamilyParent.parent_id == parent_id,
            FamilyParent.status == "active",
            ParentAuthorization.parent_id == parent_id,
            ParentAuthorization.status == "active",
        )
        .first()
    )
    if parent_link is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this parent")
    return parent


def audit(db: Session, user_id: str, action: str, entity_type: str, entity_id: str, reason: str = None):
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        reason=reason,
    ))


@router.get("", response_model=list[ParentResponse])
def list_parents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = require_family_member(db, current_user)
    parents = (
        db.query(ParentProfile)
        .join(FamilyParent, FamilyParent.parent_id == ParentProfile.id)
        .join(
            ParentAuthorization,
            (ParentAuthorization.parent_id == ParentProfile.id)
            & (ParentAuthorization.family_member_id == membership.id),
        )
        .filter(
            FamilyParent.family_id == membership.family_id,
            FamilyParent.status == "active",
            ParentAuthorization.status == "active",
            ParentProfile.status == "active",
        )
        .all()
    )
    return parents


@router.post("", response_model=ParentResponse, status_code=status.HTTP_201_CREATED)
def create_parent(
    payload: ParentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = require_family_member(db, current_user)

    parent = ParentProfile(
        full_name=payload.full_name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        phone=payload.phone,
        alternate_phone=payload.alternate_phone,
        address_line1=payload.address_line1,
        address_line2=payload.address_line2,
        city=payload.city,
        state=payload.state,
        postal_code=payload.postal_code,
        country=payload.country,
        address_instructions=payload.address_instructions,
        preferred_language=payload.preferred_language,
        interests=payload.interests,
        accessibility_preferences=payload.accessibility_preferences,
        status="active",
    )
    db.add(parent)
    db.flush()

    family_parent = FamilyParent(
        family_id=membership.family_id,
        parent_id=parent.id,
        relationship_type=payload.relationship,
        status="active",
    )
    db.add(family_parent)

    authorization = ParentAuthorization(
        parent_id=parent.id,
        family_member_id=membership.id,
        role="owner",
        can_edit_profile=True,
        can_manage_consent=True,
        can_view_visits=True,
        status="active",
    )
    db.add(authorization)

    for index, contact in enumerate(payload.emergency_contacts):
        db.add(EmergencyContact(
            parent_id=parent.id,
            full_name=contact.full_name,
            relationship_type=contact.relationship,
            phone=contact.phone,
            alternate_phone=contact.alternate_phone,
            is_primary=contact.is_primary if index > 0 or contact.is_primary else True,
            status="active",
        ))

    audit(db, current_user.id, "create", "parent_profile", parent.id)
    db.commit()
    db.refresh(parent)
    return parent


@router.get("/me", response_model=ParentResponse)
def get_my_parent_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = db.query(ParentProfile).filter(
        ParentProfile.parent_user_id == current_user.id,
        ParentProfile.status == "active",
    ).first()
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No parent profile is linked to this account")
    return parent


@router.get("/{parent_id}", response_model=ParentResponse)
def get_parent(
    parent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return require_parent_access(db, current_user, parent_id)


@router.put("/{parent_id}", response_model=ParentResponse)
def update_parent(
    parent_id: str,
    payload: ParentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = require_parent_access(db, current_user, parent_id)
    if parent.parent_user_id != current_user.id:
        membership = require_family_member(db, current_user)
        authorization = (
            db.query(ParentAuthorization)
            .filter(
                ParentAuthorization.parent_id == parent_id,
                ParentAuthorization.family_member_id == membership.id,
                ParentAuthorization.status == "active",
            )
            .first()
        )
        if authorization is None or not authorization.can_edit_profile:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Profile editing is not authorized")

    for field_name in payload.model_fields_set:
        if field_name != "emergency_contacts" and hasattr(parent, field_name):
            if (
                parent.parent_user_id
                and parent.parent_user_id != current_user.id
                and field_name in {"preferred_language", "interests", "accessibility_preferences"}
                and getattr(parent, field_name) != getattr(payload, field_name)
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the parent can change personal preferences",
                )
            setattr(parent, field_name, getattr(payload, field_name))

    db.query(EmergencyContact).filter(
        EmergencyContact.parent_id == parent_id,
        EmergencyContact.status == "active",
    ).update({"status": "inactive"}, synchronize_session=False)

    for index, contact in enumerate(payload.emergency_contacts):
        db.add(EmergencyContact(
            parent_id=parent_id,
            full_name=contact.full_name,
            relationship_type=contact.relationship,
            phone=contact.phone,
            alternate_phone=contact.alternate_phone,
            is_primary=contact.is_primary if index > 0 or contact.is_primary else True,
            status="active",
        ))

    audit(db, current_user.id, "update", "parent_profile", parent.id)
    db.commit()
    db.refresh(parent)
    return parent


@router.post("/{parent_id}/consents", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
def record_consent(
    parent_id: str,
    payload: ConsentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = db.query(ParentProfile).filter(ParentProfile.id == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found")

    is_parent = parent.parent_user_id == current_user.id
    if is_parent:
        consent_source = "parent"
        signer_relationship = None
    else:
        parent = require_parent_access(db, current_user, parent_id)
        membership = require_family_member(db, current_user)
        authorization = (
            db.query(ParentAuthorization)
            .filter(
                ParentAuthorization.parent_id == parent_id,
                ParentAuthorization.family_member_id == membership.id,
                ParentAuthorization.status == "active",
            )
            .first()
        )
        if authorization is None or not authorization.can_manage_consent:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent management is not authorized")
        consent_source = "family_reported"
        family_link = db.query(FamilyParent).filter(
            FamilyParent.parent_id == parent_id,
            FamilyParent.family_id == membership.family_id,
            FamilyParent.status == "active",
        ).first()
        signer_relationship = family_link.relationship_type if family_link else None

    consent = ParentConsent(
        parent_id=parent.id,
        status="active" if is_parent else "family_reported",
        consent_source=consent_source,
        scope=payload.scope,
        consent_text=payload.consent_text,
        signed_by_user_id=current_user.id,
        signer_relationship=signer_relationship,
        effective_at=datetime.now(timezone.utc) if is_parent else None,
        expires_at=payload.expires_at,
    )
    if is_parent:
        active_consents = db.query(ParentConsent).filter(
            ParentConsent.parent_id == parent.id,
            ParentConsent.status == "active",
            ParentConsent.consent_source == "parent",
        ).all()
        for active_consent in active_consents:
            active_consent.status = "superseded"

    db.add(consent)
    db.flush()
    audit(db, current_user.id, "record_consent", "parent_consent", consent.id)
    db.commit()
    db.refresh(consent)
    return consent


@router.post("/{parent_id}/consents/{consent_id}/withdraw", response_model=ConsentResponse)
def withdraw_consent(
    parent_id: str,
    consent_id: str,
    payload: WithdrawalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parent = db.query(ParentProfile).filter(ParentProfile.id == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent profile not found")

    is_parent = parent.parent_user_id == current_user.id
    if not is_parent:
        require_parent_access(db, current_user, parent_id)
        membership = require_family_member(db, current_user)
        authorization = (
            db.query(ParentAuthorization)
            .filter(
                ParentAuthorization.parent_id == parent_id,
                ParentAuthorization.family_member_id == membership.id,
                ParentAuthorization.status == "active",
            )
            .first()
        )
        if authorization is None or not authorization.can_manage_consent:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Consent management is not authorized")

    consent = db.query(ParentConsent).filter(
        ParentConsent.id == consent_id,
        ParentConsent.parent_id == parent.id,
    ).first()
    if consent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent record not found")
    if consent.consent_source == "parent" and not is_parent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the parent can withdraw personal consent")
    if consent.status not in ("active", "family_reported"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only current consent records can be withdrawn")

    consent.status = "withdrawn"
    consent.withdrawn_at = datetime.now(timezone.utc)
    consent.withdrawn_by_user_id = current_user.id
    consent.withdrawal_reason = payload.reason

    if is_parent and consent.consent_source == "parent":
        scheduled_visits = db.query(Visit).filter(
            Visit.parent_id == parent.id,
            Visit.status.in_(("requested", "assigned", "accepted")),
        ).all()
        for visit in scheduled_visits:
            visit.status = "cancelled"
            visit.cancellation_reason = "Parent withdrew personal consent"
            audit(db, current_user.id, "cancel_visit_after_consent_withdrawal", "visit", visit.id)

    audit(
        db,
        current_user.id,
        "withdraw_consent",
        "parent_consent",
        consent.id,
        payload.reason,
    )
    db.commit()
    db.refresh(consent)
    return consent
