from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.bills.schemas import BillCreate, BillResponse, BillUpdate
from app.core.database import get_db
from app.models import Bill, User

router = APIRouter(prefix="/bills", tags=["bills"])


def _response(bill: Bill) -> BillResponse:
    return BillResponse(
        id=bill.id,
        name=bill.name,
        expected_amount=float(bill.expected_amount),
        due_day=bill.due_day,
        next_due_date=bill.next_due_date.isoformat(),
        frequency=bill.frequency,
        is_auto_detected=bill.is_auto_detected,
        status=bill.status,
    )


@router.get("", response_model=list[BillResponse])
def list_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bills = db.scalars(select(Bill).where(Bill.user_id == current_user.id).order_by(Bill.next_due_date)).all()
    return [_response(bill) for bill in bills]


@router.post("", response_model=BillResponse)
def create_route(payload: BillCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = Bill(user_id=current_user.id, **payload.model_dump())
    db.add(bill)
    db.commit()
    return _response(bill)


@router.patch("/{bill_id}", response_model=BillResponse)
def patch_route(
    bill_id: str,
    payload: BillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bill = db.get(Bill, bill_id)
    if not bill or bill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bill, field, value)
    db.commit()
    return _response(bill)


@router.delete("/{bill_id}")
def delete_route(bill_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bill = db.get(Bill, bill_id)
    if not bill or bill.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    bill.status = "inactive"
    db.commit()
    return {"message": "Bill disabled"}

