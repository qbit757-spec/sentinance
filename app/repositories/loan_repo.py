from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.loan_model import Loan
from app.repositories.base_repo import BaseRepository


class LoanRepository(BaseRepository[Loan]):
    def __init__(self, db: AsyncSession):
        super().__init__(Loan, db)

    async def get_by_user(self, user_id: int) -> list[Loan]:
        result = await self.db.execute(
            select(Loan)
            .options(joinedload(Loan.account))
            .where(
                Loan.user_id == user_id,
                Loan.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: int, loan_id: int) -> Loan | None:
        result = await self.db.execute(
            select(Loan)
            .options(joinedload(Loan.account))
            .where(
                Loan.user_id == user_id,
                Loan.id == loan_id,
                Loan.is_active == True
            )
        )
        return result.scalar_one_or_none()
