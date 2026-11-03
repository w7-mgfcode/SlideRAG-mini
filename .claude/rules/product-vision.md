# Product Vision Alignment

Before creating issues, planning features, or starting work, check that the proposed work aligns with SlideRAG Mini's core identity. The source of truth is `docs/.prepare/execution-plan.md` (Option C, owner-approved direction on 2026-11-03; decision-log D-16…D-21). When this file and that plan conflict, the plan wins. The original and revised brainstorm plans are historical inputs, not competing execution instructions.

## What SlideRAG Mini Is

A Python-based, presentation-grounded knowledge assistant for a fictional telecommunications operations team. A reviewer uploads a synthetic 5G operations presentation (`.pptx`), asks a technical question, inspects slide-level source references, recreates the container, and continues querying the same indexed knowledge base. The demonstration also includes unsupported-question refusal and duplicate upload without index growth.

It is an AI Engineer portfolio project with an **8-hour implementation timebox**, not a proven completion estimate. Preparation is tracked separately. It demonstrates five capabilities: Python application engineering, document processing, vector retrieval, LLM orchestration, and AWS deployment. The demonstration is a working application that answers from specific slides, identifies its evidence, and declines when that evidence is insufficient.

## Core Principles

1. **Portfolio-grade inside an 8-hour timebox.** M1 stack proof 60 min, M2 complete local path 150 min, M3 failure/evidence checks 105 min, M4 deploy/demo 75 min, workflow 30 min, reserve 60 min. Track preparation/bootstrap/AWS provisioning separately. Cut cosmetic polish; migration, deletion UI, extensive telemetry, and extra decks are already deferred. Report overruns and re-estimate; never sacrifice acceptance gates to claim completion.
2. **One application, one container.** FastAPI + Uvicorn + Jinja2 + plain CSS in a single Docker image on one EC2 `t3.small` (eu-central-1) with an EBS data volume bind-mounted at `/data`. No managed services beyond the OpenAI API.
3. **Flat modules, no framework-in-a-framework.** `app/main.py` (routes, startup, `/health`), `app/ingestion.py` (validation, SHA-256, extraction, chunking, idempotent indexing), `app/rag.py` (embeddings, Chroma, retrieval, LangGraph, source validation), `app/config.py` (settings and secrets). Avoid a generic service framework, repository layer, abstract provider factory, or event bus.
4. **Right tool per workflow.** LangChain handles document and retrieval integration. LangGraph manages only the explicit answer-or-refuse decision (`retrieve → evidence_available? → generate_answer | no_evidence`). Ordinary Python functions handle ingestion and validation.
5. **Evidence-grounded answers.** Every retrieved chunk carries `source_file`, `slide_number`, `file_sha256`, `chunk_index`. Source labels are built from that metadata, never invented by the LLM. Any model-cited identifier is validated against the retrieved set before display.
6. **Explicit insufficient-evidence fallback.** Empty retrieval returns a deterministic fallback. Generation may also refuse. Use C1 validated cited-only sources and native structured output. Distances are not confidence; tune an optional threshold on separate calibration probes, never the five acceptance questions. Valid citations prove provenance, not factual correctness.
7. **Persistence survives container recreation.** Chroma, uploads, and the manifest share DATA_DIR (`/data` on EBS in the container). Coordinate ingestion and retrieval snapshots so partial writes are not queryable. Compare the complete index configuration; preserve and refuse inconsistent/mismatched state. Recovery uses an explicit clean root and re-upload, not automatic migration or broad deletion.
8. **Synthetic data only.** Every demo slide identifies itself as synthetic. Only synthetic text is ever sent to external APIs.

## Scope Lock (from the plan)

| Feature | Priority | Decision |
|---------|----------|----------|
| PPTX upload and validation | MUST HAVE | One file at a time |
| Slide-level text extraction | MUST HAVE | Preserve filename and slide number |
| Chunking and embeddings | MUST HAVE | External API |
| Persistent vector search | MUST HAVE | Local Chroma |
| Question-answer workflow | MUST HAVE | Minimal LangGraph |
| Evidence-grounded answers | MUST HAVE | Source-verified citations |
| Insufficient-evidence fallback | MUST HAVE | Explicit decision path |
| Simple document list | MUST HAVE | Persisted index metadata |
| FastAPI web interface | MUST HAVE | Jinja2 + HTML/CSS |
| Docker and AWS deployment | MUST HAVE | One container |
| Basic tests and README | MUST HAVE | Small, focused suite |
| Document deletion and reindexing UI | LATER | Not required for interview |
| User authentication and multi-tenancy | LATER | Private demo only |
| Conversation history and advanced evaluation | LATER | No requirement |
| OCR and visual slide interpretation | EXCLUDED | Text extraction only |
| Multiple agents and autonomous tool use | EXCLUDED | Unnecessary |
| Kubernetes, Redis, Celery, PostgreSQL | EXCLUDED | Overengineering |
| React, Next.js and frontend build tooling | EXCLUDED | No material MVP benefit |

**Scope freeze:** No additional feature should enter the first release unless it fixes a correctness, security, or demonstration-blocking problem.

## What SlideRAG Mini Is Not (Negative Guardrails)

Identity-level constraints. If a feature pushes the repo toward any of these, flag it.

- **Not an authenticated or multi-tenant product.** Private demo reached through an SSH tunnel. Auth and multi-tenancy are LATER.
- **Not a multi-agent system.** No autonomous tool use, no second model, no self-reflection loop, no reranker.
- **Not a visual-understanding system.** Text extraction only. No OCR, no image interpretation.
- **Not a distributed system.** No Kubernetes, Redis, Celery, PostgreSQL, message queues, or multiple workers.
- **Not a JavaScript frontend.** No React, Next.js, bundlers, or component libraries. Jinja2 templates and one plain CSS file.
- **Not an evaluation platform.** Five known questions in pytest plus manual grounding checks. No evaluation framework for five examples.
- **Not production-hardened for public traffic.** One worker, one upload at a time, 10 MB cap. Document these limits rather than hide them.

## Out of Scope (Hard No)

Do not propose or build:
- A public HTTPS endpoint, domain, reverse proxy, or login flow for the demo
- Multiple application containers, Compose stacks with databases, or orchestration
- Replacing FastAPI, LangChain, LangGraph, or Chroma with alternatives
- A second LLM vendor, local model serving, or GPU dependencies
- A conversation memory, chat history, or session store
- Any feature not in the MUST HAVE tier before the definition of done passes on EC2

## The Litmus Test

When evaluating an idea, ask:
1. Does it fit one of the four flat modules without adding a layer?
2. Is it MUST HAVE in the scope lock, or does it fix a correctness, security, or demonstration-blocking problem?
3. Does it keep source labels derived from retrieved metadata and preserve the no-evidence fallback?
4. Does it keep application data under the configured DATA_DIR (`/data` in the container) so it survives container recreation?
5. Does it run in one container on a `t3.small` with the bind mount?
6. Does it fit the remaining hour budget, and does it sit ahead of the cut order?
7. Does it pass `ruff` + `pytest` and the relevant QG-01 through QG-09 gate?

If any answer is "no" or "unclear", flag the concern before proceeding.

## When Ideas Don't Align

- Don't silently proceed. Raise the concern directly.
- Cite the specific principle or scope-lock row it conflicts with.
- Suggest an alternative that fits the flat architecture and the hour budget.
- If the user wants to proceed despite the concern: go ahead, but note the vision tension in the issue or PR description.

## When Ideas Are Ambiguous

- Ask which module owns the work (`main`, `ingestion`, `rag`, `config`).
- Ask which scope-lock tier it belongs to.
- Check whether it adds an external service or dependency.
- Default to deferring rather than guessing.
