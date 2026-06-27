from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.account_model import Account
from app.repositories.base_repo import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

    async def get_by_user(self, user_id: int) -> list[Account]:
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: int, account_id: int) -> Account | None:
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == user_id,
                Account.id == account_id,
                Account.is_active == True
            )
        )
        return result.scalar_one_or_none()
