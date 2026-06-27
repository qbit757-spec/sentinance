from typing import Generic, Type, TypeVar
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id, self.model.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.db.execute(
            select(self.model)
            .where(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def remove(self, id: int) -> ModelType | None:
        db_obj = await self.get(id)
        if db_obj:
            db_obj.is_active = False
            self.db.add(db_obj)
            await self.db.flush()
        return db_obj
