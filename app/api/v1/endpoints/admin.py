from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_admin
from app.models.user import User
from app.schemas.admin import DashboardStats, BlockUser, ModerateReview, ReportMetrics
from app.schemas.professional import ProfessionalOut
from app.schemas.user import UserOut
from app.schemas.service import ReviewOut
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return admin_service.get_dashboard_stats(db)


@router.get("/professionals/pending", response_model=list[ProfessionalOut])
def pending_professionals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_service.list_pending_professionals(db, page, size)


@router.put("/professionals/{professional_id}/verify", response_model=ProfessionalOut)
def verify_professional(professional_id: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return admin_service.verify_professional(db, admin, professional_id)


@router.put("/professionals/{professional_id}/feature")
def feature_professional(
    professional_id: str,
    featured: bool = Query(True),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_service.feature_professional(db, professional_id, featured)


@router.get("/users", response_model=list[UserOut])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_service.list_users(db, page, size)


@router.put("/users/{user_id}/block", response_model=UserOut)
def block_user(user_id: str, data: BlockUser, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return admin_service.block_user(db, user_id, data)


@router.get("/reports/metrics")
def report_metrics(
    period: str = Query("monthly"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_service.get_report_metrics(db, period)


@router.get("/reviews/reported", response_model=list[ReviewOut])
def reported_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_service.get_reported_reviews(db, page, size)


@router.put("/reviews/{review_id}/moderate", response_model=ReviewOut)
def moderate_review(review_id: str, data: ModerateReview, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return admin_service.moderate_review(db, review_id, data)
