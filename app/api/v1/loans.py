from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanUpdate, LoanResponse, LoanPaymentCollect
from app.repositories.loan_repo import LoanRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[LoanResponse])
async def list_loans(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    loan_repo = LoanRepository(db)
    return await loan_repo.get_by_user(current_user.id)


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_in: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.create_loan(current_user.id, loan_in.model_dump())


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    loan_repo = LoanRepository(db)
    loan = await loan_repo.get_by_user_and_id(current_user.id, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan


@router.put("/{loan_id}", response_model=LoanResponse)
async def update_loan(
    loan_id: int,
    loan_in: LoanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    loan_repo = LoanRepository(db)
    loan = await loan_repo.get_by_user_and_id(current_user.id, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        
    updated = await loan_repo.update(loan, loan_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated


@router.delete("/{loan_id}", response_model=LoanResponse)
async def delete_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    loan_repo = LoanRepository(db)
    loan = await loan_repo.get_by_user_and_id(current_user.id, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        
    deleted = await loan_repo.remove(loan_id)
    await db.commit()
    return deleted


@router.post("/{loan_id}/collect", response_model=LoanResponse)
async def collect_loan(
    loan_id: int,
    payload: LoanPaymentCollect,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.pay_loan(current_user.id, loan_id, payload.full_pay)
si_loans_collect_test = True
