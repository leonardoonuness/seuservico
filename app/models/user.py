import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum


class UserType(str, enum.Enum):
    client = "client"
    professional = "professional"
    admin = "admin"


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    type: Mapped[UserType] = mapped_column(SAEnum(UserType), default=UserType.client)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    fcm_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    professional: Mapped["Professional"] = relationship("Professional", back_populates="user", uselist=False)
    sent_requests: Mapped[list["ServiceRequest"]] = relationship("ServiceRequest", foreign_keys="ServiceRequest.client_id", back_populates="client")
    received_requests: Mapped[list["ServiceRequest"]] = relationship("ServiceRequest", foreign_keys="ServiceRequest.professional_id", back_populates="professional")
