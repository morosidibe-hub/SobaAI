import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints

MessageText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    # Absent → une nouvelle conversation est créée ; son id est renvoyé
    # dans l'en-tête X-Conversation-Id.
    conversation_id: uuid.UUID | None = None
    message: MessageText
