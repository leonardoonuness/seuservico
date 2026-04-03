import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, Text, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class ServiceStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


def _now():
    return datetime.now(timezone.utc)


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    professional_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(200), nullable=False)
    service: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[ServiceStatus] = mapped_column(SAEnum(ServiceStatus), default=ServiceStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    client: Mapped["User"] = relationship("User", foreign_keys=[client_id], back_populates="sent_requests")
    professional: Mapped["User"] = relationship("User", foreign_keys=[professional_id], back_populates="received_requests")
    review: Mapped["Review"] = relationship("Review", back_populates="service_request", uselist=False)
    chat: Mapped["Chat"] = relationship("Chat", back_populates="service_request", uselist=False)
