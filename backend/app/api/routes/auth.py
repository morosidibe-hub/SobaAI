from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.db.session import DbSession
from app.models import User
from app.schemas.auth import Credentials, RegisterRequest, UserOut
from app.services import auth

router = APIRouter(prefix="/auth", tags=["auth"])


def _open_session(response: Response, user: User) -> None:
    settings = get_settings()
    response.set_cookie(
        auth.SESSION_COOKIE,
        auth.create_session_token(user.id),
        max_age=settings.session_days * 24 * 3600,
        httponly=True,  # illisible depuis JavaScript
        samesite="lax",  # non envoyé par les requêtes POST d'autres sites
        secure=settings.cookie_secure,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, db: DbSession):
    if await auth.get_user_by_email(db, body.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet email")
    try:
        user = await auth.create_user(db, body.email, body.password)
    except IntegrityError:  # inscription simultanée avec le même email
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Un compte existe déjà avec cet email"
        ) from None
    _open_session(response, user)
    return user


@router.post("/login", response_model=UserOut)
async def login(body: Credentials, response: Response, db: DbSession):
    user = await auth.authenticate(db, body.email, body.password)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email ou mot de passe incorrect")
    _open_session(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(auth.SESSION_COOKIE, path="/")


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    return user
