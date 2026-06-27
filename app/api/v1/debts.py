from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.debt_schema import DebtCreate, DebtUpdate, DebtResponse, DebtPaymentCreate, DebtPaymentResponse
from app.repositories.debt_repo import DebtRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[DebtResponse])
async def list_debts(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    debt_repo = DebtRepository(db)
    return await debt_repo.get_by_user(current_user.id)


@router.post("", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
async def create_debt(
    debt_in: DebtCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    debt = await finance_service.create_debt(current_user.id, debt_in.model_dump())
    return debt


@router.get("/{debt_id}", response_model=DebtResponse)
async def get_debt(
    debt_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    debt_repo = DebtRepository(db)
    debt = await debt_repo.get_by_user_and_id(current_user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
    return debt


@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: int,
    debt_in: DebtUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    debt_repo = DebtRepository(db)
    debt = await debt_repo.get_by_user_and_id(current_user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
        
    updated = await debt_repo.update(debt, debt_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated


@router.delete("/{debt_id}", response_model=DebtResponse)
async def delete_debt(
    debt_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    debt_repo = DebtRepository(db)
    debt = await debt_repo.get_by_user_and_id(current_user.id, debt_id)
    if not debt:
        raise HTTPException(status_code=404, detail="Deuda no encontrada")
        
    deleted = await debt_repo.remove(debt_id)
    await db.commit()
    return deleted


@router.post("/{debt_id}/pay", response_model=DebtPaymentResponse)
async def pay_debt_quota(
    debt_id: int,
    payment_in: DebtPaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    payment = await finance_service.pay_debt_installment(
        current_user.id,
        debt_id,
        payment_in.amount,
        payment_in.is_capital_amortization
    )
    return payment
