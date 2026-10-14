from app.services.auth import SESSION_COOKIE
from tests.conftest import PASSWORD


async def test_register_opens_session(anon_client):
    response = await anon_client.post(
        "/api/auth/register", json={"email": "  Bob@Example.COM ", "password": PASSWORD}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "bob@example.com"
    assert "hashed_password" not in response.json()

    set_cookie = response.headers["set-cookie"]
    assert SESSION_COOKIE in set_cookie and "HttpOnly" in set_cookie

    me = await anon_client.get("/api/auth/me")
    assert me.status_code == 200 and me.json()["email"] == "bob@example.com"


async def test_register_rejects_duplicate_email_case_insensitive(client):
    response = await client.post(
        "/api/auth/register", json={"email": "ALICE@example.com", "password": PASSWORD}
    )
    assert response.status_code == 409


async def test_register_validates_input(anon_client):
    bad_email = await anon_client.post(
        "/api/auth/register", json={"email": "pas-un-email", "password": PASSWORD}
    )
    short_password = await anon_client.post(
        "/api/auth/register", json={"email": "c@example.com", "password": "court"}
    )
    assert bad_email.status_code == 422
    assert short_password.status_code == 422


async def test_login_and_logout(client, new_client):
    other = await new_client()
    wrong = await other.post(
        "/api/auth/login", json={"email": "alice@example.com", "password": "mauvais"}
    )
    unknown = await other.post(
        "/api/auth/login", json={"email": "inconnu@example.com", "password": PASSWORD}
    )
    # Même message dans les deux cas : on ne révèle pas quels emails existent.
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()

    ok = await other.post(
        "/api/auth/login", json={"email": "alice@example.com", "password": PASSWORD}
    )
    assert ok.status_code == 200
    assert (await other.get("/api/auth/me")).status_code == 200

    assert (await other.post("/api/auth/logout")).status_code == 204
    assert (await other.get("/api/auth/me")).status_code == 401


async def test_invalid_token_is_rejected(anon_client):
    anon_client.cookies.set(SESSION_COOKIE, "faux.jeton.jwt")
    assert (await anon_client.get("/api/auth/me")).status_code == 401


async def test_protected_routes_require_login(anon_client):
    assert (await anon_client.get("/api/conversations")).status_code == 401
    assert (await anon_client.post("/api/chat", json={"message": "Salut"})).status_code == 401
    assert (await anon_client.get("/api/health")).status_code == 200


async def test_users_cannot_see_each_other_conversations(client, new_client, fake_claude):
    cid = (await client.post("/api/chat", json={"message": "Secret"})).headers["X-Conversation-Id"]

    bob = await new_client()
    await bob.post("/api/auth/register", json={"email": "bob@example.com", "password": PASSWORD})

    assert (await bob.get("/api/conversations")).json() == []
    assert (await bob.get(f"/api/conversations/{cid}")).status_code == 404
    assert (await bob.delete(f"/api/conversations/{cid}")).status_code == 404
    hijack = await bob.post("/api/chat", json={"conversation_id": cid, "message": "Hop"})
    assert hijack.status_code == 404

    # La conversation d'Alice est intacte.
    detail = (await client.get(f"/api/conversations/{cid}")).json()
    assert len(detail["messages"]) == 2
