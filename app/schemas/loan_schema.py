from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.account_schema import AccountResponse


class LoanBase(BaseModel):
    account_id: int | None = None
    debtor: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    date_granted: datetime
    due_date: datetime
    status: str = Field(default="Pendiente", pattern="^(Pendiente|Cobrado)$")
    is_installment_loan: bool = False
    interest_rate: Decimal = Field(default=Decimal("0.00"))
    total_installments: int = 0
    installments_paid: int = 0
    payment_day: int = Field(default=1, ge=1, le=31)


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    account_id: int | None = None
    debtor: str | None = None
    description: str | None = None
    amount: Decimal | None = None
    date_granted: datetime | None = None
    due_date: datetime | None = None
    status: str | None = None
    is_installment_loan: bool | None = None
    interest_rate: Decimal | None = None
    total_installments: int | None = None
    installments_paid: int | None = None
    payment_day: int | None = None
    is_active: bool | None = None


class LoanResponse(LoanBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    account: AccountResponse | None = None

    class Config:
        from_attributes = True


class LoanPaymentCollect(BaseModel):
    full_pay: bool = False
