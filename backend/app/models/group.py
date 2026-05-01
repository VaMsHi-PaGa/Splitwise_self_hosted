import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Table, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class GroupCategory(str, enum.Enum):
    TRIP = "trip"
    FLATMATES = "flatmates"
    FAMILY = "family"
    OFFICE = "office"
    FRIENDS = "friends"
    OTHER = "other"


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    category = Column(Enum(GroupCategory), default=GroupCategory.OTHER)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group {self.name}>"


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)

    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="members")
    user = relationship("User")

    def __repr__(self):
        return f"<GroupMember {self.group_id} - {self.user_id}>"
