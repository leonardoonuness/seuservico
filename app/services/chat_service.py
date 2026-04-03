from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.chat import Chat, Message
from app.models.user import User
from app.schemas.chat import MessageCreate


def get_user_conversations(db: Session, user: User) -> list:
    chats = db.query(Chat).filter(Chat.participants.contains([user.id])).order_by(Chat.updated_at.desc()).all()
    result = []
    for chat in chats:
        last_msg = (
            db.query(Message)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        unread = (
            db.query(Message)
            .filter(Message.chat_id == chat.id, Message.sender_id != user.id, Message.is_read == False)
            .count()
        )
        result.append({"chat": chat, "last_message": last_msg, "unread_count": unread})
    return result


def get_messages(db: Session, user: User, chat_id: str, page: int = 1, size: int = 50) -> list:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    if user.id not in chat.participants:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .offset((page - 1) * size).limit(size).all()
    )


def send_message(db: Session, user: User, chat_id: str, data: MessageCreate) -> Message:
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    if user.id not in chat.participants:
        raise HTTPException(status_code=403, detail="Acesso negado")
    msg = Message(chat_id=chat_id, sender_id=user.id, content=data.content)
    db.add(msg)
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(msg)
    return msg


def mark_as_read(db: Session, user: User, message_id: str) -> Message:
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    chat = db.query(Chat).filter(Chat.id == msg.chat_id).first()
    if user.id not in (chat.participants or []):
        raise HTTPException(status_code=403, detail="Acesso negado")
    if not msg.is_read:
        msg.is_read = True
        msg.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(msg)
    return msg
