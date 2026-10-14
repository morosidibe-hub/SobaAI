from collections.abc import AsyncIterator
from functools import lru_cache

import anthropic

from app.core.config import get_settings
from app.schemas.chat import ChatMessage

SYSTEM_PROMPT = (
    "Tu es SobaAI, un assistant serviable et précis. "
    "Réponds dans la langue de l'utilisateur, de façon claire et concise."
)

REFUSAL_NOTICE = "\n\n_(Je ne peux pas répondre à cette demande.)_"


@lru_cache
def get_client() -> anthropic.AsyncAnthropic:
    # Sans clé explicite, le SDK lit ANTHROPIC_API_KEY ou un profil `ant auth login`.
    return anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)


async def stream_reply(messages: list[ChatMessage]) -> AsyncIterator[str]:
    """Envoie l'historique à Claude et renvoie la réponse morceau par morceau."""
    settings = get_settings()

    async with get_client().beta.messages.stream(
        model=settings.claude_model,
        max_tokens=settings.claude_max_tokens,
        system=SYSTEM_PROMPT,
        messages=[m.model_dump() for m in messages],
        output_config={"effort": settings.claude_effort},
        # Si le modèle décline la demande, l'API la relance sur un modèle de repli.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        async for text in stream.text_stream:
            yield text
        final = await stream.get_final_message()

    if final.stop_reason == "refusal":
        yield REFUSAL_NOTICE
