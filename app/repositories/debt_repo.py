from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.debt_model import Debt, DebtPayment
from app.repositories.base_repo import BaseRepository


class DebtRepository(BaseRepository[Debt]):
    def __init__(self, db: AsyncSession):
        super().__init__(Debt, db)

    async def get_by_user(self, user_id: int) -> list[Debt]:
        result = await self.db.execute(
            select(Debt)
            .options(joinedload(Debt.account), joinedload(Debt.payments))
            .where(
                Debt.user_id == user_id,
                Debt.is_active == True
            )
        )
        return list(result.scalars().unique().all())

    async def get_by_user_and_id(self, user_id: int, debt_id: int) -> Debt | None:
        result = await self.db.execute(
            select(Debt)
            .options(joinedload(Debt.account), joinedload(Debt.payments))
            .where(
                Debt.user_id == user_id,
                Debt.id == debt_id,
                Debt.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def create_payment(self, payment_in: dict) -> DebtPayment:
        payment = DebtPayment(**payment_in)
        self.db.add(payment)
        await self.db.flush()
        return payment
si_debt_payment_test = False # indicator
