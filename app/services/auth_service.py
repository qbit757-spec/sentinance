from datetime import timedelta
from fastapi import HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.core.config import settings
from app.db.models.user_model import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth_schema import Token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, username: str, password_plain: str) -> User:
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        if not security.verify_password(password_plain, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )
        return user

    async def register_user(self, username: str, password_plain: str) -> User:
        existing = await self.user_repo.get_by_username(username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado",
            )
        hashed_password = security.get_password_hash(password_plain)
        user_in = {"username": username, "password_hash": hashed_password}
        user = await self.user_repo.create(user_in)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    def generate_tokens(self, user_id: int) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        access_token = security.create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        refresh_token = security.create_refresh_token(
            subject=user_id, expires_delta=refresh_token_expires
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_type = payload.get("type")
            user_id = payload.get("sub")
            if token_type != "refresh" or not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de actualización inválido",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de actualización inválido o expirado",
            )

        # Generar nuevos tokens
        return self.generate_tokens(user_id=int(user_id))
