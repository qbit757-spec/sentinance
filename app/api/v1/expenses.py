from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.repositories.expense_repo import ExpenseRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[ExpenseResponse])
async def list_expenses(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=1900, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense_repo = ExpenseRepository(db)
    return await expense_repo.get_by_user(current_user.id, month, year)


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_in: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.create_expense(current_user.id, expense_in.model_dump())


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense_repo = ExpenseRepository(db)
    expense = await expense_repo.get_by_user_and_id(current_user.id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense_repo = ExpenseRepository(db)
    expense = await expense_repo.get_by_user_and_id(current_user.id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
        
    updated = await expense_repo.update(expense, expense_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated


@router.delete("/{expense_id}", response_model=ExpenseResponse)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    expense_repo = ExpenseRepository(db)
    expense = await expense_repo.get_by_user_and_id(current_user.id, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
        
    deleted = await expense_repo.remove(expense_id)
    await db.commit()
    return deleted
