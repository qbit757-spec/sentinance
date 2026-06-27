from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.schemas.goal_schema import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
    GoalInvitationCreate,
    GoalInvitationRespond,
    GoalInvitationResponse,
)
from app.repositories.goal_repo import GoalRepository
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    goal_repo = GoalRepository(db)
    return await goal_repo.get_by_user(current_user.id)


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.create_goal(current_user.id, goal_in.model_dump())


@router.get("/invitations/received", response_model=list[GoalInvitationResponse])
async def list_received_invitations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    goal_repo = GoalRepository(db)
    return await goal_repo.get_invitations_by_receiver(current_user.id)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal_repo = GoalRepository(db)
    goal = await goal_repo.get_by_user_and_id(current_user.id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal_repo = GoalRepository(db)
    goal = await goal_repo.get_by_user_and_id(current_user.id, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Meta no encontrada o no eres colaborador")
        
    updated = await goal_repo.update(goal, goal_in.model_dump(exclude_unset=True))
    await db.commit()
    return updated


@router.delete("/{goal_id}", response_model=GoalResponse)
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal_repo = GoalRepository(db)
    goal = await goal_repo.get_by_user_and_id(current_user.id, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Meta no encontrada o no tienes permisos de creador para eliminarla"
        )
        
    deleted = await goal_repo.remove(goal_id)
    await db.commit()
    return deleted


@router.post("/{goal_id}/invite", response_model=GoalInvitationResponse)
async def invite_collaborator(
    goal_id: int,
    inv_in: GoalInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if inv_in.goal_id != goal_id:
        raise HTTPException(status_code=400, detail="ID de meta inconsistente")
        
    finance_service = FinanceService(db)
    return await finance_service.send_goal_invitation(
        current_user.id,
        goal_id,
        inv_in.receiver_username
    )


@router.post("/invitations/{invitation_id}/respond", response_model=GoalInvitationResponse)
async def respond_invitation(
    invitation_id: int,
    resp: GoalInvitationRespond,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.respond_to_invitation(
        current_user.id,
        invitation_id,
        resp.accept
    )
