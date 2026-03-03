from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models import UserRole, DocumentStatus


# ==================== AUTH ====================
class LoginRequest(BaseModel):
    track_number: str = Field(..., min_length=1, description="Трек-номер или ИИН")
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    bin: str = Field(..., min_length=12, max_length=12, description="БИН (12 цифр)")
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @field_validator('bin')
    @classmethod
    def validate_bin(cls, v):
        if not v.isdigit():
            raise ValueError('БИН должен содержать только цифры')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== USER ====================
class UserBase(BaseModel):
    inn: str
    email: EmailStr
    fio: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    fio: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    address: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PERSON INFO ====================
class PersonInfo(BaseModel):
    fio: str
    inn: str
    organization: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


# ==================== CARGO ====================
class CargoItemBase(BaseModel):
    name: str
    package_type: Optional[str] = None
    quantity: int = 1
    weight: float = 0.0
    declared_value: Optional[float] = None
    distance: Optional[float] = None
    rate: Optional[float] = None


class CargoItemCreate(CargoItemBase):
    pass


class CargoItemResponse(CargoItemBase):
    id: int
    
    class Config:
        from_attributes = True


# ==================== TRANSPORT DOCUMENT ====================
class DocumentBase(BaseModel):
    train_number: Optional[str] = None
    departure_station: str
    destination_station: str
    route: Optional[str] = None
    
    sender_fio: str
    sender_inn: str
    sender_organization: Optional[str] = None
    sender_address: Optional[str] = None
    sender_phone: Optional[str] = None
    
    receiver_fio: str
    receiver_inn: str
    receiver_organization: Optional[str] = None
    receiver_address: Optional[str] = None
    receiver_phone: Optional[str] = None
    
    total_cost: float = 0.0
    send_date: Optional[datetime] = None
    notes: Optional[str] = None


class DocumentCreate(DocumentBase):
    cargo_items: List[CargoItemCreate] = []


class DocumentUpdate(BaseModel):
    train_number: Optional[str] = None
    departure_station: Optional[str] = None
    destination_station: Optional[str] = None
    route: Optional[str] = None
    status: Optional[DocumentStatus] = None
    total_cost: Optional[float] = None
    send_date: Optional[datetime] = None
    notes: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    document_number: str
    status: DocumentStatus
    sender_id: int
    receiver_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    cargo_items: List[CargoItemResponse] = []
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    document_number: str
    inn: str
    train_number: Optional[str]
    sender_fio: str
    receiver_fio: str
    departure_station: str
    destination_station: str
    cargo_info: str
    status: DocumentStatus
    total_cost: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SEARCH ====================
class DocumentSearchParams(BaseModel):
    document_number: Optional[str] = None
    send_date: Optional[datetime] = None
    receive_date: Optional[datetime] = None
    send_station: Optional[str] = None
    dest_station: Optional[str] = None
    status: Optional[DocumentStatus] = None
    page: int = 1
    limit: int = 10


class PaginatedResponse(BaseModel):
    data: List[DocumentListResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# ==================== LU-63 ====================
class LU63Create(BaseModel):
    start_station: str
    destination_station: str
    
    sender_fio: str
    sender_inn: str
    sender_organization: Optional[str] = None
    sender_address: Optional[str] = None
    sender_phone: Optional[str] = None
    
    receiver_fio: str
    receiver_inn: str
    receiver_organization: Optional[str] = None
    receiver_address: Optional[str] = None
    receiver_phone: Optional[str] = None
    
    cargo_name: str
    cargo_amount: int = 1
    cargo_weight: float = 0.0
    packaging_type: Optional[str] = None


class LU63Response(BaseModel):
    id: int
    application_number: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== LU-59 ====================
class LU59Create(BaseModel):
    station: str
    receipt_date: datetime
    train_number: str
    document_number: Optional[str] = None
    destination_station: str
    receiver_fio: str
    cargo_name: str
    places_count: int = 1


class LU59Response(BaseModel):
    id: int
    label_number: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== GU-26 ====================
class GU26ItemCreate(BaseModel):
    doc_number: Optional[str] = None
    station_departure: Optional[str] = None
    station_destination: Optional[str] = None
    quantity: Optional[int] = None
    weight: Optional[float] = None
    brand: Optional[str] = None
    status: Optional[str] = None


class GU26Create(BaseModel):
    departure_station: str
    destination_station: str
    train_from: Optional[str] = None
    train_to: Optional[str] = None
    wagon_from: Optional[str] = None
    wagon_to: Optional[str] = None
    receiver_from: Optional[str] = None
    receiver_to: Optional[str] = None
    items: List[GU26ItemCreate] = []


class GU26Response(BaseModel):
    id: int
    list_number: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== COMMON ====================
class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
