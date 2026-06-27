from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.income_schema import IncomeCreate, IncomeUpdate, IncomeResponse
from app.repositories.income_repo import IncomeRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[IncomeResponse])
async def list_incomes(
    month: int | None = Query(None, ge=1, le=12),
    year: int | None = Query(None, ge=1900, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income_repo = IncomeRepository(db)
    return await income_repo.get_by_user(current_user.id, month, year)


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    income_in: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.create_income(current_user.id, income_in.model_dump())


@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income_repo = IncomeRepository(db)
    income = await income_repo.get_by_user_and_id(current_user.id, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
    return income


@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: int,
    income_in: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income_repo = IncomeRepository(db)
    income = await income_repo.get_by_user_and_id(current_user.id, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
        
    updated = await income_repo.update(income, income_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated


@router.delete("/{income_id}", response_model=IncomeResponse)
async def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    income_repo = IncomeRepository(db)
    income = await income_repo.get_by_user_and_id(current_user.id, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")
        
    deleted = await income_repo.remove(income_id)
    await db.commit()
    return deleted
si_income_checks = True
