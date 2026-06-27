from sqlalchemy import select, extract, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.income_model import Income
from app.repositories.base_repo import BaseRepository


class IncomeRepository(BaseRepository[Income]):
    def __init__(self, db: AsyncSession):
        super().__init__(Income, db)

    async def get_by_user(
        self, user_id: int, month: int | None = None, year: int | None = None
    ) -> list[Income]:
        query = (
            select(Income)
            .options(joinedload(Income.account), joinedload(Income.category))
            .where(
                Income.user_id == user_id,
                Income.is_active == True
            )
        )
        if month is not None:
            query = query.where(extract("month", Income.date) == month)
        if year is not None:
            query = query.where(extract("year", Income.date) == year)

        query = query.order_by(Income.date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: int, income_id: int) -> Income | None:
        result = await self.db.execute(
            select(Income)
            .options(joinedload(Income.account), joinedload(Income.category))
            .where(
                Income.user_id == user_id,
                Income.id == income_id,
                Income.is_active == True
            )
        )
        return result.scalar_one_or_none()
