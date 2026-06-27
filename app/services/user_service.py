from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user_model import User
from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int) -> User | None:
        return await self.user_repo.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return await self.user_repo.get_by_username(username)
