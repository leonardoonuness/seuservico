from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user, get_current_active_professional
from app.models.user import User
from app.schemas.professional import ProfessionalRegister, ProfessionalUpdate, ProfessionalOut, ProfessionalStats, AvailabilityUpdate
from app.services import professional_service

router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.get("/", response_model=list[ProfessionalOut])
def list_professionals(
    category: str | None = Query(None),
    service: str | None = Query(None),
    city: str | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=5),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return professional_service.list_professionals(db, category, service, city, min_rating, page, size)


@router.get("/me/stats", response_model=ProfessionalStats)
def get_my_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_professional)):
    return professional_service.get_professional_stats(db, current_user)


@router.get("/me/availability")
def get_availability(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_professional)):
    from app.models.professional import Professional
    prof = db.query(Professional).filter(Professional.user_id == current_user.id).first()
    return {"availability": prof.availability if prof else {}}


@router.put("/me/availability")
def update_availability(
    data: AvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_professional),
):
    return professional_service.update_availability(db, current_user, data)


@router.get("/{professional_id}", response_model=ProfessionalOut)
def get_professional(professional_id: str, db: Session = Depends(get_db)):
    from app.models.professional import Professional
    prof = db.query(Professional).filter(Professional.id == professional_id).first()
    if not prof:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return prof


@router.post("/register", response_model=ProfessionalOut, status_code=201)
def register_professional(
    data: ProfessionalRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return professional_service.register_professional(db, current_user, data)


@router.put("/me", response_model=ProfessionalOut)
def update_professional(
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_professional),
):
    return professional_service.update_professional(db, current_user, data)


@router.post("/me/portfolio", response_model=ProfessionalOut)
async def add_portfolio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_professional),
):
    return await professional_service.add_portfolio_image(db, current_user, file)


@router.delete("/me/portfolio/{image_id}", response_model=ProfessionalOut)
def remove_portfolio(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_professional),
):
    return professional_service.remove_portfolio_image(db, current_user, image_id)
