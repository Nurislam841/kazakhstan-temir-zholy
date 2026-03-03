from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    CASHIER = "cashier"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inn: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    fio: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents_as_sender: Mapped[List["TransportDocument"]] = relationship(
        "TransportDocument", 
        back_populates="sender",
        foreign_keys="TransportDocument.sender_id"
    )
    documents_as_receiver: Mapped[List["TransportDocument"]] = relationship(
        "TransportDocument", 
        back_populates="receiver",
        foreign_keys="TransportDocument.receiver_id"
    )


class TransportDocument(Base):
    __tablename__ = "transport_documents"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    # Train info
    train_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    departure_station: Mapped[str] = mapped_column(String(100))
    destination_station: Mapped[str] = mapped_column(String(100))
    route: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Sender
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    sender_fio: Mapped[str] = mapped_column(String(255))
    sender_inn: Mapped[str] = mapped_column(String(12))
    sender_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Receiver
    receiver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    receiver_fio: Mapped[str] = mapped_column(String(255))
    receiver_inn: Mapped[str] = mapped_column(String(12))
    receiver_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    receiver_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receiver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Status and payment
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Dates
    send_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    receive_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    sender: Mapped["User"] = relationship("User", back_populates="documents_as_sender", foreign_keys=[sender_id])
    receiver: Mapped[Optional["User"]] = relationship("User", back_populates="documents_as_receiver", foreign_keys=[receiver_id])
    cargo_items: Mapped[List["CargoItem"]] = relationship("CargoItem", back_populates="document", cascade="all, delete-orphan")


class CargoItem(Base):
    __tablename__ = "cargo_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("transport_documents.id"))
    
    name: Mapped[str] = mapped_column(String(255))
    package_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    declared_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationship
    document: Mapped["TransportDocument"] = relationship("TransportDocument", back_populates="cargo_items")


class LU63Application(Base):
    """Заявление на отправление грузо-багажа (форма ЛУ-63)"""
    __tablename__ = "lu63_applications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    start_station: Mapped[str] = mapped_column(String(100))
    destination_station: Mapped[str] = mapped_column(String(100))
    
    # Sender
    sender_fio: Mapped[str] = mapped_column(String(255))
    sender_inn: Mapped[str] = mapped_column(String(12))
    sender_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Receiver
    receiver_fio: Mapped[str] = mapped_column(String(255))
    receiver_inn: Mapped[str] = mapped_column(String(12))
    receiver_organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    receiver_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receiver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Cargo
    cargo_name: Mapped[str] = mapped_column(String(255))
    cargo_amount: Mapped[int] = mapped_column(Integer, default=1)
    cargo_weight: Mapped[float] = mapped_column(Float, default=0.0)
    packaging_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LU59Label(Base):
    """Ярлык на прием багажа (форма ЛУ-59)"""
    __tablename__ = "lu59_labels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    label_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    station: Mapped[str] = mapped_column(String(100))
    receipt_date: Mapped[datetime] = mapped_column(DateTime)
    train_number: Mapped[str] = mapped_column(String(20))
    document_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    destination_station: Mapped[str] = mapped_column(String(100))
    receiver_fio: Mapped[str] = mapped_column(String(255))
    cargo_name: Mapped[str] = mapped_column(String(255))
    places_count: Mapped[int] = mapped_column(Integer, default=1)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GU26List(Base):
    """Сдаточный список (форма ГУ-26)"""
    __tablename__ = "gu26_lists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    list_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    
    departure_station: Mapped[str] = mapped_column(String(100))
    destination_station: Mapped[str] = mapped_column(String(100))
    train_from: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    train_to: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    wagon_from: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    wagon_to: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    receiver_from: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    receiver_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    items: Mapped[List["GU26Item"]] = relationship("GU26Item", back_populates="gu26_list", cascade="all, delete-orphan")


class GU26Item(Base):
    """Строка сдаточного списка ГУ-26"""
    __tablename__ = "gu26_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gu26_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("gu26_lists.id"))
    
    doc_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    station_departure: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    station_destination: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    gu26_list: Mapped["GU26List"] = relationship("GU26List", back_populates="items")
