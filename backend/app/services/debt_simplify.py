from decimal import Decimal
from typing import List, Dict, Tuple
from uuid import UUID

from app.services.balances import compute_group_balances


class Transaction:
    def __init__(self, from_user_id: UUID, to_user_id: UUID, amount: Decimal):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.amount = amount

    def __repr__(self):
        return f"Transaction({self.from_user_id} -> {self.to_user_id}: ₹{self.amount})"


def simplify_debts(balances: Dict[UUID, Decimal]) -> List[Transaction]:
    transactions = []

    while True:
        creditors = {uid: bal for uid, bal in balances.items() if bal > 0}
        debtors = {uid: bal for uid, bal in balances.items() if bal < 0}

        if not creditors or not debtors:
            break

        max_creditor = max(creditors, key=creditors.get)
        max_debtor = max(debtors, key=lambda x: -debtors[x])

        credit = creditors[max_creditor]
        debt = -debtors[max_debtor]

        amount = min(credit, debt)
        transactions.append(Transaction(max_debtor, max_creditor, amount))

        balances[max_creditor] -= amount
        balances[max_debtor] += amount

        if balances[max_creditor] == 0:
            del balances[max_creditor]
        if balances[max_debtor] == 0:
            del balances[max_debtor]

    return transactions
