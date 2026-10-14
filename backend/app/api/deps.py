from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from app.db.session import DbSession
from app.models import User
from app.services.auth import SESSION_COOKIE, read_session_token


async def get_current_user(
    db: DbSession,
    session: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> User:
    user_id = read_session_token(session) if session else None
    user = await db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non connecté")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
