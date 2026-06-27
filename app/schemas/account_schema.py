from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=50)
    currency: str = Field(..., min_length=1, max_length=10)
    base_balance: Decimal = Field(default=Decimal("0.00"))


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    currency: str | None = None
    base_balance: Decimal | None = None
    is_active: bool | None = None


class AccountResponse(AccountBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    real_balance: Decimal = Decimal("0.00")
    projected_balance: Decimal = Decimal("0.00")

    class Config:
        from_attributes = True
