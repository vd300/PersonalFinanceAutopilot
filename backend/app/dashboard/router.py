from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.dashboard.service import monthly_dashboard
from app.models import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_route(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return monthly_dashboard(db, current_user, month)

