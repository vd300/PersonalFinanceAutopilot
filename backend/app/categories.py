from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.models import Category, User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def categories_route(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.scalars(
        select(Category)
        .where((Category.user_id == current_user.id) | (Category.user_id.is_(None)))
        .order_by(Category.type, Category.name)
    ).all()
    return [
        {"id": category.id, "name": category.name, "type": category.type, "is_default": category.is_default}
        for category in categories
    ]

