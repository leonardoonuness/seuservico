from pydantic import BaseModel
from typing import Optional


class DashboardStats(BaseModel):
    total_users: int
    total_professionals: int
    total_clients: int
    total_services: int
    completed_services: int
    pending_services: int
    total_reviews: int
    reported_reviews: int
    premium_professionals: int


class BlockUser(BaseModel):
    reason: str


class ModerateReview(BaseModel):
    action: str  # "remove" | "keep"
    reason: Optional[str] = None


class ReportMetrics(BaseModel):
    period: str
    new_users: int
    new_services: int
    completed_services: int
    cancelled_services: int
    average_rating: float
