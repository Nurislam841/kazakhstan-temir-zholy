from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime
import random
import string

from app.models import (
    TransportDocument, 
    CargoItem, 
    DocumentStatus,
    LU63Application,
    LU59Label,
    GU26List,
    GU26Item,
)
from app.schemas import (
    DocumentCreate,
    DocumentUpdate,
    DocumentSearchParams,
    DocumentResponse,
    DocumentListResponse,
    PaginatedResponse,
    LU63Create,
    LU59Create,
    GU26Create,
)


def generate_document_number() -> str:
    """Generate unique document number."""
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"75{timestamp}{random_suffix}"


def generate_application_number() -> str:
    """Generate unique application number."""
    return ''.join(random.choices(string.digits, k=6))


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_documents(
        self, 
        params: DocumentSearchParams,
        user_id: int
    ) -> PaginatedResponse:
        """Search documents with filters and pagination."""
        query = select(TransportDocument).where(
            or_(
                TransportDocument.sender_id == user_id,
                TransportDocument.receiver_id == user_id
            )
        )
        
        # Apply filters
        if params.document_number:
            query = query.where(
                TransportDocument.document_number.contains(params.document_number)
            )
        
        if params.send_station:
            query = query.where(
                TransportDocument.departure_station.ilike(f"%{params.send_station}%")
            )
        
        if params.dest_station:
            query = query.where(
                TransportDocument.destination_station.ilike(f"%{params.dest_station}%")
            )
        
        if params.status:
            query = query.where(TransportDocument.status == params.status)
        
        if params.send_date:
            query = query.where(
                func.date(TransportDocument.send_date) == params.send_date.date()
            )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (params.page - 1) * params.limit
        query = query.offset(offset).limit(params.limit)
        query = query.options(selectinload(TransportDocument.cargo_items))
        query = query.order_by(TransportDocument.created_at.desc())
        
        result = await self.db.execute(query)
        documents = result.scalars().all()
        
        # Convert to response format
        data = []
        for doc in documents:
            cargo_names = [item.name for item in doc.cargo_items]
            data.append(DocumentListResponse(
                id=doc.id,
                document_number=doc.document_number,
                inn=doc.sender_inn,
                train_number=doc.train_number,
                sender_fio=doc.sender_fio,
                receiver_fio=doc.receiver_fio,
                departure_station=doc.departure_station,
                destination_station=doc.destination_station,
                cargo_info=", ".join(cargo_names) if cargo_names else "",
                status=doc.status,
                total_cost=doc.total_cost,
                created_at=doc.created_at,
            ))
        
        total_pages = (total + params.limit - 1) // params.limit
        
        return PaginatedResponse(
            data=data,
            total=total,
            page=params.page,
            limit=params.limit,
            total_pages=total_pages,
        )
    
    async def get_document_by_id(self, document_id: int, user_id: int) -> TransportDocument:
        """Get document by ID."""
        query = select(TransportDocument).where(
            TransportDocument.id == document_id
        ).options(selectinload(TransportDocument.cargo_items))
        
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Документ не найден",
            )
        
        # Check access
        if document.sender_id != user_id and document.receiver_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому документу",
            )
        
        return document
    
    async def create_document(self, data: DocumentCreate, user_id: int) -> TransportDocument:
        """Create a new transport document."""
        document = TransportDocument(
            document_number=generate_document_number(),
            sender_id=user_id,
            train_number=data.train_number,
            departure_station=data.departure_station,
            destination_station=data.destination_station,
            route=data.route,
            sender_fio=data.sender_fio,
            sender_inn=data.sender_inn,
            sender_organization=data.sender_organization,
            sender_address=data.sender_address,
            sender_phone=data.sender_phone,
            receiver_fio=data.receiver_fio,
            receiver_inn=data.receiver_inn,
            receiver_organization=data.receiver_organization,
            receiver_address=data.receiver_address,
            receiver_phone=data.receiver_phone,
            total_cost=data.total_cost,
            send_date=data.send_date,
            notes=data.notes,
            status=DocumentStatus.DRAFT,
        )
        
        self.db.add(document)
        await self.db.flush()
        
        # Add cargo items
        for item_data in data.cargo_items:
            cargo_item = CargoItem(
                document_id=document.id,
                name=item_data.name,
                package_type=item_data.package_type,
                quantity=item_data.quantity,
                weight=item_data.weight,
                declared_value=item_data.declared_value,
                distance=item_data.distance,
                rate=item_data.rate,
            )
            self.db.add(cargo_item)
        
        await self.db.flush()
        await self.db.refresh(document)
        
        return document
    
    async def update_document(
        self, 
        document_id: int, 
        data: DocumentUpdate, 
        user_id: int
    ) -> TransportDocument:
        """Update a transport document."""
        document = await self.get_document_by_id(document_id, user_id)
        
        # Check if user is sender
        if document.sender_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только отправитель может редактировать документ",
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)
        
        document.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(document)
        
        return document
    
    async def confirm_payment(self, document_id: int, user_id: int) -> TransportDocument:
        """Confirm payment for document."""
        document = await self.get_document_by_id(document_id, user_id)
        
        if document.status != DocumentStatus.PENDING and document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Документ не может быть оплачен в текущем статусе",
            )
        
        document.status = DocumentStatus.PAID
        document.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(document)
        
        return document
    
    # ==================== LU-63 ====================
    async def create_lu63(self, data: LU63Create, user_id: int) -> LU63Application:
        """Create LU-63 application."""
        application = LU63Application(
            application_number=generate_application_number(),
            user_id=user_id,
            start_station=data.start_station,
            destination_station=data.destination_station,
            sender_fio=data.sender_fio,
            sender_inn=data.sender_inn,
            sender_organization=data.sender_organization,
            sender_address=data.sender_address,
            sender_phone=data.sender_phone,
            receiver_fio=data.receiver_fio,
            receiver_inn=data.receiver_inn,
            receiver_organization=data.receiver_organization,
            receiver_address=data.receiver_address,
            receiver_phone=data.receiver_phone,
            cargo_name=data.cargo_name,
            cargo_amount=data.cargo_amount,
            cargo_weight=data.cargo_weight,
            packaging_type=data.packaging_type,
        )
        
        self.db.add(application)
        await self.db.flush()
        await self.db.refresh(application)
        
        return application
    
    # ==================== LU-59 ====================
    async def create_lu59(self, data: LU59Create, user_id: int) -> LU59Label:
        """Create LU-59 label."""
        label = LU59Label(
            label_number=generate_application_number(),
            user_id=user_id,
            station=data.station,
            receipt_date=data.receipt_date,
            train_number=data.train_number,
            document_number=data.document_number,
            destination_station=data.destination_station,
            receiver_fio=data.receiver_fio,
            cargo_name=data.cargo_name,
            places_count=data.places_count,
        )
        
        self.db.add(label)
        await self.db.flush()
        await self.db.refresh(label)
        
        return label
    
    # ==================== GU-26 ====================
    async def create_gu26(self, data: GU26Create, user_id: int) -> GU26List:
        """Create GU-26 list."""
        gu26_list = GU26List(
            list_number=generate_application_number(),
            user_id=user_id,
            departure_station=data.departure_station,
            destination_station=data.destination_station,
            train_from=data.train_from,
            train_to=data.train_to,
            wagon_from=data.wagon_from,
            wagon_to=data.wagon_to,
            receiver_from=data.receiver_from,
            receiver_to=data.receiver_to,
        )
        
        self.db.add(gu26_list)
        await self.db.flush()
        
        # Add items
        for item_data in data.items:
            item = GU26Item(
                gu26_list_id=gu26_list.id,
                doc_number=item_data.doc_number,
                station_departure=item_data.station_departure,
                station_destination=item_data.station_destination,
                quantity=item_data.quantity,
                weight=item_data.weight,
                brand=item_data.brand,
                status=item_data.status,
            )
            self.db.add(item)
        
        await self.db.flush()
        await self.db.refresh(gu26_list)
        
        return gu26_list
