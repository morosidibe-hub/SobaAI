import re
import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, Message
from app.models.conversation import utcnow
from app.schemas.chat import ChatMessage

TITLE_MAX_LENGTH = 60


def make_title(first_message: str) -> str:
    text = re.sub(r"\s+", " ", first_message).strip()
    if len(text) <= TITLE_MAX_LENGTH:
        return text
    return text[: TITLE_MAX_LENGTH - 1].rstrip() + "…"


async def list_conversations(db: AsyncSession) -> Sequence[Conversation]:
    result = await db.scalars(select(Conversation).order_by(Conversation.updated_at.desc()))
    return result.all()


async def get_conversation(
    db: AsyncSession, conversation_id: uuid.UUID, *, with_messages: bool = False
) -> Conversation | None:
    options = [selectinload(Conversation.messages)] if with_messages else []
    return await db.get(Conversation, conversation_id, options=options)


async def create_conversation(db: AsyncSession, first_message: str) -> Conversation:
    conversation = Conversation(title=make_title(first_message))
    db.add(conversation)
    await db.commit()
    return conversation


async def add_message(
    db: AsyncSession, conversation: Conversation, role: str, content: str
) -> Message:
    message = Message(conversation_id=conversation.id, role=role, content=content)
    conversation.updated_at = utcnow()
    db.add(message)
    await db.commit()
    return message


async def delete_conversation(db: AsyncSession, conversation: Conversation) -> None:
    await db.delete(conversation)
    await db.commit()


def to_history(messages: Sequence[Message]) -> list[ChatMessage]:
    """Convertit les messages stockés en historique pour Claude.

    Les messages consécutifs du même rôle sont fusionnés (cas d'une réponse
    interrompue avant le premier mot : deux messages utilisateur se suivent).
    """
    history: list[ChatMessage] = []
    for m in messages:
        if history and history[-1].role == m.role:
            history[-1].content += "\n\n" + m.content
        else:
            history.append(ChatMessage(role=m.role, content=m.content))
    return history
