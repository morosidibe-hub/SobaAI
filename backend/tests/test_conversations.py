import uuid

from app.schemas.chat import ChatMessage
from app.services.conversations import make_title, to_history


async def test_list_conversations_most_recent_first(client, fake_claude):
    a = (await client.post("/api/chat", json={"message": "Première"})).headers["X-Conversation-Id"]
    b = (await client.post("/api/chat", json={"message": "Deuxième"})).headers["X-Conversation-Id"]
    # Une activité sur A la fait remonter en tête.
    await client.post("/api/chat", json={"conversation_id": a, "message": "Encore"})

    listing = (await client.get("/api/conversations")).json()
    assert [c["id"] for c in listing] == [a, b]


async def test_delete_conversation(client, fake_claude):
    cid = (await client.post("/api/chat", json={"message": "À supprimer"})).headers[
        "X-Conversation-Id"
    ]

    assert (await client.delete(f"/api/conversations/{cid}")).status_code == 204
    assert (await client.get(f"/api/conversations/{cid}")).status_code == 404
    assert (await client.get("/api/conversations")).json() == []


async def test_unknown_conversation_returns_404(client):
    assert (await client.get(f"/api/conversations/{uuid.uuid4()}")).status_code == 404
    assert (await client.delete(f"/api/conversations/{uuid.uuid4()}")).status_code == 404


def test_make_title_truncates_long_messages():
    assert make_title("  Bonjour\n  le monde ") == "Bonjour le monde"
    title = make_title("x" * 200)
    assert len(title) == 60 and title.endswith("…")


def test_to_history_merges_consecutive_roles():
    msgs = [
        ChatMessage(role="user", content="A"),
        ChatMessage(role="user", content="B"),
        ChatMessage(role="assistant", content="C"),
    ]
    history = to_history(msgs)
    assert [(m.role, m.content) for m in history] == [("user", "A\n\nB"), ("assistant", "C")]
