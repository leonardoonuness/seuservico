from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime
from app.models.service import ServiceStatus


class ServiceRequestCreate(BaseModel):
    professional_id: Optional[str] = None
    category: str
    service: str
    description: Optional[str] = None
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    price: Optional[float] = None


class ServiceRequestOut(BaseModel):
    id: str
    client_id: str
    professional_id: Optional[str] = None
    category: str
    service: str
    description: Optional[str] = None
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    price: Optional[float] = None
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Nota deve ser entre 1 e 5")
        return v


class ReviewOut(BaseModel):
    id: str
    service_request_id: str
    client_id: str
    professional_id: str
    rating: int
    comment: Optional[str] = None
    is_reported: bool
    is_removed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
