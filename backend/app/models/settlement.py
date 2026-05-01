import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SettlementMethod(str, enum.Enum):
    CASH = "cash"
    UPI = "upi"
    OTHER = "other"


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    method = Column(Enum(SettlementMethod), default=SettlementMethod.CASH)
    note = Column(String(500))
    settled_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Settlement {self.from_user_id} -> {self.to_user_id}>"
