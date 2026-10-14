import logging
import uuid
from collections.abc import AsyncIterator

import anthropic
import anyio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.db import session as db_session
from app.db.session import DbSession
from app.schemas.chat import ChatMessage, ChatRequest
from app.services import conversations
from app.services.llm import stream_reply

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

MISSING_KEY_MESSAGE = "Clé API Anthropic absente ou invalide (voir ANTHROPIC_API_KEY dans .env)."


async def _save_reply(conversation_id: uuid.UUID, content: str) -> None:
    # Session dédiée : celle de la requête est fermée une fois le streaming lancé.
    try:
        async with db_session.SessionLocal() as db:
            conversation = await conversations.get_conversation(db, conversation_id)
            if conversation is not None:
                await conversations.add_message(db, conversation, "assistant", content)
    except Exception:
        logger.exception("Impossible d'enregistrer la réponse de l'assistant")


async def _stream_and_save(
    conversation_id: uuid.UUID, history: list[ChatMessage]
) -> AsyncIterator[str]:
    # Une fois le streaming commencé, on ne peut plus changer le code HTTP :
    # les erreurs sont donc renvoyées sous forme de texte (et non enregistrées).
    reply: list[str] = []
    try:
        async for chunk in stream_reply(history):
            reply.append(chunk)
            yield chunk
    except anthropic.AuthenticationError:
        yield f"\n\n⚠️ {MISSING_KEY_MESSAGE}"
    except anthropic.RateLimitError:
        yield "\n\n⚠️ Trop de requêtes, réessayez dans un instant."
    except anthropic.APIStatusError as e:
        logger.exception("Erreur API Claude")
        yield f"\n\n⚠️ Erreur du service IA ({e.status_code})."
    except anthropic.APIConnectionError:
        yield "\n\n⚠️ Impossible de joindre le service IA."
    except TypeError as e:
        # Le SDK lève une TypeError quand aucune clé/identifiant n'est configuré.
        if "authentication" not in str(e):
            raise
        yield f"\n\n⚠️ {MISSING_KEY_MESSAGE}"
    finally:
        # Exécuté aussi quand l'utilisateur clique « Arrêter » : la réponse partielle
        # est conservée. Le shield empêche l'annulation de couper l'enregistrement.
        if reply:
            with anyio.CancelScope(shield=True):
                await _save_reply(conversation_id, "".join(reply))


@router.post("/chat")
async def chat(request: ChatRequest, db: DbSession) -> StreamingResponse:
    if request.conversation_id is None:
        conversation = await conversations.create_conversation(db, request.message)
        previous = []
    else:
        conversation = await conversations.get_conversation(
            db, request.conversation_id, with_messages=True
        )
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation introuvable")
        previous = list(conversation.messages)

    user_message = await conversations.add_message(db, conversation, "user", request.message)
    history = conversations.to_history([*previous, user_message])

    return StreamingResponse(
        _stream_and_save(conversation.id, history),
        media_type="text/plain; charset=utf-8",
        headers={"X-Conversation-Id": str(conversation.id)},
    )
