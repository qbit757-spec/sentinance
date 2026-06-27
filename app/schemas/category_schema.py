from datetime import datetime
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(Ingreso|Gasto)$")  # Debe ser "Ingreso" o "Gasto"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
