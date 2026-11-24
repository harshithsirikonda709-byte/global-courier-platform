from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import Family, FamilyMember, User
from ..schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email")

    if payload.phone:
        phone = payload.phone.strip()
        if db.query(User).filter(User.phone == phone).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this phone number")
    else:
        phone = None

    user = User(
        email=email,
        phone=phone,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        account_status="active",
    )
    db.add(user)
    db.flush()

    family = Family(
        primary_user_id=user.id,
        name=f"{payload.full_name.strip()} Family",
        account_status="active",
    )
    db.add(family)
    db.flush()

    membership = FamilyMember(
        family_id=family.id,
        user_id=user.id,
        role="owner",
        status="active",
    )
    db.add(membership)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        access_token=create_access_token(user),
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.account_status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive")

    return AuthResponse(
        access_token=create_access_token(user),
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
