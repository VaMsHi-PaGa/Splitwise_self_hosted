from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.group import GroupMember
from app.schemas import DashboardBalanceResponse, GroupBalanceResponse, BalanceResponse
from app.services.balances import compute_user_total_balance, compute_group_balances

router = APIRouter(prefix="/balances", tags=["balances"])


@router.get("", response_model=DashboardBalanceResponse)
def get_dashboard_balances(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_owed, total_owing = compute_user_total_balance(db, current_user.id)

    user_groups = db.query(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    groups_data = []

    for gm in user_groups:
        group = gm.group
        balances_dict = compute_group_balances(db, group.id)
        group_members = db.query(GroupMember).filter(GroupMember.group_id == group.id).all()

        balances = []
        for member in group_members:
            balance = balances_dict.get(member.user_id, 0)
            balances.append(BalanceResponse(
                user_id=member.user_id,
                user_name=member.user.name,
                user_email=member.user.email,
                balance=balance,
                is_creditor=balance > 0
            ))

        groups_data.append(GroupBalanceResponse(
            group_id=group.id,
            group_name=group.name,
            balances=balances
        ))

    return DashboardBalanceResponse(
        total_owed=total_owed,
        total_owing=total_owing,
        groups=groups_data
    )
