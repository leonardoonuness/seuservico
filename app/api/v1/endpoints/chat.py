from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.chat import MessageCreate, MessageOut
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_service.get_user_conversations(db, current_user)


@router.get("/conversations/{chat_id}/messages", response_model=list[MessageOut])
def get_messages(
    chat_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.get_messages(db, current_user, chat_id, page, size)


@router.post("/conversations/{chat_id}/messages", response_model=MessageOut, status_code=201)
def send_message(
    chat_id: str,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.send_message(db, current_user, chat_id, data)


@router.put("/messages/{message_id}/read", response_model=MessageOut)
def mark_read(message_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_service.mark_as_read(db, current_user, message_id)
