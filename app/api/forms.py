from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_current_user_id
from app.schemas import (
    LU63Create,
    LU63Response,
    LU59Create,
    LU59Response,
    GU26Create,
    GU26Response,
)
from app.services import DocumentService

router = APIRouter(prefix="/forms", tags=["Forms"])


# ==================== LU-63 ====================
@router.post("/lu63", response_model=LU63Response)
async def create_lu63_application(
    data: LU63Create,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание заявления на отправление грузо-багажа (форма ЛУ-63).
    """
    service = DocumentService(db)
    return await service.create_lu63(data, user_id)


# ==================== LU-59 ====================
@router.post("/lu59", response_model=LU59Response)
async def create_lu59_label(
    data: LU59Create,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание ярлыка на прием багажа (форма ЛУ-59).
    """
    service = DocumentService(db)
    return await service.create_lu59(data, user_id)


# ==================== GU-26 ====================
@router.post("/gu26", response_model=GU26Response)
async def create_gu26_list(
    data: GU26Create,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание сдаточного списка (форма ГУ-26).
    """
    service = DocumentService(db)
    return await service.create_gu26(data, user_id)
