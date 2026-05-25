from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.auth.service import login, signup
from app.core.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup_route(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    _, token = signup(db, payload)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    _, token = login(db, payload)
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout_route() -> dict[str, str]:
    return {"message": "Client token cleared"}


@router.get("/me", response_model=UserResponse)
def me_route(current_user: User = Depends(get_current_user)) -> User:
    return current_user

