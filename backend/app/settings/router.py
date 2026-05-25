from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import User
from app.settings.schemas import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _response(user: User) -> SettingsResponse:
    return SettingsResponse(
        preferred_currency=user.preferred_currency,
        monthly_income_day=user.monthly_income_day,
        savings_goal_amount=float(user.savings_goal_amount),
        minimum_buffer_amount=float(user.minimum_buffer_amount),
    )


@router.get("", response_model=SettingsResponse)
def get_route(current_user: User = Depends(get_current_user)):
    return _response(current_user)


@router.patch("", response_model=SettingsResponse)
def patch_route(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    return _response(current_user)

