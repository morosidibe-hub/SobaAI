from contextlib import AsyncExitStack

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes import chat as chat_route
from app.db import session as db_session
from app.main import app
from app.models import Base

PASSWORD = "motdepasse-solide"


@pytest.fixture
async def new_client(monkeypatch):
    """Fabrique de clients HTTP (non connectés) partageant une base SQLite en mémoire."""
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    monkeypatch.setattr(
        db_session, "SessionLocal", async_sessionmaker(engine, expire_on_commit=False)
    )

    async with AsyncExitStack() as stack:

        async def make() -> AsyncClient:
            transport = ASGITransport(app=app)
            return await stack.enter_async_context(
                AsyncClient(transport=transport, base_url="http://test")
            )

        yield make
    await engine.dispose()


@pytest.fixture
async def anon_client(new_client) -> AsyncClient:
    return await new_client()


@pytest.fixture
async def client(new_client) -> AsyncClient:
    """Client connecté en tant que alice@example.com."""
    c = await new_client()
    response = await c.post(
        "/api/auth/register", json={"email": "alice@example.com", "password": PASSWORD}
    )
    assert response.status_code == 201
    return c


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
