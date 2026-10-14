import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from functools import lru_cache

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import User

logger = logging.getLogger(__name__)

SESSION_COOKIE = "sobaai_session"
JWT_ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()  # Argon2id
# Hash factice : quand l'email n'existe pas, on vérifie quand même un mot de passe
# pour que le temps de réponse ne révèle pas quels emails sont inscrits.
_DUMMY_HASH = password_hash.hash(secrets.token_urlsafe(16))


@lru_cache
def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if secret:
        return secret
    logger.warning(
        "JWT_SECRET non défini : clé temporaire générée, sessions perdues au redémarrage."
    )
    return secrets.token_urlsafe(32)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_session_token(user_id: uuid.UUID) -> str:
    expires = datetime.now(UTC) + timedelta(days=get_settings().session_days)
    return jwt.encode({"sub": str(user_id), "exp": expires}, _jwt_secret(), JWT_ALGORITHM)


def read_session_token(token: str) -> uuid.UUID | None:
    """Renvoie l'id utilisateur du jeton, ou None s'il est invalide ou expiré."""
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
        return uuid.UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == normalize_email(email)))


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    user = User(email=normalize_email(email), hashed_password=password_hash.hash(password))
    db.add(user)
    await db.commit()
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None:
        password_hash.verify(password, _DUMMY_HASH)
        return None
    if not password_hash.verify(password, user.hashed_password):
        return None
    return user
