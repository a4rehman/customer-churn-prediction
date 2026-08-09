from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserOut
from app.services.seed import pwd_context

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(user.username, user.role)
    return TokenResponse(
        access_token=token,
        username=user.username,
        role=user.role,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.get("/me", response_model=UserOut)
def me(current=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
