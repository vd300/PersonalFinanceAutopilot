from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import Alert, User

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alerts = db.scalars(
        select(Alert).where(Alert.user_id == current_user.id).order_by(Alert.created_at.desc())
    ).all()
    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "title": alert.title,
            "message": alert.message,
            "severity": alert.severity,
            "status": alert.status,
            "created_at": alert.created_at.isoformat(),
        }
        for alert in alerts
    ]


@router.patch("/{alert_id}/dismiss")
def dismiss_route(alert_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.get(Alert, alert_id)
    if not alert or alert.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    alert.status = "dismissed"
    db.commit()
    return {"message": "Alert dismissed"}

