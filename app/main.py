"""FastAPI application factory, lifespan, routes and public error mapping.

Run with ``uvicorn --factory app.main:create_app`` (one worker: one process owns
the data root). Settings, embeddings and the structured generator are injectable
so tests use deterministic fakes; when they are not injected, real OpenAI clients
are built only if a key is configured. There is no fake fallback: a missing key
or unusable provider client keeps ``/health`` degraded and upload/ask at 503.

Status mapping: 409 busy, 503 degraded/missing key, 502 provider error, and
400/413/415 for client errors, always with generic messages that never echo
request content.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable, MutableMapping
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from langchain_core.embeddings import Embeddings
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException
from starlette.formparsers import MultiPartException

from app import ingestion
from app.config import (
    MAX_FORM_REQUEST_BYTES,
    MAX_QUESTION_CHARS,
    MAX_REQUEST_BYTES,
    Settings,
    load_settings,
)
from app.ingestion import BusyError, DataRoot, DegradedError, UploadRejected
from app.rag import (
    ProviderError,
    StructuredGenerator,
    StructuredOutputUnsupportedError,
    answer_question,
    build_answer_graph,
    build_embeddings,
    build_structured_generator,
)

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parent

_KIND_STATUS = {"too_large": 413, "unsupported": 415, "invalid": 400}
MSG_BUSY = "Another upload or question is in progress. Please retry shortly."
MSG_DEGRADED = "The service is unavailable: storage or provider configuration needs attention."
MSG_PROVIDER = "The model provider did not respond successfully. Please retry."
MSG_QUESTION = f"Enter a question of 1 to {MAX_QUESTION_CHARS} characters."
MSG_FORM = "The form submission was not understood."
MSG_INGEST_FAILED = "The upload could not be indexed and nothing was kept. Please retry."


def degraded_reasons(settings: Settings) -> list[str]:
    reasons: list[str] = []
    if not settings.openai_api_key_set:
        reasons.append("openai_api_key_missing")
    return reasons


def _build_providers(
    settings: Settings,
    embeddings: Embeddings | None,
    generator: StructuredGenerator | None,
    reasons: list[str],
) -> tuple[Embeddings | None, StructuredGenerator | None]:
    """Real clients only with a key; construction failures become degraded reasons.

    Without a key nothing is built and ``openai_api_key_missing`` already blocks use.
    """
    if not settings.openai_api_key_set:
        return embeddings, generator
    try:
        if embeddings is None:
            embeddings = build_embeddings(settings)
        if generator is None:
            generator = build_structured_generator(settings)
    except StructuredOutputUnsupportedError:
        reasons.append("structured_output_unsupported")
    except Exception as exc:  # e.g. an endpoint the HTTP client refuses at construction
        logger.error("provider client construction failed: %s", type(exc).__name__)
        reasons.append("provider_client_unavailable")
    return embeddings, generator


# ── Bounded request bodies (enforced while receiving, before parsing) ───


class _BodyTooLarge(Exception):
    pass


Receive = Callable[[], Awaitable[MutableMapping[str, Any]]]


def _bounded_receive(receive: Receive, limit: int) -> Receive:
    received = 0

    async def wrapped() -> MutableMapping[str, Any]:
        nonlocal received
        message = await receive()
        if message["type"] == "http.request":
            received += len(message.get("body", b""))
            if received > limit:
                raise _BodyTooLarge
        return message

    return wrapped


async def _bounded_form(
    request: Request, limit: int, *, max_files: int, max_fields: int, content_types: set[str]
) -> Any:
    """Parse a form whose whole body is capped at ``limit`` bytes while it is received.

    A declared Content-Length above the cap is refused before reading anything; the
    wrapped receive channel enforces the same cap on the actual bytes, so a missing
    or false header cannot reach parser spooling beyond it.
    """
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type not in content_types:
        raise UploadRejected("unsupported_media_type")
    declared = request.headers.get("content-length")
    if declared is not None:
        if not declared.isdigit():
            raise UploadRejected("invalid_form")
        if int(declared) > limit:
            raise UploadRejected("request_too_large")
    bounded = Request(request.scope, _bounded_receive(request.receive, limit))
    try:
        return await bounded.form(
            max_files=max_files, max_fields=max_fields, max_part_size=MAX_FORM_REQUEST_BYTES
        )
    except _BodyTooLarge:
        raise UploadRejected("request_too_large") from None
    except (HTTPException, MultiPartException):
        # Starlette's parser errors carry parser text; replace them with a generic code.
        raise UploadRejected("invalid_form") from None


def _single_item(form: Any, name: str) -> Any:
    items = form.multi_items()
    if len(items) != 1 or items[0][0] != name:
        return None
    return items[0][1]


# ── Application ─────────────────────────────────────────────────────────


def create_app(
    settings: Settings | None = None,
    *,
    embeddings: Embeddings | None = None,
    generator: StructuredGenerator | None = None,
) -> FastAPI:
    resolved = settings if settings is not None else load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        reasons = degraded_reasons(resolved)
        active_embeddings, active_generator = _build_providers(
            resolved, embeddings, generator, reasons
        )
        root = await run_in_threadpool(ingestion.open_data_root, resolved, active_embeddings)
        app.state.settings = resolved
        app.state.startup_reasons = reasons
        app.state.root = root
        # Compiled once per process, with the lock-holding snapshot function injected.
        app.state.graph = (
            build_answer_graph(partial(ingestion.retrieve_snapshot, root), active_generator)
            if active_generator is not None and active_embeddings is not None
            else None
        )
        # Log key names and booleans only, never values or paths.
        logger.info(
            "startup openai_api_key_set=%s degraded_reasons=%s",
            resolved.openai_api_key_set,
            [*reasons, *root.degraded],
        )
        yield

    app = FastAPI(title="SlideRAG Mini", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
    templates = Jinja2Templates(
        env=Environment(loader=FileSystemLoader(APP_DIR / "templates"), autoescape=True)
    )

    def current_reasons(request: Request) -> list[str]:
        """Startup reasons plus runtime degradation (for example failed cleanup)."""
        state = request.app.state
        reasons: list[str] = list(state.startup_reasons)
        reasons += [r for r in state.root.degraded if r not in reasons]
        if not reasons and state.graph is None:
            reasons.append("provider_client_unavailable")
        return reasons

    def page(request: Request, status_code: int = 200, **context: Any) -> HTMLResponse:
        root: DataRoot = request.app.state.root
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "documents": root.list_documents(),
                "degraded": current_reasons(request),
                "max_question_chars": MAX_QUESTION_CHARS,
                **context,
            },
            status_code=status_code,
        )

    def error(request: Request, status_code: int, text: str) -> HTMLResponse:
        return page(request, status_code, message={"kind": "error", "text": text})

    @app.get("/health")
    async def health(request: Request) -> JSONResponse:
        reasons = current_reasons(request)
        key_set: bool = request.app.state.settings.openai_api_key_set
        if reasons:
            return JSONResponse(
                status_code=503,
                content={"status": "degraded", "reasons": reasons, "openai_api_key_set": key_set},
            )
        return JSONResponse(
            status_code=200, content={"status": "ok", "openai_api_key_set": key_set}
        )

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return page(request)

    @app.post("/upload", response_class=HTMLResponse)
    async def upload(request: Request) -> HTMLResponse:
        if current_reasons(request):
            return error(request, 503, MSG_DEGRADED)
        root: DataRoot = request.app.state.root
        try:
            with ingestion.exclusive(root):  # EXEC-01 § 4 step 1: lock before the body
                form = await _bounded_form(
                    request,
                    MAX_REQUEST_BYTES,
                    max_files=1,
                    max_fields=0,
                    content_types={"multipart/form-data"},
                )
                try:
                    upload_file = _single_item(form, "file")
                    if not isinstance(upload_file, UploadFile):
                        raise UploadRejected("invalid_form")
                    staged = await run_in_threadpool(
                        ingestion.stage_upload, upload_file.file, root.settings
                    )
                    filename = upload_file.filename or ""
                finally:
                    await form.close()
                try:
                    outcome = await run_in_threadpool(
                        ingestion.ingest_staged, root, staged, filename
                    )
                finally:
                    staged.discard()
        except BusyError:
            return error(request, 409, MSG_BUSY)
        except DegradedError:
            return error(request, 503, MSG_DEGRADED)
        except UploadRejected as exc:
            logger.info("upload rejected code=%s", exc.code)
            return error(request, _KIND_STATUS[exc.kind], exc.message)
        except ProviderError as exc:
            logger.warning("upload provider error: %s", exc)
            if root.degraded:  # rollback failed: degraded (503) outranks the provider 502
                return error(request, 503, MSG_DEGRADED)
            return error(request, 502, MSG_PROVIDER)
        except Exception as exc:  # storage failure: rolled back, or the root is now degraded
            logger.error("upload failed: %s", type(exc).__name__)
            if root.degraded:
                return error(request, 503, MSG_DEGRADED)
            return error(request, 500, MSG_INGEST_FAILED)
        record = outcome.record
        if outcome.duplicate:
            text = f"Already indexed as {record.source_file}; nothing was added."
        else:
            text = (
                f"Indexed {record.source_file}: {record.indexed_slide_count} of "
                f"{record.slide_count} slides with text, {record.chunk_count} chunks."
            )
        return page(request, message={"kind": "ok", "text": text})

    @app.post("/ask", response_class=HTMLResponse)
    async def ask(request: Request) -> HTMLResponse:
        if current_reasons(request):
            return error(request, 503, MSG_DEGRADED)
        try:
            form = await _bounded_form(
                request,
                MAX_FORM_REQUEST_BYTES,
                max_files=0,
                max_fields=1,
                content_types={"application/x-www-form-urlencoded", "multipart/form-data"},
            )
        except UploadRejected as exc:
            status = _KIND_STATUS[exc.kind]
            return error(request, status, MSG_FORM if status != 413 else MSG_QUESTION)
        raw = _single_item(form, "question")
        await form.close()
        question = raw.strip() if isinstance(raw, str) else ""
        if not 1 <= len(question) <= MAX_QUESTION_CHARS:
            return error(request, 400, MSG_QUESTION)
        try:
            result = await run_in_threadpool(answer_question, request.app.state.graph, question)
        except BusyError:
            return error(request, 409, MSG_BUSY)
        except DegradedError:
            return error(request, 503, MSG_DEGRADED)
        except ProviderError as exc:
            logger.warning("ask provider error: %s", exc)
            return error(request, 502, MSG_PROVIDER)
        return page(request, question=question, result=result)

    return app
