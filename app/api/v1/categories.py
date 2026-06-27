from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from app.repositories.category_repo import CategoryRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    category_repo = CategoryRepository(db)
    return await category_repo.get_by_user(current_user.id)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.create_category(current_user.id, category_in.model_dump())


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category_repo = CategoryRepository(db)
    cat = await category_repo.get_by_user_and_id(current_user.id, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category_repo = CategoryRepository(db)
    cat = await category_repo.get_by_user_and_id(current_user.id, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
    updated_cat = await category_repo.update(cat, category_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated_cat


@router.delete("/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    category_repo = CategoryRepository(db)
    cat = await category_repo.get_by_user_and_id(current_user.id, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
        
    deleted_cat = await category_repo.remove(category_id)
    await db.commit()
    return deleted_cat
