from decimal import Decimal
from typing import Dict, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpensePayer, ExpenseSplit
from app.models.settlement import Settlement


def compute_group_balances(db: Session, group_id: UUID) -> Dict[UUID, Decimal]:
    balances = {}

    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    for expense in expenses:
        for payer in expense.payers:
            balances[payer.user_id] = balances.get(payer.user_id, Decimal("0")) + payer.amount_paid

        for split in expense.splits:
            balances[split.user_id] = balances.get(split.user_id, Decimal("0")) - split.share_amount

    settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
    for settlement in settlements:
        balances[settlement.from_user_id] = balances.get(settlement.from_user_id, Decimal("0")) - settlement.amount
        balances[settlement.to_user_id] = balances.get(settlement.to_user_id, Decimal("0")) + settlement.amount

    return {uid: bal for uid, bal in balances.items() if bal != Decimal("0")}


def compute_user_total_balance(db: Session, user_id: UUID) -> Tuple[Decimal, Decimal]:
    total_owed = Decimal("0")
    total_owing = Decimal("0")

    expenses = db.query(Expense).all()
    for expense in expenses:
        for payer in expense.payers:
            if payer.user_id == user_id:
                total_owed += payer.amount_paid

        for split in expense.splits:
            if split.user_id == user_id:
                total_owing += split.share_amount

    settlements = db.query(Settlement).all()
    for settlement in settlements:
        if settlement.from_user_id == user_id:
            total_owing += settlement.amount
        if settlement.to_user_id == user_id:
            total_owed += settlement.amount

    net_owed = total_owed - total_owing
    net_owing = total_owing - total_owed

    return (max(net_owed, Decimal("0")), max(net_owing, Decimal("0")))
