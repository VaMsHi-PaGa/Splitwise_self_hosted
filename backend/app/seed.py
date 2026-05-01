from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.group import Group, GroupMember, GroupCategory
from app.models.expense import Expense, ExpensePayer, ExpenseSplit, ExpenseCategory
from app.security import hash_password
from app.database import table_exists


def seed_demo_data(db: Session):
    if not table_exists("users"):
        return

    if db.query(User).filter(User.email == "aarav@example.com").first():
        return

    aarav = User(
        name="Aarav Singh",
        email="aarav@example.com",
        phone="9876543210",
        password_hash=hash_password("password123")
    )
    priya = User(
        name="Priya Sharma",
        email="priya@example.com",
        phone="9876543211",
        password_hash=hash_password("password123")
    )
    db.add(aarav)
    db.add(priya)
    db.flush()

    group = Group(
        name="Flatmates",
        category=GroupCategory.FLATMATES,
        created_by=aarav.id
    )
    db.add(group)
    db.flush()

    db.add(GroupMember(group_id=group.id, user_id=aarav.id))
    db.add(GroupMember(group_id=group.id, user_id=priya.id))

    expense1 = Expense(
        group_id=group.id,
        description="Groceries",
        amount=Decimal("1200.00"),
        category=ExpenseCategory.GROCERIES,
        expense_date=date.today(),
        split_type="equal",
        created_by=aarav.id
    )
    db.add(expense1)
    db.flush()

    db.add(ExpensePayer(expense_id=expense1.id, user_id=aarav.id, amount_paid=Decimal("1200.00")))
    db.add(ExpenseSplit(expense_id=expense1.id, user_id=aarav.id, share_amount=Decimal("600.00")))
    db.add(ExpenseSplit(expense_id=expense1.id, user_id=priya.id, share_amount=Decimal("600.00")))

    expense2 = Expense(
        group_id=group.id,
        description="Electricity Bill",
        amount=Decimal("2400.00"),
        category=ExpenseCategory.ELECTRICITY,
        expense_date=date.today(),
        split_type="equal",
        created_by=priya.id
    )
    db.add(expense2)
    db.flush()

    db.add(ExpensePayer(expense_id=expense2.id, user_id=priya.id, amount_paid=Decimal("2400.00")))
    db.add(ExpenseSplit(expense_id=expense2.id, user_id=aarav.id, share_amount=Decimal("1200.00")))
    db.add(ExpenseSplit(expense_id=expense2.id, user_id=priya.id, share_amount=Decimal("1200.00")))

    db.commit()
