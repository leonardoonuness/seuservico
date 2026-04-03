from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ProfessionalRegister(BaseModel):
    bio: Optional[str] = None
    experience: Optional[str] = None
    hourly_rate: Optional[float] = None
    categories: List[str] = []
    services: List[str] = []


class ProfessionalUpdate(BaseModel):
    bio: Optional[str] = None
    experience: Optional[str] = None
    hourly_rate: Optional[float] = None
    categories: Optional[List[str]] = None
    services: Optional[List[str]] = None


class ProfessionalOut(BaseModel):
    id: str
    user_id: str
    bio: Optional[str] = None
    experience: Optional[str] = None
    hourly_rate: Optional[float] = None
    rating: float
    total_ratings: int
    is_premium: bool
    portfolio: List[Any] = []
    categories: List[str] = []
    services: List[str] = []
    verified_at: Optional[datetime] = None
    availability: dict = {}

    model_config = {"from_attributes": True}


class ProfessionalWithUser(ProfessionalOut):
    user: Any  # UserOut nested

    model_config = {"from_attributes": True}


class AvailabilityUpdate(BaseModel):
    availability: dict


class ProfessionalStats(BaseModel):
    total_services: int
    completed_services: int
    pending_services: int
    average_rating: float
    total_reviews: int
    monthly_earnings: float
