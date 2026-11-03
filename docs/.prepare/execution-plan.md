# SlideRAG Mini — Approved Option C Execution Plan

| Field | Value |
|---|---|
| Document ID | EXEC-01 |
| Revision | r1 |
| Date | 2026-11-03 |
| Status | Approved direction; implementation not started |
| Authority | Owner approved the preceding architectural recommendation in conversation: “APPROVE YOUR SUPERVIZED VISION” |
| Approval record | [decision-log.md § 4](decision-log.md#4-owner-approval-record), D-16…D-21 |
| Baseline | docs-baseline-r3 |

## 1. Authority and boundaries

This is the governing execution plan. It records Option C from the review: a fixed-configuration MVP with explicit recovery. It replaces conflicting implementation, lifecycle, scheduling, and approval-gate proposals in the original and revised plans. Those documents remain historical evidence; their unselected alternatives are not requirements.

Preserve the original product, synthetic deck, five acceptance questions, and QG-01…QG-09. Original plan § 9 supplies the deck contents; the current test rule supplies the acceptance questions. Do not infer approval of every earlier proposal or retrospective process decision.

The approval turn records the direction and aligns planning/policy files. It does not execute historical missions, implement application code, commit, create GitHub objects, publish, or deploy. Previously recorded public-repository authorization remains recorded separately. Approval of a plan is not evidence that its operational prerequisites or acceptance tests passed.

## 2. Product and scope

- Build a private, single-user presentation-grounded assistant for a fictional telecom team, using synthetic data only.
- Demonstrate Python engineering, PPTX processing, retrieval, minimal LangGraph orchestration, and AWS deployment.
- Done means: browser upload of the ten-slide synthetic deck; supported answers with validated filename/slide sources; unsupported-question refusal; container recreation on EC2; successful query and duplicate upload against the surviving index.
- Keep Python 3.12, FastAPI/Uvicorn, Jinja2/plain CSS, python-pptx, LangChain, LangGraph, local persistent Chroma, OpenAI embeddings/chat, Docker, and EC2 t3.small in eu-central-1 with an EBS data volume.
- Defaults remain `text-embedding-3-small` and `gpt-4.1-mini`. Public documentation supports them; project-account access and pinned-package compatibility must be demonstrated at M1.
- Exclude OCR, visual interpretation, auth, multi-tenancy, conversation history, autonomous tools, extra services, reranking, a JS frontend, and a second model provider.
- Defer deletion/reindex UI, automatic configuration migration, stale-collection management, broad orphan deletion, extensive telemetry, extra decks, and cosmetic polish.

## 3. Architecture and storage

| Component | Responsibility |
|---|---|
| `app/main.py` | Routes, lifespan, health, templates, public error mapping |
| `app/ingestion.py` | Upload validation, hashing, extraction, chunking, manifest, ingest/retrieval coordination |
| `app/rag.py` | Embeddings, Chroma operations, retrieval, compiled graph, structured generation, citation checks |
| `app/config.py` | Environment settings, constants, data-root resolution, index configuration |

Use plain functions and injected clients/functions. Do not add a repository layer, provider factory, event bus, or framework around these modules. Keep dependencies one-way; pass a lock or coordinated retrieval function into the graph rather than introducing circular imports.

One process/worker owns one data root. `DATA_DIR` is the only storage-root setting: `/data` in the container, an explicit local path for development, a temporary directory in tests. Derive `uploads/`, `chroma/`, and `manifest.json` from it; do not expose independent `CHROMA_PATH`. All application-owned data paths must remain contained under the resolved root. Parser temporary storage is bounded and cleaned up, not durable application state.

Persist one index configuration: schema version, embedding model, non-secret endpoint identity, embedding dimensions, explicit cosine distance, and extractor/chunking version. Do not store credentials in it. One active collection belongs to that configuration. A display slug is not a sufficient identity check.

Compare the full configuration at startup. On a mismatch, preserve the data and refuse uploads/queries with 503. Recovery is operator-controlled: preserve the old root, select a clean root, and re-upload. No automatic migration, collection switching, or stale-document state in v0.1.

## 4. Ingestion, consistency, and recovery

1. Acquire a process-level coordination lock for ingestion. A competing upload or retrieval snapshot returns 409 busy; use lock acquisition, not an unlocked boolean check.
2. Bound the request before multipart parsing; copy and hash the validated file into a temporary file under the data root.
3. Validate PPTX/ZIP limits before extraction. Reject empty extracted text. Extract text boxes/table cells, including supported group shapes, preserving slide number. Exclude notes and visual-only content.
4. If the file hash is already complete in a healthy index, return the existing record without embedding again.
5. Split within slide boundaries, initially about 1,000 characters with 150 overlap. Preserve `source_file`, `slide_number`, `file_sha256`, and `chunk_index`; use deterministic chunk IDs.
6. Embed/upsert, rename the temporary upload, then atomically replace the manifest (same-directory temporary file, flush/fsync, replace). Record completed documents only, with counts and configuration identity.
7. On a handled failure, remove chunks/files attributable to that attempt and permit safe retry. If cleanup cannot establish consistency, enter degraded mode; do not serve uncertain data.
8. Release the lock. Retrieval holds the same lock while obtaining its consistent evidence snapshot; generation may proceed after the snapshot is captured.

Startup may initialize an entirely empty root. Missing/invalid/unknown-version metadata alongside existing data is inconsistent state, not an empty database. Detect missing chunks for completed records and unexplained chunks/uploads; preserve durable data and enter degraded mode rather than silently deleting it. Temporary files known to be abandoned may be removed. Document manual rebuild as the recovery route for interrupted or inconsistent state.

This is deliberately not a cross-store transaction system. Its promise is: no partially committed upload becomes queryable; no uncertain state is silently destroyed; failures remain visible and recoverable by re-upload into a clean root.

## 5. Retrieval, refusal, and citations

- Retrieve up to five chunks with distances. In `retrieve`, write evidence state; the conditional edge only chooses the next node. Compile `retrieve → evidence? → generate_answer | no_evidence` once with injected dependencies.
- Empty retrieval refuses. An optional distance threshold refuses when `best_distance > T`; equality passes. `T=None` disables that layer explicitly.
- Calibrate using separate supported and near-domain unsupported probes. Do not choose T from the five acceptance-question distances. Record configuration, probes, distances, and limitations. Bind calibration to the exact index configuration; never reuse it after a mismatch. Keep T as a configuration constant rather than adding another environment setting.
- If probe distances overlap, leave T disabled and state that model judgment supplies the non-empty-evidence refusal decision. Five acceptance questions are a demonstration, not a measured refusal rate.
- Use native schema-constrained output `{answer, cited, insufficient}` through the pinned OpenAI/LangChain integration. Verify refusals, incomplete responses, and parsing behavior in M1; do not silently treat JSON mode as equivalent.
- Keep system policy separate from question/document text. Document instructions are untrusted data; delimiters and schema validation do not prove resistance to prompt injection.
- Build request-local `S1…Sk` labels from retrieved metadata. Validate model citations against that map; deduplicate by file hash/slide. Choose C1: display only validated cited sources; no valid citation means fallback. Strip inline citation markers and show the validated source list separately.
- A citation proves provenance, not semantic support. Manually assess factual support and citation coverage for synthesis/troubleshooting answers; include a live instruction-like document-text probe.
- Use the exact fallback: “I couldn't find sufficient information in the uploaded presentations to answer that question. Please upload a relevant document or ask about the indexed material.”
- Keep explicit fallback reasons: empty retrieval, above threshold, model insufficient, invalid model output, no valid citation. Malformed output is fail-closed but cannot count as a successful unsupported-question evaluation.
- Provider timeout/error is 502, not insufficient evidence. Missing credentials or inconsistent data returns degraded health and 503 for upload/ask. External calls have finite timeouts/retries; batch embeddings within verified provider limits.

## 6. Upload and deployment boundaries

| Boundary | Limit / behavior |
|---|---|
| File | 10 MiB = 10,485,760 bytes |
| Entire multipart request | File limit + 64 KiB, enforced while receiving before parser spooling; do not add the file limit twice |
| Form shape | One file and only explicitly needed fields; reject unsupported form shapes |
| ZIP | At most 100 MiB declared uncompressed size, 2,000 members, 200 slides; reject malformed structures, traversal/absolute paths, duplicate member names |
| Extracted content | At most 1,000,000 characters; this is a size bound, not a promised latency |
| Display filename / question | At most 120 characters / 1–1,000 stripped characters |
| Rendering | Jinja autoescape; no `safe` on uploaded/model text; no raw request/error echoes |

Keep finite resource limits through parsing, extraction, embedding, and generation. Validate parser limits against pinned dependencies rather than assuming that post-spool file recounting is an early request cap. Host allow-list and supported form handling are routine boundary decisions, not separate owner approval gates.

Deploy one non-root container with loopback-only port publication, SSH access restricted to the operator, secrets outside the checkout/image, `unless-stopped`, and a verified EBS mount at the host data path. Preserve the required mount dependency across boot; a failed mount must not redirect writes to the root disk.

Separate one-time volume initialization from repeatable deployment. Verify volume identity and absence of a filesystem explicitly before formatting; a failed probe is not permission to format. Preserve existing secret files and fstab entries. Never copy the historical `blkid || mkfs` sequence into the live runbook.

Verify container recreation and duplicate upload. Test reboot/mount dependency if claiming boot recovery. Observe memory over the operation and report sampled maxima honestly; one `docker stats --no-stream` observation is not peak usage. An EBS volume is not a backup. Document image rollback and the need to preserve/restore a compatible data root.

## 7. Verification and acceptance checklist

No item below is complete merely because its specification exists.

- [ ] QG-01/02: known deck text, correct slide numbering, and required metadata survive extraction/chunking.
- [ ] QG-03: duplicate upload adds no chunks and makes no new embedding call.
- [ ] QG-04: a fresh process opens the same directory and retrieves indexed content; do not rely on clearing private client caches.
- [ ] QG-05: the live fixed acceptance questions retrieve the expected slides; inspect chunk crowding before considering retrieval changes.
- [ ] QG-06: displayed sources are a subset of retrieved metadata, including invalid/empty citation cases.
- [ ] QG-07: empty, threshold, model-insufficient, invalid-output, and no-citation paths behave deterministically; the live unsupported question passes only through threshold/model-insufficient refusal.
- [ ] QG-08: malformed/oversized/traversal/expansion inputs fail safely; HTML stays escaped; instruction-like content is assessed without claiming a mocked test proves model safety.
- [ ] Consistency: concurrent retrieval cannot observe partial ingest; handled failure can retry; incomplete cleanup degrades safely.
- [ ] Recovery: missing/corrupt manifest, configuration mismatch, and completed records with missing chunks preserve data and block unsafe operations.
- [ ] Routes: happy/error paths, busy response, degraded state, and upstream failure mapping.
- [ ] Live semantic check: synthesis/troubleshooting claims and their sources agree; separate calibration probes are recorded.
- [ ] QG-09: EC2 container recreation retains document/counts, answers again, refuses unsupported questions, and deduplicates re-upload.
- [ ] Operational claims: mount/boot behavior checked; memory/latency observations recorded; limitations and recovery documented.

Use `tests/test_ingestion.py`, `tests/test_rag.py`, `tests/test_main.py`, and shared fixtures. Inject app-owned functions/clients; do not patch library internals. Offline tests should stay under 30 seconds. Live tests are integration-marked and skip without credentials. Run ruff check, ruff format check, then offline pytest; record live/manual evidence separately. No test-per-helper quota or tests mirroring constants/documentation.

## 8. Milestones and honest accounting

Preparation is outside the implementation clock and must be reported separately: prior documentation/review, this alignment, initial GitHub/bootstrap work, credential/toolchain readiness, and AWS host provisioning. Actual preparation duration is unknown until recorded; the earlier AWS allowance of 35 minutes is an estimate, not an observed cost. Do not move application implementation or verification into “preparation” to claim an eight-hour build.

| Stage | Timebox | Dependency | Observable exit |
|---|---:|---|---|
| M1 — Stack proof | 60 min | Preparation prerequisites | Locked Python 3.12 dependencies; real embedding/structured output; fresh-process Chroma persistence; basic local container |
| M2 — Complete local path | 150 min | M1 | Browser upload → extracted/indexed slides → supported answer with sources; duplicate upload stable |
| M3 — Failure and evidence checks | 105 min | M2 | Required consistency/recovery/error tests; independent calibration probes; fixed live questions and semantic review |
| M4 — Deployment and demonstration | 75 min | M3 and prepared host | EC2 recreation proof, mount/boot checks, observations, README, rehearsed 3–5 minute demo |
| Build workflow allowance | 30 min | Across M1–M4 | Outcome-sized branches/PRs and concise evidence |
| Contingency | 60 min | Reserved | Corrections, not extra features |
| Total implementation timebox | **480 min** | | **Planning allocation, not a validated forecast** |

If M1 or the complete local path misses its timebox, report the measured variance and re-estimate. Do not weaken acceptance gates or silently overrun. Cosmetic polish goes first; migration/extra decks/telemetry are already deferred, so they cannot be counted again as savings. A larger budget requires an explicit owner decision.

## 9. Workflow and next actions

Keep the recorded public-repository and milestone → umbrella → epic → sub-issue preference. Use one outcome-sized implementation sub-issue/PR per milestone where practical; minor steps are checkboxes, not separate PRs. Include minimal offline CI in the M1 outcome if executing the recorded GitHub plan, using `chore(ci)` under the existing commit grammar. No separate CI epic, deployment automation, or additional agent framework.

The active working set is this plan, the decision log, and this acceptance checklist. Core context/readiness are pointers and state summaries. Historical review scores, alternatives, and retrospective delegation choices do not add implementation gates.

Before publishing, resolve references to ignored handoffs/delegation files. Default to self-contained public summaries and preserve local originals; do not claim ignored, uncommitted files are in Git history. Publishing raw provenance remains a separate optional choice.

Next actions after this planning alignment:
1. Verify operational prerequisites and account for preparation separately; use existing authorization without repeating settled preference questions.
2. Execute M1's real stack proof before expanding infrastructure or test variants.
3. Build the entire local upload → answer → persistent reopen path, then validate its failure behavior before EC2 deployment.

## 10. Evidence and limits

See [source-register.md](source-register.md#option-c-review-and-approval-added-in-r3) for the owner approval, repository observations, and official documentation checked during the review. None establishes actual runtime performance, account access, deployed behavior, or statistical answer quality. This plan transcribes the approved recommendation; it is not an independently tested implementation.
