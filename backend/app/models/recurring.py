import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum, Integer, Boolean, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class RecurringFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String(50), nullable=False)
    split_type = Column(String(20), default="equal")
    split_config = Column(JSON, nullable=False, default={})
    payer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    frequency = Column(Enum(RecurringFrequency), default=RecurringFrequency.MONTHLY)
    day_of_month = Column(Integer, default=1)
    day_of_week = Column(Integer)
    next_run_at = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RecurringExpense {self.description}>"
