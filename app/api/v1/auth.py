from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth_schema import Token
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.rate_limiter import limiter

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_in.username, user_in.password)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    return auth_service.generate_tokens(user.id)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(refresh_token)
