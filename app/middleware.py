import time
import structlog
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

limiter = Limiter(key_func=get_remote_address)

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=round(process_time, 4),
    )
    return response

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
        )
    except Exception as e:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )
