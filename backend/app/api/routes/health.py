from fastapi import APIRouter

from app.db.session import check_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "database": "ok" if await check_db() else "unavailable"}
