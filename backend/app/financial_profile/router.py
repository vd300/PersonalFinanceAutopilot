from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.financial_profile.schemas import FinancialProfileResponse, FinancialProfileUpdate
from app.financial_profile.service import get_or_create_financial_profile, update_financial_profile
from app.models import User

router = APIRouter(prefix="/financial-profile", tags=["financial-profile"])


@router.get("", response_model=FinancialProfileResponse)
def get_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_or_create_financial_profile(db, current_user)


@router.patch("", response_model=FinancialProfileResponse)
def patch_route(
    payload: FinancialProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_financial_profile(db, current_user, payload)
