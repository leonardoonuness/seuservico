from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.service import ServiceRequest, ServiceStatus
from app.models.professional import Professional
from app.models.review import Review
from app.models.chat import Chat
from app.models.user import User
from app.schemas.service import ServiceRequestCreate, ReviewCreate


def create_request(db: Session, client: User, data: ServiceRequestCreate) -> ServiceRequest:
    req = ServiceRequest(
        client_id=client.id,
        professional_id=data.professional_id,
        category=data.category,
        service=data.service,
        description=data.description,
        address=data.address,
        city=data.city,
        latitude=data.latitude,
        longitude=data.longitude,
        scheduled_date=data.scheduled_date,
        price=data.price,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    # Auto-create chat if professional is set
    if data.professional_id:
        _ensure_chat(db, req)
    return req


def _ensure_chat(db: Session, req: ServiceRequest) -> Chat:
    existing = db.query(Chat).filter(Chat.service_request_id == req.id).first()
    if existing:
        return existing
    chat = Chat(
        participants=[req.client_id, req.professional_id],
        service_request_id=req.id,
    )
    db.add(chat)
    db.commit()
    return chat


def _get_request_or_404(db: Session, request_id: str) -> ServiceRequest:
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return req


def _transition(db: Session, req: ServiceRequest, target: ServiceStatus) -> ServiceRequest:
    req.status = target
    db.commit()
    db.refresh(req)
    return req


def get_client_requests(db: Session, user: User, page: int = 1, size: int = 20) -> list:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.client_id == user.id)
        .order_by(ServiceRequest.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )


def get_professional_requests(db: Session, user: User, page: int = 1, size: int = 20) -> list:
    return (
        db.query(ServiceRequest)
        .filter(ServiceRequest.professional_id == user.id)
        .order_by(ServiceRequest.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )


def accept_request(db: Session, user: User, request_id: str) -> ServiceRequest:
    req = _get_request_or_404(db, request_id)
    if req.professional_id and req.professional_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if req.status != ServiceStatus.pending:
        raise HTTPException(status_code=400, detail="Solicitação não está pendente")
    if not req.professional_id:
        req.professional_id = user.id
    _ensure_chat(db, req)
    return _transition(db, req, ServiceStatus.accepted)


def reject_request(db: Session, user: User, request_id: str) -> ServiceRequest:
    req = _get_request_or_404(db, request_id)
    if req.professional_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if req.status not in (ServiceStatus.pending, ServiceStatus.accepted):
        raise HTTPException(status_code=400, detail="Status inválido para recusa")
    return _transition(db, req, ServiceStatus.cancelled)


def start_request(db: Session, user: User, request_id: str) -> ServiceRequest:
    req = _get_request_or_404(db, request_id)
    if req.professional_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if req.status != ServiceStatus.accepted:
        raise HTTPException(status_code=400, detail="Serviço não foi aceito ainda")
    return _transition(db, req, ServiceStatus.in_progress)


def complete_request(db: Session, user: User, request_id: str) -> ServiceRequest:
    req = _get_request_or_404(db, request_id)
    if req.professional_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if req.status != ServiceStatus.in_progress:
        raise HTTPException(status_code=400, detail="Serviço não está em andamento")
    return _transition(db, req, ServiceStatus.completed)


def cancel_request(db: Session, user: User, request_id: str) -> ServiceRequest:
    req = _get_request_or_404(db, request_id)
    if req.client_id != user.id and req.professional_id != user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if req.status in (ServiceStatus.completed, ServiceStatus.cancelled):
        raise HTTPException(status_code=400, detail="Não é possível cancelar este serviço")
    return _transition(db, req, ServiceStatus.cancelled)


def rate_service(db: Session, user: User, request_id: str, data: ReviewCreate) -> Review:
    req = _get_request_or_404(db, request_id)
    if req.client_id != user.id:
        raise HTTPException(status_code=403, detail="Apenas o cliente pode avaliar")
    if req.status != ServiceStatus.completed:
        raise HTTPException(status_code=400, detail="Serviço não concluído")
    if db.query(Review).filter(Review.service_request_id == req.id).first():
        raise HTTPException(status_code=409, detail="Serviço já avaliado")
    review = Review(
        service_request_id=req.id,
        client_id=user.id,
        professional_id=req.professional_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    # Update professional rating
    prof = db.query(Professional).filter(Professional.user_id == req.professional_id).first()
    if prof:
        total = prof.total_ratings + 1
        prof.rating = ((prof.rating * prof.total_ratings) + data.rating) / total
        prof.total_ratings = total
    db.commit()
    db.refresh(review)
    return review
