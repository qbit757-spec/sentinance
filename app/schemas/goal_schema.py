from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.schemas.user_schema import UserResponse


class GoalUserResponse(BaseModel):
    id: int
    goal_id: int
    user_id: int
    user: UserResponse | None = None

    class Config:
        from_attributes = True


class GoalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=Decimal("0.00"))
    target_date: datetime
    accumulated_amount: Decimal = Field(default=Decimal("0.00"))
    priority: str = Field(default="Media", pattern="^(Baja|Media|Alta)$")
    status: str = Field(default="En progreso", pattern="^(En progreso|Completada)$")


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: str | None = None
    target_amount: Decimal | None = None
    target_date: datetime | None = None
    accumulated_amount: Decimal | None = None
    priority: str | None = None
    status: str | None = None
    is_active: bool | None = None


class GoalResponse(GoalBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    shared_users: list[GoalUserResponse] = []

    class Config:
        from_attributes = True


class GoalInvitationCreate(BaseModel):
    goal_id: int
    receiver_username: str = Field(..., min_length=3, max_length=50)


class GoalInvitationRespond(BaseModel):
    accept: bool


class GoalInvitationResponse(BaseModel):
    id: int
    goal_id: int
    sender_id: int
    receiver_id: int
    status: str
    sent_date: datetime
    is_active: bool
    goal: GoalResponse | None = None
    sender: UserResponse | None = None
    receiver: UserResponse | None = None

    class Config:
        from_attributes = True
