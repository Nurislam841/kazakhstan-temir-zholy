from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional

from app.models import User, UserRole
from app.schemas import RegisterRequest, UserResponse, TokenResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_inn(self, inn: str) -> Optional[User]:
        """Get user by INN."""
        result = await self.db.execute(
            select(User).where(User.inn == inn)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, track_number: str, password: str) -> User:
        """Authenticate user by track number (INN) and password."""
        user = await self.get_user_by_inn(track_number)
        
        if not user:
            # Try to find by email
            user = await self.get_user_by_email(track_number)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный трек-номер или пароль",
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный трек-номер или пароль",
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Аккаунт деактивирован",
            )
        
        return user
    
    async def register_user(self, data: RegisterRequest) -> User:
        """Register a new user."""
        # Check if user exists
        existing_user = await self.get_user_by_inn(data.bin)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким БИН уже существует",
            )
        
        existing_email = await self.get_user_by_email(data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )
        
        # Create user
        user = User(
            inn=data.bin,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            fio=data.company_name,  # Using company name as FIO for now
            phone=data.phone,
            organization=data.company_name,
            role=UserRole.USER,
            is_active=True,
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user."""
        token_data = {"sub": str(user.id), "inn": user.inn, "role": user.role.value}
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    
    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен",
            )
        
        user_id = payload.get("sub")
        user = await self.get_user_by_id(int(user_id))
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
            )
        
        return self.create_tokens(user)
