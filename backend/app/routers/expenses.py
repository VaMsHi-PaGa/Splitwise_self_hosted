from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.models.expense import Expense, ExpensePayer, ExpenseSplit, SplitType
from app.schemas import ExpenseCreate, ExpenseResponse
from app.services.splitter import split_equal, split_exact, split_percent
from app.storage import save_bill_image, get_bill_path

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseResponse)
def create_expense(exp: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == exp.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if exp.split_type == "equal":
        user_ids = [s.user_id for s in exp.splits]
        splits_dict = split_equal(exp.amount, user_ids)
    elif exp.split_type == "exact":
        splits_dict = {s.user_id: s.amount for s in exp.splits if s.amount is not None}
        splits_dict = split_exact(exp.amount, splits_dict)
    elif exp.split_type == "percent":
        percents = {s.user_id: s.percent for s in exp.splits if s.percent is not None}
        splits_dict = split_percent(exp.amount, percents)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid split_type")

    expense = Expense(
        group_id=exp.group_id,
        description=exp.description,
        amount=exp.amount,
        category=exp.category,
        expense_date=exp.expense_date,
        notes=exp.notes,
        split_type=exp.split_type,
        created_by=current_user.id
    )
    db.add(expense)
    db.flush()

    for payer in exp.payers:
        db.add(ExpensePayer(expense_id=expense.id, user_id=payer.user_id, amount_paid=payer.amount_paid))

    for user_id, share in splits_dict.items():
        db.add(ExpenseSplit(expense_id=expense.id, user_id=user_id, share_amount=share))

    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    member = db.query(GroupMember).filter(
        GroupMember.group_id == expense.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return expense


@router.delete("/{expense_id}")
def delete_expense(expense_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if expense.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}


@router.post("/{expense_id}/bill")
def upload_bill(expense_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if expense.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    filename = save_bill_image(file)
    expense.bill_path = filename
    db.commit()
    return {"bill_path": filename}


@router.get("/uploads/{filename}")
def get_bill(filename: str):
    filepath = get_bill_path(filename)
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(filepath)
