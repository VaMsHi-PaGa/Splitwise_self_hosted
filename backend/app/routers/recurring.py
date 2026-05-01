from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.models.recurring import RecurringExpense, RecurringFrequency
from app.schemas import RecurringExpenseCreate, RecurringExpenseResponse
from app.services.recurring_runner import run_recurring_tasks

router = APIRouter(prefix="/recurring", tags=["recurring"])


@router.get("/groups/{group_id}", response_model=list[RecurringExpenseResponse])
def list_recurring(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    recurrences = db.query(RecurringExpense).filter(RecurringExpense.group_id == group_id).all()
    return recurrences


@router.post("", response_model=RecurringExpenseResponse)
def create_recurring(rec: RecurringExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == rec.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    next_run = datetime.utcnow() + timedelta(hours=1)

    db_rec = RecurringExpense(
        group_id=rec.group_id,
        description=rec.description,
        amount=rec.amount,
        category=rec.category,
        split_type=rec.split_type,
        split_config=rec.split_config,
        payer_user_id=rec.payer_user_id,
        frequency=rec.frequency,
        day_of_month=rec.day_of_month,
        day_of_week=rec.day_of_week,
        next_run_at=next_run,
        active=True,
        created_by=current_user.id
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec


@router.patch("/{rec_id}", response_model=RecurringExpenseResponse)
def update_recurring(rec_id: UUID, rec: RecurringExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_rec = db.query(RecurringExpense).filter(RecurringExpense.id == rec_id).first()
    if not db_rec or db_rec.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_rec.description = rec.description
    db_rec.amount = rec.amount
    db_rec.category = rec.category
    db_rec.split_type = rec.split_type
    db_rec.split_config = rec.split_config
    db_rec.frequency = rec.frequency
    db_rec.day_of_month = rec.day_of_month
    db_rec.day_of_week = rec.day_of_week

    db.commit()
    db.refresh(db_rec)
    return db_rec


@router.delete("/{rec_id}")
def delete_recurring(rec_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_rec = db.query(RecurringExpense).filter(RecurringExpense.id == rec_id).first()
    if not db_rec or db_rec.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(db_rec)
    db.commit()
    return {"message": "Recurring expense deleted"}


@router.post("/{rec_id}/run")
def run_recurring(rec_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_rec = db.query(RecurringExpense).filter(RecurringExpense.id == rec_id).first()
    if not db_rec or db_rec.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    run_recurring_tasks(db)
    return {"message": "Recurring task executed"}
