from sqlalchemy import select, extract
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.expense_model import Expense
from app.repositories.base_repo import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: AsyncSession):
        super().__init__(Expense, db)

    async def get_by_user(
        self, user_id: int, month: int | None = None, year: int | None = None
    ) -> list[Expense]:
        query = (
            select(Expense)
            .options(joinedload(Expense.account), joinedload(Expense.category))
            .where(
                Expense.user_id == user_id,
                Expense.is_active == True
            )
        )
        if month is not None:
            query = query.where(extract("month", Expense.date) == month)
        if year is not None:
            query = query.where(extract("year", Expense.date) == year)

        query = query.order_by(Expense.date.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: int, expense_id: int) -> Expense | None:
        result = await self.db.execute(
            select(Expense)
            .options(joinedload(Expense.account), joinedload(Expense.category))
            .where(
                Expense.user_id == user_id,
                Expense.id == expense_id,
                Expense.is_active == True
            )
        )
        return result.scalar_one_or_none()
