import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.session import engine
from app.llm.base import LLMError

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Idempotent bootstrap; Alembic manages schema evolution in production.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Trivium API",
    description="Vibe code without getting dumber — coding activity in, durable knowledge out.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    # The AI provider is rate-limited/down even after retries. Surface it as a
    # temporary condition the user can retry — never a 500.
    return JSONResponse(
        status_code=503,
        content={"detail": "The AI provider is busy or rate-limited right now — please try again in a moment."},
        headers={"Retry-After": "30"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = response.headers.get("Cache-Control", "no-store")
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
