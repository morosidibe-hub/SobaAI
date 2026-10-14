import uuid

from fastapi import APIRouter, HTTPException, Response

from app.api.deps import CurrentUser
from app.db.session import DbSession
from app.schemas.conversation import ConversationDetail, ConversationOut
from app.services import conversations

router = APIRouter(prefix="/conversations", tags=["conversations"])

NOT_FOUND = "Conversation introuvable"


@router.get("", response_model=list[ConversationOut])
async def list_conversations(db: DbSession, user: CurrentUser):
    return await conversations.list_conversations(db, user.id)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: uuid.UUID, db: DbSession, user: CurrentUser):
    conversation = await conversations.get_conversation(
        db, conversation_id, user.id, with_messages=True
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: uuid.UUID, db: DbSession, user: CurrentUser):
    conversation = await conversations.get_conversation(
        db, conversation_id, user.id, with_messages=True
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    await conversations.delete_conversation(db, conversation)
    return Response(status_code=204)
