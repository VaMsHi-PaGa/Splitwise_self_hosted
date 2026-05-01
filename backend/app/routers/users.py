from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.schemas import UserSearchResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search", response_model=list[UserSearchResponse])
def search_users(q: str = Query(min_length=1), db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    users = db.query(User).filter(
        (User.name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
    ).limit(20).all()
    return users
