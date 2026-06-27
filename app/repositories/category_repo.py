from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.category_model import Category
from app.repositories.base_repo import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_user(self, user_id: int) -> list[Category]:
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: int, category_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.id == category_id,
                Category.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_type(self, user_id: int, name: str, cat_type: str) -> Category | None:
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.name.ilike(name),
                Category.type == cat_type,
                Category.is_active == True
            )
        )
        return result.scalar_one_or_none()
