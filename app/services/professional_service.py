import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.professional import Professional
from app.models.user import User, UserType
from app.models.service import ServiceRequest, ServiceStatus
from app.models.review import Review
from app.schemas.professional import ProfessionalRegister, ProfessionalUpdate, AvailabilityUpdate
from app.core.config import settings


def register_professional(db: Session, user: User, data: ProfessionalRegister) -> Professional:
    if user.type != UserType.professional:
        user.type = UserType.professional
    if db.query(Professional).filter(Professional.user_id == user.id).first():
        raise HTTPException(status_code=409, detail="Perfil profissional já existe")
    prof = Professional(
        user_id=user.id,
        bio=data.bio,
        experience=data.experience,
        hourly_rate=data.hourly_rate,
        categories=data.categories,
        services=data.services,
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def update_professional(db: Session, user: User, data: ProfessionalUpdate) -> Professional:
    prof = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(prof, field, value)
    db.commit()
    db.refresh(prof)
    return prof


def list_professionals(
    db: Session,
    category: str | None = None,
    service: str | None = None,
    city: str | None = None,
    min_rating: float | None = None,
    page: int = 1,
    size: int = 20,
) -> list:
    query = (
        db.query(Professional)
        .join(User, Professional.user_id == User.id)
        .filter(User.is_blocked == False, User.is_verified == True)
    )
    if city:
        query = query.filter(User.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Professional.categories.contains([category]))
    if service:
        query = query.filter(Professional.services.contains([service]))
    if min_rating is not None:
        query = query.filter(Professional.rating >= min_rating)
    return query.order_by(Professional.is_premium.desc(), Professional.rating.desc()).offset((page - 1) * size).limit(size).all()


def get_professional_stats(db: Session, user: User) -> dict:
    prof = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    total = db.query(ServiceRequest).filter(ServiceRequest.professional_id == user.id).count()
    completed = db.query(ServiceRequest).filter(
        ServiceRequest.professional_id == user.id,
        ServiceRequest.status == ServiceStatus.completed,
    ).count()
    pending = db.query(ServiceRequest).filter(
        ServiceRequest.professional_id == user.id,
        ServiceRequest.status == ServiceStatus.pending,
    ).count()
    earnings_row = db.query(func.sum(ServiceRequest.price)).filter(
        ServiceRequest.professional_id == user.id,
        ServiceRequest.status == ServiceStatus.completed,
    ).scalar()
    return {
        "total_services": total,
        "completed_services": completed,
        "pending_services": pending,
        "average_rating": prof.rating,
        "total_reviews": prof.total_ratings,
        "monthly_earnings": float(earnings_row or 0),
    }


async def add_portfolio_image(db: Session, user: User, file: UploadFile) -> Professional:
    prof = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Formato inválido")
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande (máx 5MB)")
    upload_path = Path(settings.UPLOAD_DIR) / "portfolio"
    upload_path.mkdir(parents=True, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1]
    image_id = str(uuid.uuid4())
    filename = f"{image_id}.{ext}"
    with open(upload_path / filename, "wb") as f:
        f.write(content)
    portfolio = list(prof.portfolio or [])
    portfolio.append({"id": image_id, "url": f"/{settings.UPLOAD_DIR}/portfolio/{filename}"})
    prof.portfolio = portfolio
    db.commit()
    db.refresh(prof)
    return prof


def remove_portfolio_image(db: Session, user: User, image_id: str) -> Professional:
    prof = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    portfolio = [p for p in (prof.portfolio or []) if p.get("id") != image_id]
    if len(portfolio) == len(prof.portfolio or []):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    prof.portfolio = portfolio
    db.commit()
    db.refresh(prof)
    return prof


def update_availability(db: Session, user: User, data: AvailabilityUpdate) -> Professional:
    prof = db.query(Professional).filter(Professional.user_id == user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    prof.availability = data.availability
    db.commit()
    db.refresh(prof)
    return prof
