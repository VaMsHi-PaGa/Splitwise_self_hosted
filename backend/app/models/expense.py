import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SplitType(str, enum.Enum):
    EQUAL = "equal"
    EXACT = "exact"
    PERCENT = "percent"


class ExpenseCategory(str, enum.Enum):
    GROCERIES = "groceries"
    RENT = "rent"
    ELECTRICITY = "electricity"
    WIFI = "wifi"
    MAID = "maid"
    COOK = "cook"
    PETROL = "petrol"
    TRAVEL = "travel"
    DINING = "dining"
    SUBSCRIPTIONS = "subscriptions"
    FESTIVAL = "festival"
    OFFICE_LUNCH = "office_lunch"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(Enum(ExpenseCategory), default=ExpenseCategory.OTHER)
    notes = Column(String(500))
    expense_date = Column(Date, default=date.today)
    split_type = Column(Enum(SplitType), default=SplitType.EQUAL)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    bill_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="expenses")
    payers = relationship("ExpensePayer", back_populates="expense", cascade="all, delete-orphan")
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Expense {self.description}>"


class ExpensePayer(Base):
    __tablename__ = "expense_payers"

    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    amount_paid = Column(Numeric(12, 2), nullable=False)

    expense = relationship("Expense", back_populates="payers")
    user = relationship("User")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    share_amount = Column(Numeric(12, 2), nullable=False)
    share_percent = Column(Numeric(5, 2))

    expense = relationship("Expense", back_populates="splits")
    user = relationship("User")
