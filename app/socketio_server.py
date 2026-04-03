import socketio
from app.core.security import decode_token
from app.db.session import SessionLocal
from app.models.user import User
from app.models.chat import Chat, Message
from datetime import datetime, timezone

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

# Map socket_id -> user_id
connected_users: dict[str, str] = {}


def _get_user_from_token(token: str) -> User | None:
    try:
        payload = decode_token(token)
        db = SessionLocal()
        user = db.query(User).filter(User.id == payload["sub"]).first()
        db.close()
        return user
    except Exception:
        return None


@sio.event
async def connect(sid, environ, auth):
    token = (auth or {}).get("token")
    if not token:
        return False  # Reject connection
    user = _get_user_from_token(token)
    if not user or user.is_blocked:
        return False
    connected_users[sid] = user.id
    await sio.emit("connected", {"user_id": user.id}, to=sid)


@sio.event
async def disconnect(sid):
    connected_users.pop(sid, None)


@sio.event
async def join_chat(sid, data):
    chat_id = data.get("chat_id")
    user_id = connected_users.get(sid)
    if not chat_id or not user_id:
        return

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat and user_id in chat.participants:
            await sio.enter_room(sid, f"chat:{chat_id}")
            await sio.emit("joined_chat", {"chat_id": chat_id}, to=sid)
    finally:
        db.close()


@sio.event
async def leave_chat(sid, data):
    chat_id = data.get("chat_id")
    if chat_id:
        await sio.leave_room(sid, f"chat:{chat_id}")


@sio.event
async def send_message(sid, data):
    chat_id = data.get("chat_id")
    content = (data.get("content") or "").strip()
    user_id = connected_users.get(sid)

    if not chat_id or not content or not user_id:
        await sio.emit("error", {"detail": "Dados inválidos"}, to=sid)
        return

    db = SessionLocal()
    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat or user_id not in chat.participants:
            await sio.emit("error", {"detail": "Acesso negado"}, to=sid)
            return

        msg = Message(
            chat_id=chat_id,
            sender_id=user_id,
            content=content,
        )
        db.add(msg)
        chat.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(msg)

        payload = {
            "id": msg.id,
            "chat_id": msg.chat_id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at.isoformat(),
        }
        await sio.emit("new_message", payload, room=f"chat:{chat_id}")
    finally:
        db.close()


@sio.event
async def typing(sid, data):
    chat_id = data.get("chat_id")
    user_id = connected_users.get(sid)
    if chat_id and user_id:
        await sio.emit("user_typing", {"user_id": user_id}, room=f"chat:{chat_id}", skip_sid=sid)


@sio.event
async def stop_typing(sid, data):
    chat_id = data.get("chat_id")
    user_id = connected_users.get(sid)
    if chat_id and user_id:
        await sio.emit("user_stopped_typing", {"user_id": user_id}, room=f"chat:{chat_id}", skip_sid=sid)
