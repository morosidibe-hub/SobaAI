import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import chat as chat_route
from app.db import session as db_session
from app.main import app
from app.models import Base


@pytest.fixture
async def client(monkeypatch):
    """Client HTTP branché sur une base SQLite en mémoire (pas besoin de PostgreSQL)."""
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    monkeypatch.setattr(
        db_session, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False)
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    await engine.dispose()


@pytest.fixture
def fake_claude(monkeypatch):
    """Remplace l'appel à Claude ; enregistre l'historique reçu à chaque appel."""
    calls: list[list] = []

    async def fake_stream(history):
        calls.append(history)
        for chunk in ["Bon", "jour", " !"]:
            yield chunk

    monkeypatch.setattr(chat_route, "stream_reply", fake_stream)
    return calls
