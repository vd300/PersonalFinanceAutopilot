from sqlalchemy.orm import Session

from app.insights.overspending import detect_overspending
from app.insights.unusual_spending import detect_unusual_transactions
from app.subscriptions.detector import detect_subscriptions


def refresh_insights(db: Session, user_id: str) -> None:
    detect_subscriptions(db, user_id)
    detect_unusual_transactions(db, user_id)
    detect_overspending(db, user_id)

