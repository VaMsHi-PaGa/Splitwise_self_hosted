from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    upi_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    id: UUID
    name: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GroupBase(BaseModel):
    name: str
    category: str = "other"


class GroupCreate(GroupBase):
    member_emails: Optional[List[str]] = []


class GroupMemberResponse(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        from_attributes = True


class GroupResponse(GroupBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    members: List[GroupMemberResponse]

    class Config:
        from_attributes = True


class ExpensePayerRequest(BaseModel):
    user_id: UUID
    amount_paid: Decimal


class ExpenseSplitRequest(BaseModel):
    user_id: UUID
    amount: Optional[Decimal] = None
    percent: Optional[Decimal] = None


class ExpenseCreate(BaseModel):
    group_id: UUID
    description: str
    amount: Decimal
    category: str = "other"
    expense_date: date = date.today()
    notes: Optional[str] = None
    split_type: str = "equal"
    payers: List[ExpensePayerRequest]
    splits: List[ExpenseSplitRequest]


class ExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    description: str
    amount: Decimal
    category: str
    expense_date: date
    notes: Optional[str]
    split_type: str
    bill_path: Optional[str]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    user_id: UUID
    user_name: str
    user_email: str
    balance: Decimal
    is_creditor: bool


class GroupBalanceResponse(BaseModel):
    group_id: UUID
    group_name: str
    balances: List[BalanceResponse]


class DashboardBalanceResponse(BaseModel):
    total_owed: Decimal
    total_owing: Decimal
    groups: List[GroupBalanceResponse]


class SettlementRequest(BaseModel):
    group_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    amount: Decimal
    method: str = "cash"
    note: Optional[str] = None


class SettlementResponse(BaseModel):
    id: UUID
    group_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    amount: Decimal
    method: str
    note: Optional[str]
    settled_at: datetime

    class Config:
        from_attributes = True


class SimplifyTransactionResponse(BaseModel):
    from_user_id: UUID
    from_user_name: str
    to_user_id: UUID
    to_user_name: str
    amount: Decimal


class RecurringExpenseCreate(BaseModel):
    group_id: UUID
    description: str
    amount: Decimal
    category: str
    split_type: str = "equal"
    split_config: dict
    payer_user_id: UUID
    frequency: str = "monthly"
    day_of_month: Optional[int] = 1
    day_of_week: Optional[int] = None


class RecurringExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    description: str
    amount: Decimal
    category: str
    split_type: str
    payer_user_id: UUID
    frequency: str
    day_of_month: Optional[int]
    next_run_at: datetime
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
