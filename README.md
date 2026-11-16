# SlideRAG Mini

A private, single-user demo of a presentation-grounded assistant for a fictional
telecom operations team. You upload a synthetic `.pptx` deck and ask a question.
The answer names the file and slide it came from, or it explicitly refuses when
the indexed slides do not support an answer.

It is an AI Engineer portfolio project: one FastAPI container, local persistent
Chroma, OpenAI embeddings and chat, and a minimal LangGraph answer-or-refuse
decision. It is **not** a production service and it is **not** meant for real
operational documents.

> Status: the offline application path is implemented and tested with mocked
> providers. Live provider behaviour, the EC2 deployment and the demo below are
> **to be verified** (see [Verification status](#verification-status)).

## Architecture

| Module | Responsibility |
|---|---|
| `app/main.py` | Routes, startup (lifespan), `/health`, Jinja2 page, public error mapping |
| `app/ingestion.py` | Upload bounds, SHA-256, PPTX/ZIP validation, slide text extraction, chunking, manifest, coordination lock |
| `app/rag.py` | Embeddings, Chroma, retrieval, the compiled graph `retrieve → evidence? → generate_answer \| no_evidence`, citation checks |
| `app/config.py` | The only environment reader: settings, limits, data paths, index configuration |

Source labels are built from retrieved metadata (`source_file`, `slide_number`,
`file_sha256`, `chunk_index`), never from model text. The page shows only the
citations that match a retrieved slide; with no valid citation it shows the
fallback.

All data lives under one `DATA_DIR`: `uploads/`, `chroma/`, `manifest.json` and a
`tmp/` staging directory. One process (one Uvicorn worker) owns one data root.

## Setup and local run

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                    # locked dependencies
uv run python demo/generate_pptx.py        # writes demo/5G_RAN_Operations_Demo.pptx (gitignored)

# Export OPENAI_API_KEY in your shell from a private place (not a file in this
# checkout). The app does not load .env files.
DATA_DIR="$PWD/data" uv run uvicorn --factory app.main:create_app \
  --host 127.0.0.1 --port 8000 --workers 1
```

Open <http://127.0.0.1:8000>. Without a key, the page renders but `/health`
reports `degraded` and upload/ask return 503. `data/` is gitignored. Use a
dedicated directory, never a shared or untrusted one.

### Configuration

The keys and their meaning are documented in [`.env.example`](.env.example):
`OPENAI_API_KEY`, `LLM_MODEL`, `EMBEDDING_MODEL`, `LLM_BASE_URL`,
`EMBEDDING_BASE_URL` and `DATA_DIR`. Never commit real values. Endpoints must be
credential-free `https` URLs. Changing the embedding model or endpoint changes
the index configuration: existing data is then refused (503), not migrated.

## Synthetic data and the API boundary

The demo deck is invented. Every slide says so, and [`demo/README.md`](demo/README.md)
lists its facts and the five acceptance questions. Uploaded slide text and
questions are sent to the configured embedding and chat endpoints, so only
synthetic content may be uploaded. Slide text is treated as untrusted data. The
grounding policy is a separate system message, but that does not prove that a
real model resists prompt injection.

## Limits

| Boundary | Limit / behaviour |
|---|---|
| Upload file | 10 MiB (10,485,760 bytes); one `.pptx` in the `file` field, no other fields |
| Whole upload request | 10 MiB + 64 KiB, enforced while receiving, before parsing |
| PPTX archive | ≤ 100 MiB declared uncompressed, ≤ 2,000 members, ≤ 200 slides; no traversal, absolute or duplicate member names |
| Extracted text | ≤ 1,000,000 characters; text boxes and table cells only (no notes, images or OCR) |
| Chunks | Within one slide, ~1,000 characters with 150 overlap, hard cap 1,000 |
| Question | 1–1,000 characters after trimming |
| Display filename | Sanitised, ≤ 120 characters |
| Concurrency | One worker, one user. A process lock covers an upload and each retrieval snapshot; a competing request gets **409** instead of waiting |

Consequences to know before the demo:

- An upload holds the lock from the start of its request body until indexing
  finishes. A stalled or slow client keeps it until the client disconnects, and
  every other upload and question gets 409 meanwhile.
- A question holds the lock while its query is embedded. Generation runs after
  the lock is released.
- Each provider call has a 30 s timeout and up to 2 retries (3 attempts), so a
  single call can take about 90 s or more in the worst case. A question makes
  two calls (query embedding, then chat). An upload makes one embedding call per
  100 chunks.

## Status codes and health

| Status | Meaning |
|---|---|
| 200 | Page, answer, refusal (fallback) or successful/duplicate upload |
| 400 | Malformed form, invalid PPTX, no extractable text, bad question length |
| 409 | Busy: another upload or retrieval holds the lock; retry |
| 413 | Upload, archive or text over a limit, or a question form over its 16 KiB request cap |
| 415 | Not a `.pptx` file, an upload that is not `multipart/form-data`, or a question form with another content type |
| 500 | Upload storage failure that was rolled back; retry |
| 502 | The model provider failed or timed out (not a refusal) |
| 503 | Degraded: missing key, provider client unusable, or inconsistent/unavailable data root |

`GET /health` returns 200 `{"status": "ok", ...}` or 503 with
`{"status": "degraded", "reasons": [...]}`. Reasons are codes only, never paths
or secrets. [`docs/deployment.md`](docs/deployment.md#degraded-reasons) explains each
code and the operator action. Error pages never echo uploaded bytes or request
bodies.

## Recovery, rollback and backups

- **Inconsistent or mismatched data is preserved, never repaired automatically.**
  The app refuses to serve it (503) and deletes nothing except its own abandoned
  temporary files.
- **Fresh-root recovery:** stop the container and keep the old root untouched.
  Start with a new, empty data root, then re-upload the deck. There is no
  automatic migration, collection switching or reindex.
- **Image rollback:** run the previous image tag against a data root that the
  image's index configuration accepts. If the configuration differs, the app
  refuses the root (503) and you use a fresh root instead.
- **An EBS volume is not a backup.** Snapshots or copies of a stopped root are
  the operator's responsibility.

The EC2 runbook in [`docs/deployment.md`](docs/deployment.md) has the exact steps.

## Security notes

- One non-root container (uid 10001). The port is published on `127.0.0.1`
  only, and access is through an SSH tunnel. No public endpoint, HTTPS or
  login (it is a private demo).
- Secrets come only from the environment, read once in `app/config.py`. They are
  never baked into the image or logged.
- ChromaDB 1.5.9 has unpatched advisories. Their mitigation and residual risk
  are in [`docs/security/chromadb-advisories.md`](docs/security/chromadb-advisories.md).
  Re-check them before every deployment.

## Tests

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -m "not integration"          # offline: fakes, temp roots, network blocked
uv run pytest -m integration --run-live     # live: needs --run-live AND a real OPENAI_API_KEY
```

Offline tests prove the application contract against fakes, not real model
behaviour. Live tests are skipped unless both opt-ins are present.

## Demo script (3–5 minutes, to be rehearsed)

Run it against the deployed container through the SSH tunnel, or locally.

1. **Upload** `5G_RAN_Operations_Demo.pptx`. Expect "Indexed …: 10 of 10 slides …"
   and the document in the list.
2. **Factual:** "What was the peak latency during INC-042?" Expect 46 ms from
   slide 4.
3. **Factual:** "What PRB utilization was observed during congestion?" Expect 92%
   from slide 5.
4. **Synthesis:** "Which conditions contributed to the latency increase?" Expect
   evidence from slides 4, 5 and 7. Check that the answer and sources agree.
5. **Unsupported:** "What is the real current outage status of the operator's
   nationwide network?" Expect the fallback, with no sources.
6. **Recreate the container** (`docker rm -f` and run again, see the runbook).
   The document list survives.
7. **Ask again:** repeat question 2 and get the same slide reference.
8. **Duplicate upload:** upload the same deck again. Expect "Already indexed …;
   nothing was added." The chunk count is unchanged.

The questions are a demonstration, not a measured accuracy or refusal rate.

## Verification status

| Area | Status |
|---|---|
| Offline unit/route tests (ruff, pytest without integration) | Passing locally at the reviewed revision |
| Live embedding/structured output, live acceptance questions | To be verified |
| Local container smoke check without a key (degraded path) | Documented in the runbook |
| EC2 `ec2-private-access`, `ec2-recreation`, `mount-boot-safety`, memory sampling, QG-09 | To be verified |
