from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.professional import Professional
from app.models.service import ServiceRequest, ServiceStatus
from app.models.review import Review
from app.schemas.admin import BlockUser, ModerateReview


def get_dashboard_stats(db: Session) -> dict:
    total_users = db.query(User).count()
    total_professionals = db.query(User).filter(User.type == "professional").count()
    total_clients = db.query(User).filter(User.type == "client").count()
    total_services = db.query(ServiceRequest).count()
    completed = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceStatus.completed).count()
    pending = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceStatus.pending).count()
    total_reviews = db.query(Review).count()
    reported = db.query(Review).filter(Review.is_reported == True).count()
    premium = db.query(Professional).filter(Professional.is_premium == True).count()
    return {
        "total_users": total_users,
        "total_professionals": total_professionals,
        "total_clients": total_clients,
        "total_services": total_services,
        "completed_services": completed,
        "pending_services": pending,
        "total_reviews": total_reviews,
        "reported_reviews": reported,
        "premium_professionals": premium,
    }


def list_pending_professionals(db: Session, page: int = 1, size: int = 20) -> list:
    return (
        db.query(Professional)
        .join(User, Professional.user_id == User.id)
        .filter(User.is_verified == False, User.is_blocked == False)
        .offset((page - 1) * size).limit(size).all()
    )


def verify_professional(db: Session, admin: User, professional_id: str) -> Professional:
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    user = db.query(User).filter(User.id == prof.user_id).first()
    user.is_verified = True
    prof.verified_at = datetime.now(timezone.utc)
    prof.verified_by = admin.id
    db.commit()
    db.refresh(prof)
    return prof


def feature_professional(db: Session, professional_id: str, featured: bool) -> Professional:
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    prof.is_premium = featured
    db.commit()
    db.refresh(prof)
    return prof


def list_users(db: Session, page: int = 1, size: int = 20) -> list:
    return db.query(User).order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()


def block_user(db: Session, user_id: str, data: BlockUser) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user.is_blocked = True
    user.block_reason = data.reason
    db.commit()
    db.refresh(user)
    return user


def get_reported_reviews(db: Session, page: int = 1, size: int = 20) -> list:
    return (
        db.query(Review)
        .filter(Review.is_reported == True, Review.is_removed == False)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )


def moderate_review(db: Session, review_id: str, data: ModerateReview) -> Review:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    if data.action == "remove":
        review.is_removed = True
        review.removal_reason = data.reason
    else:
        review.is_reported = False
    db.commit()
    db.refresh(review)
    return review


def get_report_metrics(db: Session, period: str = "monthly") -> dict:
    total_reviews = db.query(Review).count()
    avg_rating = db.query(func.avg(Review.rating)).scalar() or 0
    new_users = db.query(User).count()
    new_services = db.query(ServiceRequest).count()
    completed = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceStatus.completed).count()
    cancelled = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceStatus.cancelled).count()
    return {
        "period": period,
        "new_users": new_users,
        "new_services": new_services,
        "completed_services": completed,
        "cancelled_services": cancelled,
        "average_rating": round(float(avg_rating), 2),
    }
