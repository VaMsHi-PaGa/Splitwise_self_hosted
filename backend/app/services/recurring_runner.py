from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta

from app.models.recurring import RecurringExpense, RecurringFrequency
from app.models.expense import Expense, ExpensePayer, ExpenseSplit, SplitType
from app.services.splitter import split_equal, split_exact, split_percent


def run_recurring_tasks(db: Session):
    now = datetime.utcnow()
    recurrences = db.query(RecurringExpense).filter(
        RecurringExpense.active == True,
        RecurringExpense.next_run_at <= now
    ).all()

    for rec in recurrences:
        create_expense_from_recurring(db, rec)
        advance_next_run(db, rec)


def create_expense_from_recurring(db: Session, rec: RecurringExpense):
    split_config = rec.split_config or {}

    if rec.split_type == "equal":
        user_ids = split_config.get("user_ids", [])
        splits_dict = split_equal(rec.amount, user_ids)
    elif rec.split_type == "exact":
        splits_dict = {k: Decimal(str(v)) for k, v in split_config.get("splits", {}).items()}
        splits_dict = {k: Decimal(str(v)) for k, v in splits_dict.items()}
    elif rec.split_type == "percent":
        percents = {k: Decimal(str(v)) for k, v in split_config.get("percents", {}).items()}
        splits_dict = split_percent(rec.amount, percents)
    else:
        return

    expense = Expense(
        group_id=rec.group_id,
        description=rec.description,
        amount=rec.amount,
        category=rec.category,
        expense_date=date.today(),
        split_type=rec.split_type,
        created_by=rec.created_by,
    )

    payer = ExpensePayer(
        user_id=rec.payer_user_id,
        amount_paid=rec.amount,
        expense=expense
    )

    for user_id, share_amount in splits_dict.items():
        split = ExpenseSplit(
            user_id=user_id,
            share_amount=share_amount,
            expense=expense
        )

    db.add(expense)
    db.add(payer)
    db.commit()


def advance_next_run(db: Session, rec: RecurringExpense):
    if rec.frequency == RecurringFrequency.MONTHLY:
        new_date = rec.next_run_at + relativedelta(months=1)
    elif rec.frequency == RecurringFrequency.WEEKLY:
        new_date = rec.next_run_at + timedelta(weeks=1)
    else:
        new_date = rec.next_run_at + timedelta(days=1)

    rec.next_run_at = new_date
    db.commit()
