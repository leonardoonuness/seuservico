from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.service import ServiceRequestCreate, ServiceRequestOut, ReviewCreate, ReviewOut
from app.services import service_service

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/requests", response_model=ServiceRequestOut, status_code=201)
def create_request(
    data: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_service.create_request(db, current_user, data)


@router.get("/requests/client", response_model=list[ServiceRequestOut])
def client_requests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_service.get_client_requests(db, current_user, page, size)


@router.get("/requests/professional", response_model=list[ServiceRequestOut])
def professional_requests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_service.get_professional_requests(db, current_user, page, size)


@router.get("/requests/{request_id}", response_model=ServiceRequestOut)
def get_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.service import ServiceRequest
    from fastapi import HTTPException
    req = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    if req.client_id != current_user.id and req.professional_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return req


@router.put("/requests/{request_id}/accept", response_model=ServiceRequestOut)
def accept_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service_service.accept_request(db, current_user, request_id)


@router.put("/requests/{request_id}/reject", response_model=ServiceRequestOut)
def reject_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service_service.reject_request(db, current_user, request_id)


@router.put("/requests/{request_id}/start", response_model=ServiceRequestOut)
def start_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service_service.start_request(db, current_user, request_id)


@router.put("/requests/{request_id}/complete", response_model=ServiceRequestOut)
def complete_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service_service.complete_request(db, current_user, request_id)


@router.put("/requests/{request_id}/cancel", response_model=ServiceRequestOut)
def cancel_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service_service.cancel_request(db, current_user, request_id)


@router.post("/requests/{request_id}/rate", response_model=ReviewOut, status_code=201)
def rate_service(
    request_id: str,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service_service.rate_service(db, current_user, request_id, data)
