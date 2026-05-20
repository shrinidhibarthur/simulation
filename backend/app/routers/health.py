from fastapi import APIRouter
from sqlalchemy import text

from app.database import AsyncSessionFactory
from app.config import settings

import redis.asyncio as aioredis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    db_ok = False
    redis_ok = False
    celery_ok = False

    # Check PostgreSQL
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # Check Redis
    try:
        r = aioredis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        await r.aclose()
        redis_ok = True
    except Exception:
        pass

    # Check Celery (inspect ping via Redis)
    try:
        from app.tasks.celery_app import celery_app
        result = celery_app.control.ping(timeout=1)
        celery_ok = bool(result)
    except Exception:
        pass

    return {
        "status": "ok" if all([db_ok, redis_ok]) else "degraded",
        "db": db_ok,
        "redis": redis_ok,
        "celery": celery_ok,
    }
