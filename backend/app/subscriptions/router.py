from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import Subscription, User
from app.subscriptions.detector import detect_subscriptions
from app.subscriptions.schemas import SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


def _response(subscription: Subscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=subscription.id,
        merchant_name=subscription.merchant_name,
        amount=float(subscription.amount),
        frequency=subscription.frequency,
        last_payment_date=subscription.last_payment_date.isoformat(),
        next_expected_payment_date=subscription.next_expected_payment_date.isoformat(),
        status=subscription.status,
        confidence_score=subscription.confidence_score,
    )


@router.get("", response_model=list[SubscriptionResponse])
def list_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscriptions = db.scalars(
        select(Subscription).where(Subscription.user_id == current_user.id).order_by(Subscription.next_expected_payment_date)
    ).all()
    return [_response(item) for item in subscriptions]


@router.post("", response_model=SubscriptionResponse)
def create_route(
    payload: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = Subscription(user_id=current_user.id, source_type="manual", confidence_score=100, **payload.model_dump())
    db.add(subscription)
    db.commit()
    return _response(subscription)


@router.patch("/{subscription_id}", response_model=SubscriptionResponse)
def patch_route(
    subscription_id: str,
    payload: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = db.get(Subscription, subscription_id)
    if not subscription or subscription.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(subscription, field, value)
    db.commit()
    return _response(subscription)


@router.post("/detect")
def detect_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    detect_subscriptions(db, current_user.id)
    db.commit()
    return {"message": "Subscription detection refreshed"}

