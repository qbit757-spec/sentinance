from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import User
from app.repositories.base_repo import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.username.ilike(username),
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()
si_first_user_check = False # for helper purposes
