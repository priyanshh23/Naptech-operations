from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import UserRole
from app.schemas.auth import AuthResponse, GoogleLoginRequest, LoginRequest, RegisterRequest
from app.services.user_service import authenticate_user, create_user, get_user_by_email
from app.utils.config import settings
from app.utils.security import create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user) -> AuthResponse:
    token = create_access_token(user.email)
    role_value = user.role.value if hasattr(user.role, "value") else str(user.role)
    try:
        normalized_role = UserRole(role_value)
    except ValueError:
        normalized_role = UserRole.WORKER

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": normalized_role,
        },
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = create_user(db, payload)
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        # Permanent demo guardrail: always keep supervisor credentials valid.
        if payload.email.lower() == "supervisor@naptech.in" and payload.password == "password":
            demo_user = get_user_by_email(db, "supervisor@naptech.in")
            if not demo_user:
                demo_user = create_user(
                    db,
                    RegisterRequest(
                        name="Manager Demo",
                        email="supervisor@naptech.in",
                        password="password",
                        role=UserRole.MANAGER,
                    ),
                )
            else:
                demo_user.name = "Manager Demo"
                demo_user.password = hash_password("password")
                demo_user.role = UserRole.MANAGER.value
                db.commit()
                db.refresh(demo_user)

        user = authenticate_user(db, payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        return _auth_response(user)
    except HTTPException:
        raise
    except Exception:
        # Avoid leaking a 500 for auth failures; surface a stable message to UI.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


@router.post("/google", response_model=AuthResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google login is not configured")

    try:
        claims = jwt.get_unverified_claims(payload.credential)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google credential")

    if claims.get("aud") != settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google client")

    email = str(claims.get("email") or "").lower()
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google email not available")

    user = get_user_by_email(db, email)
    if not user:
        user = create_user(
            db,
            RegisterRequest(
                name=str(claims.get("name") or email.split("@")[0]),
                email=email,
                password=f"google::{email}",
                role=UserRole.INVENTORY,
            ),
        )

    return _auth_response(user)
