import time
from typing import Optional
import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request, status
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User

_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def rate_limit_dependency(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Redis sliding-window rate limiter keyed by tenant/user."""
    tenant_id = getattr(current_user, "tenant_id", None) or "default"
    user_id = getattr(current_user, "id", "anonymous")
    key = f"ratelimit:{tenant_id}:{user_id}:{request.url.path}"

    now = time.time()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    limit = settings.RATE_LIMIT_REQUESTS

    try:
        client = get_redis_client()
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zadd(key, {f"{now}": now})
        pipe.expire(key, window)
        _, current_count, _, _ = await pipe.execute()

        if current_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded ({limit} requests per {window}s).",
            )
    except HTTPException:
        raise
    except Exception:
        # Fail-open if Redis is unavailable in local unit-test environments
        return
