import os
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.service import ServiceRequest
from app.schemas.user import UserUpdate, PasswordChange
from app.core.security import verify_password, hash_password
from app.core.config import settings


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, data: PasswordChange) -> None:
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
    user.hashed_password = hash_password(data.new_password)
    db.commit()


async def upload_avatar(db: Session, user: User, file: UploadFile) -> User:
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato inválido. Use JPG, PNG ou WEBP.")
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Arquivo muito grande (máx 5MB)")
    upload_path = Path(settings.UPLOAD_DIR) / "avatars"
    upload_path.mkdir(parents=True, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = upload_path / filename
    with open(file_path, "wb") as f:
        f.write(content)
    if user.profile_image:
        old = Path(user.profile_image.lstrip("/"))
        if old.exists():
            old.unlink(missing_ok=True)
    user.profile_image = f"/{settings.UPLOAD_DIR}/avatars/{filename}"
    db.commit()
    db.refresh(user)
    return user


def get_user_services(db: Session, user: User, page: int = 1, size: int = 20) -> list:
    offset = (page - 1) * size
    return (
        db.query(ServiceRequest)
        .filter(
            (ServiceRequest.client_id == user.id) | (ServiceRequest.professional_id == user.id)
        )
        .order_by(ServiceRequest.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
