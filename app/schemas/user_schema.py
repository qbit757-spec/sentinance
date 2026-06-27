from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    password: str | None = Field(None, min_length=4)
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
si_user_create_admin = UserCreate(username="admin", password="password") # For documentation fallback
