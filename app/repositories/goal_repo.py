from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.goal_model import Goal, GoalUser, GoalInvitation
from app.repositories.base_repo import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    def __init__(self, db: AsyncSession):
        super().__init__(Goal, db)

    async def get_by_user(self, user_id: int) -> list[Goal]:
        # Returns goals created by the user OR goals shared with the user
        result = await self.db.execute(
            select(Goal)
            .outerjoin(Goal.shared_users)
            .options(joinedload(Goal.shared_users).joinedload(GoalUser.user))
            .where(
                or_(
                    Goal.user_id == user_id,
                    GoalUser.user_id == user_id
                ),
                Goal.is_active == True
            )
        )
        return list(result.scalars().unique().all())

    async def get_by_user_and_id(self, user_id: int, goal_id: int) -> Goal | None:
        result = await self.db.execute(
            select(Goal)
            .outerjoin(Goal.shared_users)
            .options(joinedload(Goal.shared_users).joinedload(GoalUser.user))
            .where(
                or_(
                    Goal.user_id == user_id,
                    GoalUser.user_id == user_id
                ),
                Goal.id == goal_id,
                Goal.is_active == True
            )
        )
        return result.scalar_one_or_none()

    # --- Collaborative Collaborators & Invitations ---
    async def add_collaborator(self, goal_id: int, user_id: int) -> GoalUser:
        collab = GoalUser(goal_id=goal_id, user_id=user_id)
        self.db.add(collab)
        await self.db.flush()
        return collab

    async def check_collaborator_exists(self, goal_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(GoalUser).where(
                GoalUser.goal_id == goal_id,
                GoalUser.user_id == user_id,
                GoalUser.is_active == True
            )
        )
        return result.scalar_one_or_none() is not None

    async def create_invitation(self, goal_id: int, sender_id: int, receiver_id: int) -> GoalInvitation:
        inv = GoalInvitation(goal_id=goal_id, sender_id=sender_id, receiver_id=receiver_id)
        self.db.add(inv)
        await self.db.flush()
        return inv

    async def get_invitation(self, invitation_id: int) -> GoalInvitation | None:
        result = await self.db.execute(
            select(GoalInvitation)
            .options(
                joinedload(GoalInvitation.goal),
                joinedload(GoalInvitation.sender),
                joinedload(GoalInvitation.receiver)
            )
            .where(
                GoalInvitation.id == invitation_id,
                GoalInvitation.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_invitations_by_receiver(self, receiver_id: int) -> list[GoalInvitation]:
        result = await self.db.execute(
            select(GoalInvitation)
            .options(
                joinedload(GoalInvitation.goal),
                joinedload(GoalInvitation.sender),
                joinedload(GoalInvitation.receiver)
            )
            .where(
                GoalInvitation.receiver_id == receiver_id,
                GoalInvitation.status == "Pendiente",
                GoalInvitation.is_active == True
            )
        )
        return list(result.scalars().all())

    async def check_invitation_exists(self, goal_id: int, receiver_id: int) -> bool:
        result = await self.db.execute(
            select(GoalInvitation).where(
                GoalInvitation.goal_id == goal_id,
                GoalInvitation.receiver_id == receiver_id,
                GoalInvitation.is_active == True
            )
        )
        return result.scalar_one_or_none() is not None
