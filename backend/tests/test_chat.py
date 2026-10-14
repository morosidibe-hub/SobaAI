import uuid

from app.api.routes import chat as chat_route


async def test_chat_creates_conversation_and_saves_messages(client, fake_claude):
    response = await client.post("/api/chat", json={"message": "Bonjour SobaAI"})
    assert response.status_code == 200
    assert response.text == "Bonjour !"

    conversation_id = response.headers["X-Conversation-Id"]
    detail = (await client.get(f"/api/conversations/{conversation_id}")).json()
    assert detail["title"] == "Bonjour SobaAI"
    assert [(m["role"], m["content"]) for m in detail["messages"]] == [
        ("user", "Bonjour SobaAI"),
        ("assistant", "Bonjour !"),
    ]


async def test_chat_sends_previous_messages_to_claude(client, fake_claude):
    first = await client.post("/api/chat", json={"message": "Question 1"})
    conversation_id = first.headers["X-Conversation-Id"]

    await client.post(
        "/api/chat", json={"conversation_id": conversation_id, "message": "Question 2"}
    )

    history = fake_claude[-1]
    assert [(m.role, m.content) for m in history] == [
        ("user", "Question 1"),
        ("assistant", "Bonjour !"),
        ("user", "Question 2"),
    ]


async def test_chat_unknown_conversation_returns_404(client, fake_claude):
    response = await client.post(
        "/api/chat", json={"conversation_id": str(uuid.uuid4()), "message": "Salut"}
    )
    assert response.status_code == 404


async def test_chat_rejects_blank_message(client, fake_claude):
    response = await client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 422


async def test_chat_error_is_shown_but_not_saved(client, monkeypatch):
    async def no_credentials(history):
        raise TypeError('"Could not resolve authentication method. ..."')
        yield  # pragma: no cover - fait de cette fonction un générateur

    monkeypatch.setattr(chat_route, "stream_reply", no_credentials)
    response = await client.post("/api/chat", json={"message": "Salut"})
    assert "ANTHROPIC_API_KEY" in response.text

    detail = (
        await client.get(f"/api/conversations/{response.headers['X-Conversation-Id']}")
    ).json()
    assert [m["role"] for m in detail["messages"]] == ["user"]
