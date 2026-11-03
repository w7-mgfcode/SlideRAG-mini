# Core Context — SlideRAG Mini

| Field | Value |
|---|---|
| Document ID | PREP-02 |
| Revision | r3 |
| Status | Current summary of approved Option C direction |
| Last updated | 2026-11-03 |
| Baseline | docs-baseline-r3; source-register.md r3 |
| Authority | [execution-plan.md](execution-plan.md), EXEC-01 r1 |
| Approval | [decision-log.md § 4](decision-log.md#4-owner-approval-record), D-16…D-21 |

## Product and definition of done

- **Requirement:** private, single-user Python assistant for synthetic telecom PPTX material; intended as an AI Engineer portfolio demonstration.
- **Purpose:** show Python engineering, document processing, retrieval, LLM orchestration, and AWS deployment.
- **Done:** upload the synthetic ten-slide deck; answer supported questions with validated slide sources; refuse an unsupported question; recreate the EC2 container; query the surviving index; duplicate upload does not grow it.
- **Scope:** four flat modules, one process/container, server-rendered interface. No OCR, visual interpretation, auth, multi-tenancy, autonomous agents/tools, chat history, extra services, reranker, or JS frontend.

## Verified state and authorization

- **Verified local state, 2026-11-03:** unborn main, zero commits, no remote, no application/tests/dependency lock/Dockerfile/root README. Git identity is configured; HANDOFF.md's contrary statement is stale.
- Present: preparation documents, ignore files, project tooling (7 rules, 4 agents, 15 skills, 27 commands), and a newer GitHub bootstrap plan. Host Python is 3.14.4; project target remains 3.12.
- The preceding review's GitHub API check failed to connect. Local remote absence does not establish remote repository absence. Cloud/account readiness is unverified.
- The GitHub mission records prior public-repository/hierarchy authorization. It is not an instruction to execute that historical mission during this approval turn.
- The owner approved the preceding Option C recommendation with “APPROVE YOUR SUPERVIZED VISION”. The current turn records/aligns planning and policy only; no implementation, commits, external objects, publication, or deployment.
- No runtime performance, semantic-quality, recovery, or cloud acceptance result exists. Documentation approval does not complete a test.

## Approved architecture and choices

| Area | Current direction |
|---|---|
| Runtime/UI | Python 3.12, FastAPI/Uvicorn, Jinja2 and plain CSS |
| Modules | main: HTTP/startup; ingestion: document lifecycle and coordination; rag: embeddings/store/graph/generation; config: settings/constants |
| AI | OpenAI text-embedding-3-small and gpt-4.1-mini defaults; LangChain integration; minimal compiled LangGraph |
| Storage | Persistent Chroma, uploaded PPTX, manifest under DATA_DIR; derive all child paths |
| Index identity | Model, non-secret endpoint identity, dimensions, explicit cosine, extractor/chunking version, schema version |
| Recovery | Preserve mismatched/corrupt/inconsistent state and return degraded 503; explicit fresh-root rebuild/re-upload |
| Concurrency | Same process lock around ingest mutation and retrieval snapshots; competing work receives 409 busy |
| QA | Top-five retrieval, empty/optional calibrated-distance gate, model-insufficient check, native structured output, C1 cited-only validation |
| Deployment | One non-root Docker container on EC2 t3.small eu-central-1; EBS at /data, loopback port, SSH tunnel, verified boot/mount dependency |
| Workflow | Recorded public GitHub hierarchy, outcome-sized implementation issues/PRs, minimal offline CI using chore(ci) |

Configuration keys are OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL, LLM_BASE_URL, EMBEDDING_BASE_URL, DATA_DIR. No independent CHROMA_PATH. Alternative endpoint compatibility is not a v0.1 promise.

The detailed contracts and limits live only in EXEC-01. Retain the original plan's synthetic deck content and the test rule's five acceptance questions. The old full-lifecycle proposal does not supply additional mandatory features.

## Flow and trust boundaries

- Ingestion: acquire coordination lock → bound/validate/hash upload → deduplicate → extract/chunk within slides → embed/upsert → preserve upload → atomically complete manifest → release.
- Retrieval takes a consistent evidence snapshot under the same lock, then generation can run after release.
- Startup initializes a truly empty root. Existing durable data with missing/corrupt metadata is inconsistent, not empty. Preserve it; do not broadly delete or automatically migrate.
- Question answering: retrieve → evidence decision → structured answer or fallback → validate source labels against retrieved metadata → escaped HTML.
- Four boundaries: uploaded bytes; text sent to the external API; model output rendered in the browser; persistent local data.
- Citations establish provenance, not semantic truth. Distances are not confidence. Separate calibration probes choose T; acceptance questions do not. T=None explicitly disables the threshold.
- Provider error/timeout is 502; inconsistent state/missing credentials is 503; busy is 409. Evidence fallback remains a normal answer with an explicit reason.

## Budget and verification

The approved implementation timebox is 480 minutes: M1 stack proof 60; M2 complete local path 150; M3 failure/evidence checks 105; M4 deployment/demo 75; workflow 30; reserve 60. These are allocations, not measured predictions.

Preparation/review, initial GitHub/bootstrap work, credential/toolchain readiness, and AWS provisioning are accounted for separately. Their actual duration is not yet recorded. Do not relabel application work as preparation or weaken gates to claim an eight-hour result.

QG-01…QG-09 remain required. Prioritize ingest/retrieval isolation, failed-ingest retry, missing/corrupt manifest, configuration mismatch, fresh-process persistence, live semantic checks, and EC2 container recreation. Run ruff check/format check and offline pytest; live tests are marked and skipped without credentials.

## Remaining evidence, not repeated preference questions

- M1: pinned Python/library compatibility, account access, real embedding and structured output, fresh-process persistence.
- M2/M3: complete local flow, bounded parsing, consistency/recovery behavior, independent calibration, live answer/citation support.
- M4: actual AWS access/mounts, recreation and boot behavior, observed memory/latency, rehearsed demo.
- Publication: resolve ignored-provenance links; default to public summaries and preserve local originals. Raw publication is optional.
- A measured overrun requires re-estimation and, if necessary, a budget decision; no hidden scope cuts.

## Reading order and history

1. [Execution plan and acceptance checklist](execution-plan.md)
2. [Decision log](decision-log.md), [current readiness](readiness-report.md), [question dispositions](open-questions.md)
3. [Source register](source-register.md) and historical plans/review on demand

The original plan and archive remain unchanged. D-08…D-15 retain historical proposal status; their retrospective approval is not a build prerequisite. The current active plan is approved by owner direction, not by agent self-approval.
