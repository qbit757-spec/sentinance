from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.account_schema import AccountResponse
from app.schemas.category_schema import CategoryResponse


class IncomeBase(BaseModel):
    account_id: int
    category_id: int
    goal_id: int | None = None
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    date: datetime
    status: str = Field(default="Liquidado", pattern="^(Liquidado|Por liquidar)$")


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    goal_id: int | None = None
    description: str | None = None
    amount: Decimal | None = None
    date: datetime | None = None
    status: str | None = None
    is_active: bool | None = None


class IncomeResponse(IncomeBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    account: AccountResponse | None = None
    category: CategoryResponse | None = None

    class Config:
        from_attributes = True
