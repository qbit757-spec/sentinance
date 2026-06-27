from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User
from app.services.finance_service import FinanceService

router = APIRouter()


@router.get("")
async def get_dashboard(
    month: int = Query(default=datetime.utcnow().month, ge=1, le=12),
    year: int = Query(default=datetime.utcnow().year, ge=1900, le=2100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    finance_service = FinanceService(db)
    return await finance_service.get_dashboard_summary(current_user.id, month, year)
