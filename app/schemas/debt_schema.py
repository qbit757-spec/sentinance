from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.account_schema import AccountResponse


class DebtPaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    is_capital_amortization: bool = False


class DebtPaymentCreate(DebtPaymentBase):
    pass


class DebtPaymentResponse(DebtPaymentBase):
    id: int
    debt_id: int
    date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DebtBase(BaseModel):
    account_id: int
    name: str = Field(..., min_length=1, max_length=100)
    creditor: str = Field(..., min_length=1, max_length=100)
    original_amount: Decimal = Field(..., gt=Decimal("0.00"))
    pending_balance: Decimal = Field(..., ge=Decimal("0.00"))
    type: str = Field(default="Directa", pattern="^(Directa|En Cuotas)$")
    total_installments: int = 0
    paid_installments: int = 0
    interest_rate: Decimal = Field(default=Decimal("0.00"))
    amortizes_capital: bool = False
    next_due_date: datetime | None = None


class DebtCreate(DebtBase):
    pass


class DebtUpdate(BaseModel):
    account_id: int | None = None
    name: str | None = None
    creditor: str | None = None
    original_amount: Decimal | None = None
    pending_balance: Decimal | None = None
    type: str | None = None
    total_installments: int | None = None
    paid_installments: int | None = None
    interest_rate: Decimal | None = None
    amortizes_capital: bool | None = None
    next_due_date: datetime | None = None
    is_active: bool | None = None


class DebtResponse(DebtBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    account: AccountResponse | None = None
    payments: list[DebtPaymentResponse] = []

    class Config:
        from_attributes = True
