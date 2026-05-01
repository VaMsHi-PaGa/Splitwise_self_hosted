from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import Group, GroupMember
from app.schemas import GroupCreate, GroupResponse, BalanceResponse, GroupBalanceResponse
from app.services.balances import compute_group_balances

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupResponse])
def list_groups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    groups = db.query(Group).join(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    return groups


@router.post("", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_group = Group(name=group.name, category=group.category, created_by=current_user.id)
    db.add(db_group)
    db.flush()

    member = GroupMember(group_id=db_group.id, user_id=current_user.id)
    db.add(member)

    for email in (group.member_emails or []):
        user = db.query(User).filter(User.email == email).first()
        if user and not db.query(GroupMember).filter(GroupMember.group_id == db_group.id, GroupMember.user_id == user.id).first():
            db.add(GroupMember(group_id=db_group.id, user_id=user.id))

    db.commit()
    db.refresh(db_group)
    return db_group


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return group


@router.post("/{group_id}/members")
def add_member(group_id: UUID, email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already a member")

    db.add(GroupMember(group_id=group_id, user_id=user.id))
    db.commit()
    return {"message": "Member added"}


@router.delete("/{group_id}/members/{user_id}")
def remove_member(group_id: UUID, user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db.delete(member)
    db.commit()
    return {"message": "Member removed"}


@router.get("/{group_id}/balances", response_model=GroupBalanceResponse)
def get_group_balances(group_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    member = db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    balances_dict = compute_group_balances(db, group_id)
    group_members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    balances = []
    for gm in group_members:
        balance = balances_dict.get(gm.user_id, 0)
        balances.append(BalanceResponse(
            user_id=gm.user_id,
            user_name=gm.user.name,
            user_email=gm.user.email,
            balance=balance,
            is_creditor=balance > 0
        ))

    return GroupBalanceResponse(group_id=group_id, group_name=group.name, balances=balances)
