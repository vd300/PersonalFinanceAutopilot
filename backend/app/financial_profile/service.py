from sqlalchemy import select
from sqlalchemy.orm import Session

from app.financial_profile.models import FinancialProfile
from app.financial_profile.schemas import FinancialProfileUpdate
from app.models import User
from app.shared.enums import FinancialMode


def get_or_create_financial_profile(db: Session, user: User) -> FinancialProfile:
    profile = db.scalar(select(FinancialProfile).where(FinancialProfile.user_id == user.id))
    if profile:
        return profile

    profile = FinancialProfile(
        user_id=user.id,
        financial_mode=FinancialMode.SALARIED.value,
        monthly_income_day=user.monthly_income_day,
        minimum_emergency_buffer=user.minimum_buffer_amount,
        savings_goal_amount=user.savings_goal_amount,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_financial_profile(
    db: Session,
    user: User,
    payload: FinancialProfileUpdate,
) -> FinancialProfile:
    profile = get_or_create_financial_profile(db, user)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value.value if isinstance(value, FinancialMode) else value)
    db.commit()
    db.refresh(profile)
    return profile
