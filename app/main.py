"""FastAPI application factory, lifespan and health route.

Run with ``uvicorn --factory app.main:create_app``. Settings are injectable so
tests never depend on the process environment.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import Settings, load_settings

logger = logging.getLogger(__name__)


def degraded_reasons(settings: Settings) -> list[str]:
    reasons: list[str] = []
    if not settings.openai_api_key_set:
        reasons.append("openai_api_key_missing")
    return reasons


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings if settings is not None else load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = resolved
        app.state.degraded_reasons = degraded_reasons(resolved)
        # Log key names and booleans only, never values.
        logger.info(
            "startup openai_api_key_set=%s degraded_reasons=%s",
            resolved.openai_api_key_set,
            app.state.degraded_reasons,
        )
        yield

    app = FastAPI(title="SlideRAG Mini", lifespan=lifespan)

    @app.get("/health")
    async def health(request: Request) -> JSONResponse:
        reasons: list[str] = request.app.state.degraded_reasons
        key_set: bool = request.app.state.settings.openai_api_key_set
        if reasons:
            return JSONResponse(
                status_code=503,
                content={"status": "degraded", "reasons": reasons, "openai_api_key_set": key_set},
            )
        return JSONResponse(
            status_code=200, content={"status": "ok", "openai_api_key_set": key_set}
        )

    return app
