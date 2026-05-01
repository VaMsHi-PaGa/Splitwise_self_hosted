from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.models.settlement import Settlement
from app.models.expense import Expense
from app.schemas import SettlementRequest, SettlementResponse, SimplifyTransactionResponse
from app.services.balances import compute_group_balances
from app.services.debt_simplify import simplify_debts
from copy import deepcopy

router = APIRouter(tags=["settlements"])


@router.post("/settle", response_model=SettlementResponse)
def create_settlement(settle: SettlementRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(GroupMember).filter(
        GroupMember.group_id == settle.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    settlement = Settlement(
        group_id=settle.group_id,
        from_user_id=settle.from_user_id,
        to_user_id=settle.to_user_id,
        amount=settle.amount,
        method=settle.method,
        note=settle.note
    )
    db.add(settlement)
    db.commit()
    db.refresh(settlement)
    return settlement


@router.get("/groups/{group_id}/settlements", response_model=list[SettlementResponse])
def get_group_settlements(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
    return settlements


@router.get("/groups/{group_id}/simplify", response_model=list[SimplifyTransactionResponse])
def simplify_group_debts(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    balances = compute_group_balances(db, group_id)
    balances_copy = deepcopy(balances)

    transactions = simplify_debts(balances_copy)

    result = []
    for tx in transactions:
        from_user = db.query(User).filter(User.id == tx.from_user_id).first()
        to_user = db.query(User).filter(User.id == tx.to_user_id).first()
        result.append(SimplifyTransactionResponse(
            from_user_id=tx.from_user_id,
            from_user_name=from_user.name if from_user else "Unknown",
            to_user_id=tx.to_user_id,
            to_user_name=to_user.name if to_user else "Unknown",
            amount=tx.amount
        ))

    return result
