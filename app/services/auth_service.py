import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User, VALID_USER_TYPES
from app.schemas.user import UserRegister, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.db.redis import blacklist_token, is_token_blacklisted

logger = logging.getLogger(__name__)


def register_user(db: Session, data: UserRegister) -> User:
    """Register a new user with validation and error handling."""
    try:
        # Validate user type
        if data.type not in VALID_USER_TYPES:
            logger.warning(f"Invalid user type: {data.type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de usuário inválido. Use: {', '.join(VALID_USER_TYPES)}"
            )
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == data.email.lower()).first()
        if existing_user:
            logger.warning(f"Email already registered: {data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado"
            )
        
        logger.info(f"Registering new user: {data.email}, type: {data.type}")
        
        # Create new user
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
        
        logger.info(f"User registered successfully: {user.id}")
        return user
    
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao registrar usuário. Email pode já estar cadastrado."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        )


def login_user(db: Session, data: UserLogin) -> dict:
    logger.info(f"Login attempt for email: {data.email}")
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {data.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    if user.is_blocked:
        logger.warning(f"Blocked user login attempt: {user.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Conta bloqueada: {user.block_reason}")
    
    logger.info(f"Successful login for user: {user.id}")
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
