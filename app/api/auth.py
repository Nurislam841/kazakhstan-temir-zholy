from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_current_user_id
from app.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Авторизация пользователя.
    
    - **track_number**: ИИН или email
    - **password**: Пароль
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(data.track_number, data.password)
    return auth_service.create_tokens(user)


@router.post("/register", response_model=TokenResponse)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    - **company_name**: Наименование компании
    - **bin**: БИН (12 цифр)
    - **email**: Email
    - **phone**: Телефон
    - **password**: Пароль (минимум 6 символов)
    - **confirm_password**: Подтверждение пароля
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(data)
    return auth_service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access токена с помощью refresh токена.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем пользователе.
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    
    return user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user_id: int = Depends(get_current_user_id)
):
    """
    Выход из системы.
    
    Примечание: в текущей реализации токен не инвалидируется на сервере.
    Клиент должен удалить токен локально.
    """
    return MessageResponse(message="Выход выполнен успешно")
