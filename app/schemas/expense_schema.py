from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.account_schema import AccountResponse
from app.schemas.category_schema import CategoryResponse


class ExpenseBase(BaseModel):
    account_id: int
    category_id: int
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    date: datetime
    status: str = Field(default="Pagado", pattern="^(Pagado|Por pagar)$")


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    description: str | None = None
    amount: Decimal | None = None
    date: datetime | None = None
    status: str | None = None
    is_active: bool | None = None


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    account: AccountResponse | None = None
    category: CategoryResponse | None = None

    class Config:
        from_attributes = True
