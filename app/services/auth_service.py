from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.db.redis import blacklist_token, is_token_blacklisted


def register_user(db: Session, data: UserRegister) -> User:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado")
    user = User(
        name=data.name,
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        phone=data.phone,
        city=data.city,
        type=data.type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, data: UserLogin) -> dict:
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Conta bloqueada: {user.block_reason}")
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": user,
    }


def refresh_tokens(db: Session, refresh_token: str) -> dict:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    if is_token_blacklisted(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revogado")
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    blacklist_token(refresh_token, expire_seconds=60 * 60 * 24 * 7)
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": create_refresh_token(user.id),
        "token_type": "bearer",
        "user": user,
    }


def logout_user(access_token: str) -> None:
    blacklist_token(access_token, expire_seconds=60 * 60)


def request_password_reset(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        # Do not reveal whether user exists
        return "Se o e-mail existir, você receberá instruções."
    token = create_access_token(user.id)
    # TODO: send email with token
    return token


def reset_password(db: Session, token: str, new_password: str) -> None:
    payload = decode_token(token)
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    user.hashed_password = hash_password(new_password)
    db.commit()
