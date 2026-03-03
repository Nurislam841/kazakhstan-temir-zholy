from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core import get_db, get_current_user_id
from app.models import DocumentStatus
from app.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentSearchParams,
    PaginatedResponse,
    MessageResponse,
)
from app.services import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("", response_model=PaginatedResponse)
async def search_documents(
    document_number: Optional[str] = Query(None, description="Номер документа"),
    send_date: Optional[datetime] = Query(None, description="Дата отправки"),
    receive_date: Optional[datetime] = Query(None, description="Дата получения"),
    send_station: Optional[str] = Query(None, description="Станция отправления"),
    dest_station: Optional[str] = Query(None, description="Станция назначения"),
    status: Optional[DocumentStatus] = Query(None, description="Статус документа"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=100, description="Количество на странице"),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Поиск перевозочных документов с фильтрацией и пагинацией.
    """
    params = DocumentSearchParams(
        document_number=document_number,
        send_date=send_date,
        receive_date=receive_date,
        send_station=send_station,
        dest_station=dest_station,
        status=status,
        page=page,
        limit=limit,
    )
    
    service = DocumentService(db)
    return await service.search_documents(params, user_id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Получение документа по ID.
    """
    service = DocumentService(db)
    return await service.get_document_by_id(document_id, user_id)


@router.post("", response_model=DocumentResponse)
async def create_document(
    data: DocumentCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Создание нового перевозочного документа.
    """
    service = DocumentService(db)
    return await service.create_document(data, user_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    data: DocumentUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Обновление перевозочного документа.
    """
    service = DocumentService(db)
    return await service.update_document(document_id, data, user_id)


@router.post("/{document_id}/pay", response_model=DocumentResponse)
async def confirm_payment(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Подтверждение оплаты документа.
    """
    service = DocumentService(db)
    return await service.confirm_payment(document_id, user_id)
