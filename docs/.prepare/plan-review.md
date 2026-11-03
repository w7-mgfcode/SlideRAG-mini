# Plan Review — brainstorm-plan.md v1.0

> **Follow-up, 2026-11-03:** the owner approved Option C after a subsequent review found incomplete index identity, uncommitted-data visibility, destructive missing-manifest recovery, retained calibration leakage, upload-cap arithmetic, unsafe provisioning reruns, weak verification priorities, and unresolved budget/governance drift. [execution-plan.md](execution-plan.md) contains the accepted direction; [source-register.md](source-register.md#option-c-review-and-approval-added-in-r3) records the evidence. This document preserves the original r2 review and scores; findings are not implemented merely because a correction is specified.

| Field | Value |
|---|---|
| Document ID | PREP-07 |
| Title | Deep Critical Review, Recommendations, Ranking |
| Revision | r2 |
| Status | ready-for-human-review (orchestrator review independently challenged by S3, SR-36) |
| Owner | Orchestrator; § 6 independent review authored by S3; approver: repository owner |
| Last updated | 2026-11-02 |
| Evidence baseline | source-register.md r2; review target SR-01 sha256 `8a5e41cc903a` |
| Core-context revision used | r1 for §§ 1–5 (initial review); r2 for §§ 6–7 (docs-baseline-r2) |
| Dependencies | core-context.md r1, source-register.md r1, open-questions.md r1, methodology-adaptation.md r1 |
| Supersedes | — |
| Approval record | none |
| Change summary | r1: findings F-01…F-15, recommendations R-01…R-14 with initial scores and ranks. r2: S3 citation corrections; F-12 split; F-16…F-20 added; R-04 merged into R-03; R-15 added; R-09/R-10 reclassified as mandatory; revised scores; independent review (§ 6) and re-ranking (§ 7) |

Line references `L<n>` without a prefix refer to `docs/.prepare/brainstorm-plan.md` (SR-01). Rule references cite the rule file (SR-03…SR-10).

## 1. Review summary

v1.0 is a **sound, well-scoped plan**. Its architecture is proportionate and its scope lock is explicit. Its weaknesses are concentrated in **three load-bearing contracts that are named but not specified**:

- the evidence gate (QG-07)
- the citation contract (QG-06)
- ingest consistency (QG-03/QG-08)

It also has a **schedule risk** that the plan itself acknowledges. No finding is Critical: nothing makes the approach unsafe or unable to reach its definition of done. Three findings are High.

## 2. Dimension coverage

| Dimension | Findings | Notes |
|---|---|---|
| Problem clarity and intended outcomes | — | Strength S-01. DoD is concrete (L26). |
| Scope and non-goals | — | Strength S-02 (L28–49). |
| Functional requirements | F-07, F-01, F-02 | Narrative only; no IDs |
| Non-functional requirements | F-07, F-15 | Timeouts, latency, memory, and cost are unstated |
| Architectural consistency | F-02, F-04 | Diagram places validation after generation (L66); § 6 places it under `generate_answer` (L220–222) |
| Data model and lifecycle | F-03, F-04 | Manifest schema unspecified |
| Interfaces and integrations | F-08, F-13 | Routes undefined; external API claims unverified |
| Security, privacy, trust boundaries | F-05, F-11, F-10 | Mostly well covered (L411–416, SR-04). Gaps are numeric limits and enforcement mechanics. |
| Failure handling and resilience | F-03, F-15 | |
| Testing and verifiability | F-01, F-02, F-09 | |
| Deployment and rollback | F-10 | No rollback path |
| Operations and observability | F-15 | |
| F-16 *(r2, S1/S3)* | One worker does not enforce "one upload at a time" | Low | L189; PREP-08 CL-11; A-05 | A threadpooled sync handler can run two uploads at once | Double-click upload | Racing manifest writes | Process-level upload lock → 409 (PREP-08 NFR-02) | Medium (A-05 unverified) | R-03 |
| F-17 *(r2, S3)* | The evidence threshold is calibrated on the evaluation set | Medium | PREP-08 § 5.5 steps 2–3; FR-13; T-H07f | T is set from the same Q5 that the QG-07 live test runs, so layer 1 passes Q5 by construction | An improvised near-domain interview question may fall below T | False confidence in layer 1 | Held-out probe questions for calibration (OQ-21a); T-H07f asserts the layer that fired | High | R-01 |
| F-18 *(r2, S2/S3)* | The operator's browser can be used against `127.0.0.1:8000` while the tunnel is open | Low | PREP-08 § 8.A TB-1, RR-06 | Cross-site POST / DNS rebinding are not modelled in v1.0 | A third-party path exists despite the SSH-only design | Junk uploads, API spend | UV-11 Host allow-list (OQ-27), upload limits | Medium | R-05 |
| F-19 *(r2, S3; split from F-12)* | Commit preconditions and the per-issue branch/PR workflow are unbudgeted | Medium | SR-06 L14; hook L81; SR-07 L32–37; OQ-02, OQ-10 | The first commit needs an issue and a remote; four milestone branches/PRs cost time | Hook denies the first commit; ~20 min unbudgeted | Lost M1 time | Settle before M1: remote + issues, or relax `(#issue)`; budget or waive branch/PR overhead | High | R-15, R-06 |
| F-20 *(r2, S2/S3)* | The QG-04 same-process reopen test may not prove disk persistence | Low | PREP-08 § 9.H.2 T-H04 | Chroma may cache clients in-process (unverified) | QG-04 could pass vacuously | False assurance (QG-09 still catches it) | Clear the client cache or reopen in a subprocess; verify at M1 | Medium | R-12, R-11 |
| Dependencies and sequencing | F-06 | |
| Feasibility and maintainability | F-06, F-13 | |
| Decision traceability | F-12 | |
| Agent handoffs and context sufficiency | F-14 | |
| Unnecessary complexity | — | **None found in v1.0.** LangGraph use is minimal and justified (L191, L434–436). No extra services. *r2 (S3 § 1.1): the revised package adds degraded modes, about 20 log events, and a test inventory of about 50 functions. This is addressed by test tiering (OQ-25), not by new findings.* |
| Missing approvals or ownership | F-12 | Single owner; approval mechanism now defined by D-02 |
| Multi-tenancy, scaling, compliance/legal | — | **Not applicable.** Auth and multi-tenancy are LATER (L42). Scaling is explicitly deferred (L446–448). Data is synthetic (L387), and the operator name was neutralised (D-07). |

## 3. Strengths to preserve

| ID | Strength | Evidence |
|---|---|---|
| S-01 | One-sentence, demo-observable definition of done | L26 |
| S-02 | Explicit scope lock with MUST/LATER/EXCLUDED, plus a scope freeze | L28–49 |
| S-03 | Flat four-module layout, explicitly forbidding framework layers | L175–180 |
| S-04 | Provenance metadata on every chunk; labels built from metadata, not model text | L91–98 |
| S-05 | Negative-case demo (unsupported question) as a first-class requirement | L394–396 |
| S-06 | Honest boundaries: citations ≠ correctness; Chroma scores ≠ probabilities; t3.small not guaranteed | L100, L240, L265 |
| S-07 | Private SSH-tunnel access instead of a public unauthenticated endpoint | L276–293 |
| S-08 | Cut order that protects ingestion, QA, citations, and persistence | L369 |
| S-09 | Per-slide chunking (never across slides) keeps citations exact | L84 |

## 4. Findings register

Severity: Critical · High · Medium · Low (mission § 5). Severity is about the issue, not the recommendation's priority.

| ID | Title | Severity | Evidence | Missing / inconsistent / risky | Why it matters | Likely consequence | Recommended correction | Confidence & limits | Recs |
|---|---|---|---|---|---|---|---|---|---|
| F-01 | Evidence gate has no decidable rule | **High** | L238–242 ("conservative evidence policy", "calibrate"); L215–222 (edge); SR-05 L41, L57–59 | Only "empty retrieval → fallback" is defined. With ≥ 5 chunks indexed, top-k similarity search returns k results for any query, so for the demo deck the deterministic branch **never fires on the unsupported question**. Everything then rests on the model choosing "not enough information". | QG-07 is a load-bearing test (SR-05 L57–59), and the unsupported question is "essential" to the demo (L396) | Unsupported question answered with plausible citations, live, in the interview. Or an ad hoc threshold invented under time pressure in M3. | Define a two-layer gate: (1) a distance threshold on the best hit, with a calibration procedure over the 5 eval questions and recorded values; (2) a structured generation output with an explicit `insufficient` flag that also routes to the deterministic fallback text | High on the mechanism (top-k semantics of vector search). Medium on the eventual threshold value, which is unmeasured. | R-01 |
| F-02 | Citation contract unspecified | **High** | L98 ("*If* the model is asked to cite…"); L66 vs L220–222 (validation placement differs); L204 (`sources: list[dict]`); SR-04 L55; SR-05 L40. *r2: L66 is part of the reconstructed Mermaid diagram (D-07), so it is tagged [ASSUME: reconstruction]; the finding stands on L98, L204, L220–222.* | No identifier format, no output schema, no rule for what is displayed (cited ∩ retrieved vs all retrieved), no behaviour when the model cites nothing or cites invalid IDs. The diagram puts validation in its own node after `generate_answer`; § 6 puts it inside. | QG-06 is load-bearing and must be a deterministic unit test | QG-06 test cannot be written until M3 decides it. Risk of displaying retrieved-but-irrelevant slides as "sources". | Specify: evidence labelled `[S1]…[Sk]` in the user message; model returns structured `{answer, cited: [labels], insufficient: bool}`; display = valid cited labels mapped to metadata; invalid labels dropped and logged; no valid citation + not insufficient → owner-chosen policy (OQ-13) | High | R-02 |
| F-03 | Ingest consistency across uploads, Chroma, and manifest is under-specified | Medium | L85–87 ("cleaned up or safely retried"); SR-04 L43, L50 | No deterministic ID scheme is given. No ordering of file write → upsert → manifest. No startup reconciliation for chunks whose hash is not in the manifest. | QG-03 (no duplication) and QG-08 (no partial state) depend on it | Duplicate or orphan chunks after a crash mid-ingest. A flaky QG-03 test. | Chunk ID `"{sha256}:{slide}:{chunk_index}"`; order = validate → hash → dedupe check → extract → upsert → atomic manifest write; on failure delete by `file_sha256` filter; on startup delete chunks whose hash is absent or not `complete` in the manifest | High (logic). Library-level delete-by-metadata support unverified (R-12). | R-03 |
| F-04 | Manifest schema and vector-space identity have no mechanism | Medium | L137 (model change → reindex/new collection), L189 (manifest fields in prose); SR-04 L67 | The policy exists but the mechanism does not: no collection naming rule, no `embedding_model` field, no `schema_version`. Same bytes uploaded under a different filename: which display name wins? | Mixing vector spaces silently breaks retrieval. The manifest is the document list (MUST HAVE). | Silent retrieval degradation if `EMBEDDING_MODEL` changes between deploys | Manifest v1 schema (`schema_version`, `embedding_model`, `collection`, docs keyed by sha256 with display name, status, slide/chunk counts, timestamps). Collection name derived from the embedding-model slug. Mismatch at startup → new collection + docs flagged for reindex. | High | R-04 |
| F-05 | Upload limits not numeric; enforcement mechanics missing | Medium | L80, L412; SR-04 L35–43 ("fixed ceiling" without a value) | No uncompressed-size ceiling, member-count cap, or slide cap. No statement of *how* the 10 MB cap is enforced before the body is read (SR-04 L41). XML parser safety of python-pptx is not addressed. | Untrusted ZIP/XML input is the main attack surface (SR-04 L1–3) | Zip bomb or memory exhaustion on a 2 GiB host. A validator written without agreed numbers. | Fix numbers (proposed: 10 MB compressed, 100 MB total uncompressed, ≤ 2,000 members, ≤ 200 slides), stream-count bytes with early abort, check member names, and verify python-pptx's XML parser config | Medium. Exploitability is low (single private user behind SSH), but SR-04 makes these MUSTs. Library parser config unverified. | R-05 |
| F-06 | Schedule omits work items and overloads M4 | **High** | L319–369; L157 (`demo/generate_pptx.py` in tree); SR-05 L71 (conftest uses the generated deck); L461 ("One-day feasibility 3.5"); L476 | Generating the 10-slide synthetic deck is in the tree but in **no milestone**. Writing the tests is not budgeted. M4 packs Dockerfile, EC2 + EBS provisioning, deploy, restart verification, README, architecture doc, and rehearsal into 2 h. | The 8 h budget is a confirmed constraint (C-01). The plan's own score flags deployment risk. | Buffer consumed by M4. Tests or docs cut, which the cut order does not allow (L369). | Budget the deck generator in M2 (it is the QG-01 fixture). Fold tests into each milestone's exit. Move AWS provisioning out of the clock or explicitly into M4 (OQ-09). Give each milestone an exit command. | High (evidence is in the plan itself). Durations are estimates. | R-06 |
| F-07 | Requirements are narrative and untraceable | Medium | L28–49, L319–369, L398–409 | No FR/NFR IDs. No mapping MUST HAVE → requirement → QG/test → milestone. NFRs absent: external-call timeouts (SR-04 L66), latency expectations, memory under 2 GiB, cost cap. | Agents and the owner need IDs to plan, test, and accept. Methodology M-02/M-03. | Gaps found during build. Untestable acceptance. | FR/NFR table with IDs, acceptance criteria, and QG/test mapping | High | R-07 |
| F-08 | HTTP interface undefined | Medium | L176 (main.py responsibilities in one line); SR-05 L64 (each route needs 2xx + error test) | No route list, methods, form fields, status codes, error rendering, or `/health` semantics. Upload is implicitly synchronous (embedding inside the request). | Rule SR-05 requires per-route tests. UI and tests need a contract. | Rework between M1 and M3. Inconsistent error behaviour. | Route table: `GET /`, `POST /upload`, `POST /ask`, `GET /health`, with status codes and error behaviour | High | R-08 |
| F-09 | Eval-set pass criteria are fuzzy | Medium | L388–396; SR-05 L45–55 | "Combines evidence", "summarizes steps" have no checkable criterion. Live LLM output is non-deterministic. | QG-05 and the integration tests need stable pass rules | Flaky integration tests, or tests weakened later | Split: deterministic retrieval check (expected slides ∈ top-5); factual answers assert the substring (`46 ms`, `92%`); synthesis/troubleshooting are manual grounding checks; temperature 0 | High | R-11 |
| F-10 | Deployment lacks run spec, mount guard, and rollback | Medium | L257–262, L268–274, L313–317 | No exact `docker run` (loopback publish, env file, bind mount, restart policy). No check that `/data` is actually the EBS mount (if not, QG-09 passes on the root disk and data dies with the instance). Image build location on a 2 GiB host unstated. No rollback. Chroma client telemetry (an extra egress) not addressed. | QG-09 and SR-04 L71–73 depend on exact flags | False QG-09 pass, or port exposure by a wrong `-p` | Runbook: `mountpoint /var/lib/sliderag` precondition; exact `docker run -p 127.0.0.1:8000:8000 --env-file … -v /var/lib/sliderag:/data --restart unless-stopped sliderag:<ver>`; keep the previous tag for one-command rollback; disable Chroma anonymized telemetry | Medium. The telemetry default is unverified for the pinned version (R-12). | R-10 |
| F-11 | `/data` containment rule conflicts with local dev and tests; config keys incomplete | Medium | SR-04 L49 ("MUST be under `/data`"), L31 (closed key list); L134 (`CHROMA_PATH` only); SR-05 L71 ("temp `/data`-style directory") | Uploads and manifest paths have no setting. A literal `/data` containment check fails on a laptop and in pytest temp dirs. | Config is M1 work, and the rule is a MUST | Ad hoc weakening of containment, or tests that need root | A single data root (default `/data`); derive `uploads/`, `chroma/`, `manifest.json` from it; containment = under the configured root. This needs either a new `DATA_DIR` key or deriving the root from `CHROMA_PATH`'s parent (owner choice, OQ-14). | High | R-09 |
| F-12 | Governance artifacts drift from each other | Low | SR-06 L11 vs SR-08 L26 (`ci` type); SR-10 L81 (scope optional for all types) vs SR-06 L65–67; SR-06 L35–45 vs harness attribution default (OQ-11); SR-03 L3 (SoT pointer) | Small inconsistencies in the rule set | They confuse agents at commit time | A denied `ci:` commit; an agent adding a forbidden trailer | Proposed rule edits in readiness-report.md. Owner decides OQ-05 and OQ-11. *r2: the M1-blocking commit precondition moved to F-19 (S3).* | High | R-14 |
| F-13 | External claims unverified; Python version mismatch | Medium | L104, L110–122 (models, prices, "+1" residue), L194–196, L268–270, L286, L295–313; SR-18 (host 3.14.4) | Model availability and prices as of the build date are unverified. LangGraph/langchain-chroma API claims unchecked. Citation residue ("OpenAI API +1") is not a reference. | A retired model or changed API blocks M2/M3 | Lost build time at the worst moment | Verify at M1: provider model list, `library-claim-verify` on LangGraph/langchain-chroma/python-pptx claims, `uv python pin 3.12`; record in the source register | High that it is unverified; unknown whether anything is actually wrong | R-12 |
| F-14 | Agent context gaps for the build | Low | L140–172 (tree lacks `tests/conftest.py`, which SR-05 L71 requires); L163 (`docs/architecture.md` unowned in the roadmap); no CLAUDE.md (SR-17); SR-01 is pasted text without markdown headings | Build agents lack commands and conventions in one place. Tree and rules disagree slightly. | Methodology M-06; build sessions read CLAUDE.md first | Repeated mistakes; drift between plan tree and rules | Add CLAUDE.md at M1 via `managing-agent-memory`; add `conftest.py` to the tree; assign `docs/architecture.md` to M4 | High | R-13 |
| F-15 | Observability and failure handling thin | Medium | L414 (only "avoid leaking credentials in logs"); SR-04 L66 (timeouts), L80 (log security events) | No log events defined (rejected upload, dropped citation, fallback taken). No timeout values. No user-visible error for an API outage. | Demo debugging and the security rule's logging requirement | Silent failures during the live demo | Fold into R-07 (NFR: timeouts 30 s chat / 30 s embed, structured log events) and R-08 (error rendering, `/health`) | High | R-07, R-08 |

## 5. Recommendations and initial ranking

### 5.1 Rubric

Priority = Σ weight × score/5. Weights: **A** alignment 25 · **B** risk reduction 25 · **C** unblocking 20 · **D** implementation readiness 20 · **E** build-time proportionality 10. This is a structured decision aid, not a prediction. Confidence is reported separately. Effort is **build-time** effort only (D-01). Documentation effort is free in this phase.

### 5.2 Categories (initial; final categories in § 7.2)

- **Mandatory blockers** (D-12): R-01, R-02, R-03, R-05
- **Ranked improvements:** R-06, R-07, R-10, R-04, R-11, R-08, R-09, R-12, R-13
- **Optional enhancement:** R-14

### 5.3 Recommendation records

#### R-01 · Define the evidence gate · MANDATORY (blocks M3)
- **Rank: initial 1 → final 1.** r2: score unchanged (94); confidence High → **Medium** (F-17 calibration circularity; possible distance overlap).
- **Findings:** F-01 · **Owner role:** architect (spec) → M3 builder (calibration)
- **Action:** Specify a two-layer gate: (a) `best_distance > T` → `no_evidence`, with T calibrated in M3 by recording best-hit distances for the 4 supported and 1 unsupported eval questions and setting T between the groups (or reporting that they overlap); (b) generation returns `insufficient: true`, which routes to the same deterministic fallback text. Empty retrieval → fallback.
- **Expected outcome:** QG-07 is testable deterministically (unit: mocked distances and flag) and live (integration).
- **Dependencies:** R-02 (shared output schema), R-12 (model verification).
- **Effort:** spec 0 h build-time; calibration ~20–30 min in M3. Basis: 5 queries + one table.
- **Acceptance:** spec names the rule, the calibration procedure, and where T is configured; unit tests cover all three routes.
- **Uncertainty:** distances may not separate cleanly. Layer (b) is then the safety net, and that must be stated honestly in the demo.

| Criterion | Score | Justification |
|---|---|---|
| A Alignment | 5 | Insufficient-evidence fallback is MUST HAVE (L36); the negative case is "essential" (L396) |
| B Risk | 5 | Evidenced: the deterministic branch cannot fire on the demo's unsupported question (F-01) |
| C Unblocking | 4 | Blocks the M3 graph node and QG-07 tests; not M1/M2 |
| D Readiness | 5 | Turns a load-bearing gate from untestable into testable |
| E Proportionality | 4 | ~30 min build time for the highest-visibility demo behaviour |
| **Priority** | **94** | 25+25+16+20+8 |

Confidence: **High**.

#### R-02 · Define the citation contract · MANDATORY (blocks M3)
- **Rank: initial 2 → final 2.** r2: unchanged (89). Executed as one QA-contract bundle with R-01 (shared schema).
- **Findings:** F-02 · **Owner role:** architect → M3 builder
- **Action:** Specify evidence labelling `[S1]…[Sk]`, a structured model output `{answer, cited, insufficient}`, validation as a step at the end of `generate_answer` (resolving the L66 vs L222 placement), display = valid cited labels → metadata labels `"<source_file> — slide <n>"`, invalid labels dropped and logged, and the no-citation policy per OQ-13.
- **Dependencies:** R-01 (same schema). · **Effort:** ~15 min extra in M3 versus an unspecified approach. Basis: one Pydantic model + one filter function.
- **Acceptance:** a unit test feeds fabricated labels and asserts none are displayed (QG-06).
- **Uncertainty:** structured-output support of the chosen model and wrapper (R-12).

| Criterion | Score | Justification |
|---|---|---|
| A | 5 | "Evidence-grounded answers · source-verified citations" is MUST HAVE (L35); SR-04 L55 |
| B | 4 | Fabricated-citation risk is real but the plan already intends validation; risk is in the gaps |
| C | 4 | Blocks the QG-06 test and the answer template |
| D | 5 | Makes QG-06 a deterministic unit test |
| E | 4 | Small code; large demo credibility |
| **Priority** | **89** | 25+20+16+20+8 |

Confidence: **High**.

#### R-03 · Specify ingest ordering, deterministic IDs, and reconciliation · MANDATORY (blocks M2)
- **Rank: initial 3 → final 3.** r2: **absorbs R-04** (manifest v1 + vector-space identity). Merged score 76 (A4 B4 C3 D4 E4); effort ~30–35 min (PREP-08 M2 step 4).
- **Findings:** F-03 · **Owner:** architect → M2 builder
- **Action:** ID scheme, ordering, failure cleanup by `file_sha256` filter, startup reconciliation (see F-03).
- **Dependencies:** R-04 (manifest status field), R-12 (delete-by-filter API). · **Effort:** ~20 min in M2.
- **Acceptance:** QG-03 test (re-upload → same count); a test that simulates failure after upsert leaves no chunks for that hash and no manifest entry.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Idempotent indexing is in the module contract (L177) and SR-04 L50 |
| B | 4 | Partial state is a stated rule violation (SR-04 L43) |
| C | 3 | Needed for M2 completion; not for M1 |
| D | 4 | Makes QG-03/QG-08 "no partial state" testable |
| E | 4 | ~20 min |
| **Priority** | **76** | 20+20+12+16+8 |

Confidence: **High**.

#### R-05 · Fix numeric upload limits and enforcement mechanics · MANDATORY (blocks M2)
- **Rank: initial 4 → final 5.** r2: B 3→4 (python-pptx reads all members into memory, SR-30; browser path F-18); E 4→3 (realised test cost 40–60 min, unmeasured; returns to 4 if test tiering OQ-25 is adopted). Revised **70**.
- **Findings:** F-05 · **Owner:** security writer (S2) → M2 builder
- **Action:** Agree on the numbers. Enforce 10 MB by streamed counting (and `Content-Length` pre-check) before full read. Check magic bytes, required members, member names, total uncompressed size, member count, slide count. Confirm python-pptx's XML parsing does not resolve external entities.
- **Why mandatory:** `security-patterns.md` L35–43 are MUSTs and "violations must be fixed before committing" (SR-04 L5). Its lower score below does not de-prioritise it (mission § 6).
- **Effort:** ~25 min in M2 including adversarial tests. Basis: `zipfile` infolist checks + 4 small tests.
- **Acceptance:** QG-08 adversarial tests (non-ZIP named .pptx, >10 MB, `..` member, zip bomb) reject with a clear error and leave no state.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Upload validation is MUST HAVE (L30) |
| B | 3 | Real attack class, but exposure is a single private user behind SSH (L276) |
| C | 2 | Only the validator depends on it |
| D | 4 | Turns "fixed ceiling" into testable numbers |
| E | 4 | ~25 min |
| **Priority** | **67** | 20+15+8+16+8 |

Confidence: **Medium** (python-pptx parser behaviour unverified).

#### R-06 · Re-budget the roadmap with exit commands
- **Rank: initial 5 → final 8.** r2: score unchanged (78). It drops in rank only because R-10 and R-09 became mandatory and R-15 entered as an owner precondition. The action is incomplete until the merged budget is re-summed (PREP-08 § 15.3, OQ-25).
- **Findings:** F-06 · **Owner:** architect (S1) + owner (OQ-09)
- **Action:** Put the deck generator in M2 (≈20 min) as the QG-01 fixture. Make tests part of each milestone's exit. Define an exit command per milestone. Decide whether AWS provisioning is inside M4 (OQ-09). Move `docs/architecture.md` + README into M4 with a fixed timebox.
- **Effort:** 0 h build-time (planning). It reallocates time rather than adding it.
- **Acceptance:** the revised roadmap sums to ≤ 8 h with every tree item and every QG assigned to a milestone.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | 8 h budget is a confirmed constraint (C-01) |
| B | 4 | Plan self-rates feasibility 3.5/5 (L461); unbudgeted items evidenced |
| C | 4 | Every build session depends on the milestone breakdown |
| D | 3 | Improves sequencing more than testability |
| E | 5 | Pure planning; no build time |
| **Priority** | **78** | 20+20+16+12+10 |

Confidence: **Medium** (durations are estimates; OQ-09 open).

#### R-07 · Requirements register with traceability and NFRs
- **Rank: initial 6 → final 9.** r2: D 5→4 (its readiness value double-counts R-01/R-02/R-03/R-08). Revised **70**.
- **Findings:** F-07, F-15 · **Owner:** S1
- **Action:** FR-xx/NFR-xx with acceptance criteria. Map MUST HAVE → FR → QG/test → milestone. NFRs: external-call timeouts, single worker, 2 GiB memory check, structured security log events, cost note.
- **Effort:** 0 h build. **Acceptance:** every MUST HAVE row and every QG appears in the matrix.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Directly restates confirmed intent as checkable items |
| B | 2 | Reduces omission risk; does not by itself fix a failure mode |
| C | 4 | S2's verification mapping and build plans key off the IDs |
| D | 5 | Core of implementation readiness |
| E | 4 | Planning only; slight ongoing upkeep |
| **Priority** | **74** | 20+10+16+20+8 |

Confidence: **High**.

#### R-10 · Deployment runbook with mount guard and rollback
- **Rank: initial 7 → final 4.** r2: **reclassified MANDATORY** (blocks M4, or blocks provisioning under M4-pre). SP L73 "verified mounted before the container starts" fails on reboot with `unless-stopped` unless dockerd is ordered after the mount (S2 DEP-04), and SP L71 needs the exact `-p` flag. Score unchanged (72).
- **Findings:** F-10 · **Owner:** S2 (verification) / architect
- **Action:** Exact `docker run`. `mountpoint` precondition. Version-tagged images with the previous tag kept. Build location decision (local build + `docker save | ssh docker load`, or build on host). Chroma telemetry off. QG-09 manual script (recreate container → query).
- **Effort:** ~15 min in M4 beyond what M4 already does.
- **Acceptance:** runbook steps executed once on EC2; QG-09 evidence recorded.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Docker + AWS is MUST HAVE; persistence is in the DoD |
| B | 4 | Wrong mount = data loss + false QG-09 pass; wrong `-p` = exposure (SR-04 L71) |
| C | 2 | Only M4 |
| D | 4 | Makes QG-09 a scripted check |
| E | 4 | Small |
| **Priority** | **72** | 20+20+8+16+8 |

Confidence: **Medium** (telemetry default and host build feasibility unverified).

#### R-04 · Manifest v1 schema and vector-space identity
- **Rank: initial 8 → merged into R-03.** r2: double count with R-03 (S3 § 2.3); S1 implements both as one mechanism. If the owner keeps them separate: C 3→2, 67, mandatory (SP L67).
- **Findings:** F-04 · **Owner:** S1 → M2 builder
- **Action:** Schema with `schema_version`, `embedding_model`, `collection`, docs keyed by sha256. Collection name derived from the model slug. Startup mismatch handling. Display-name rule for identical bytes (first upload wins, proposed).
- **Effort:** ~10 min in M2. **Acceptance:** a unit test asserts that a changed `EMBEDDING_MODEL` yields a different collection name.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Document list is MUST HAVE (L37); SR-04 L67 |
| B | 3 | Mixed-vector-space risk only on a model change; unlikely within the demo |
| C | 3 | Feeds R-03 status handling |
| D | 4 | Gives the manifest a testable contract |
| E | 4 | ~10 min |
| **Priority** | **71** | 20+15+12+16+8 |

Confidence: **High**.

#### R-11 · Make eval-set pass criteria checkable
- **Rank: initial 9 → final 12.** r2: D 5→4 (QG-05 is not load-bearing; consistency with R-03). Revised **67**.
- **Findings:** F-09 · **Owner:** S2
- **Action:** Per question: expected slides ∈ top-5 (retrieval, integration); factual substring check; synthesis and troubleshooting as manual grounding checks; unsupported → fallback, no citation; temperature 0.
- **Effort:** ~15 min in M3. **Acceptance:** parametrised tests encode exactly these criteria.

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | Eval set is mandated (SR-05 L45–55) |
| B | 3 | Prevents flaky or weakened tests |
| C | 2 | Only test authoring depends on it |
| D | 5 | Directly defines verification |
| E | 4 | Small |
| **Priority** | **71** | 20+15+8+20+8 |

Confidence: **High**.

#### R-08 · HTTP route table, error behaviour, `/health`
- **Rank: initial 10 → final 11.** r2: unchanged (68). E stays 5, with a watch: if all degraded paths are kept, E = 4 is more accurate.
- **Findings:** F-08, F-15 · **Owner:** S1
- **Action:** Routes, methods, form fields, status codes, error rendering. `/health` = liveness plus data-root writable (no external calls).
- **Effort:** 0 h extra (defines what M1/M3 build anyway). **Acceptance:** each route has a 2xx and an error test (SR-05 L64).

| Criterion | Score | Justification |
|---|---|---|
| A | 4 | FastAPI interface is MUST HAVE |
| B | 2 | Mostly rework avoidance |
| C | 3 | M1 skeleton and template depend on it |
| D | 4 | Enables per-route tests |
| E | 5 | No added build time |
| **Priority** | **68** | 20+10+12+16+10 |

Confidence: **High**.

#### R-09 · Single configurable data root and containment wording
- **Rank: initial 11 → final 6.** r2: **reclassified MANDATORY (blocks M1)**: SP L49 is a MUST and OQ-14 blocks M1. C 3→4 (every fixture depends on it). Revised **68**.
- **Findings:** F-11 · **Owner:** S2 + owner (OQ-14)
- **Action:** Data root (default `/data`) with derived paths. Containment against the resolved root. Propose the rule-wording change (readiness report). Decide `DATA_DIR` vs deriving from `CHROMA_PATH`.
- **Effort:** ~5 min in M1.

| Criterion | Score | Justification |
|---|---|---|
| A | 3 | Supports persistence and security rules; not itself a scope item |
| B | 3 | Avoids ad hoc containment weakening |
| C | 3 | M1 config design |
| D | 3 | Makes containment testable in temp dirs |
| E | 5 | Minutes |
| **Priority** | **64** | 15+15+12+12+10 |

Confidence: **High**.

#### R-12 · Verify external claims and pin Python at M1 · PROVISIONAL score
- **Rank: initial 12 → final 10.** r2: C 3→4, D 3→4 (mandatory items depend on it; about 15 load-bearing [ASSUME] items enumerated). Revised **62–77 (provisional)**. It is an M1 entry check: execution comes first even though its priority rank is 10.
- **Findings:** F-13 · **Owner:** M1 builder / owner
- **Action:** Check the provider model list and prices. Run `library-claim-verify` for LangGraph `StateGraph` + conditional edges, langchain-chroma `persist_directory` / delete-by-filter / relevance scores, python-pptx table/XML handling. `uv python pin 3.12` (OQ-07). Record as SR-30+.
- **Effort:** ~15 min in M1.

| Criterion | Score | Justification |
|---|---|---|
| A | 3 | Supports the chosen stack; not itself a feature |
| B | **unknown (1–4)** | Missing evidence: whether any claim is actually false today. If a model is retired, risk reduction is 4; if all hold, 1. Not scored zero, not renormalised. |
| C | 3 | M2/M3 depend on the verified APIs |
| D | 3 | Removes uncertainty from R-01/R-02/R-03/R-05 |
| E | 5 | ~15 min |
| **Priority** | **54–69 (provisional)** | 15 + [5…20] + 12 + 12 + 10 |

Confidence: **Low** on the score (premise unverified); **High** that verification is cheap.

#### R-13 · Agent build context
- **Rank: initial 13 → final 13.** r2: unchanged (57).
- **Findings:** F-14 · **Owner:** M1 builder
- **Action:** CLAUDE.md at M1 (commands, verification block) via `managing-agent-memory`. Add `tests/conftest.py` to the tree. Assign `docs/architecture.md` to M4.
- **Effort:** ~10 min in M1.

| Criterion | Score | Justification |
|---|---|---|
| A | 3 | Supports the "basic README" and the agent workflow |
| B | 2 | Reduces repeated agent mistakes; no evidenced failure yet |
| C | 3 | Build sessions read CLAUDE.md first |
| D | 3 | Puts verification commands in reach |
| E | 4 | ~10 min |
| **Priority** | **57** | 15+10+12+12+8 |

Confidence: **High**.

#### R-14 · Governance rule-drift fixes · OPTIONAL
- **Rank: initial 14 → final 14.** r2: narrowed to cosmetic drift (`ci` type, hook regex, `\n`, SoT pointer). The commit precondition moved to R-15. Unchanged (46).
- **Findings:** F-12 · **Owner:** owner
- **Action:** Proposed edits listed in readiness-report.md (`ci` type, hook scope-optional regex, deny `\n`, SoT pointer after approval). Owner applies or rejects.
- **Effort:** ~10 min, outside the build clock if done before M1.

| Criterion | Score | Justification |
|---|---|---|
| A | 2 | Hygiene |
| B | 2 | Minor commit-time friction |
| C | 2 | Only the first `ci`-type commit (no CI planned) |
| D | 2 | Indirect |
| E | 5 | Trivial |
| **Priority** | **46** | 10+10+8+8+10 |

Confidence: **High**.

#### R-15 · Settle commit preconditions before M1 · OWNER PRECONDITION *(added in r2, S3)*
- **Rank: new → final 7.**
- **Findings:** F-19 · **Owner:** repository owner
- **Action:** Before M1, either (a) create the GitHub remote and the issues, so the first commit can carry `(#N)`, or (b) relax `(#issue)` (OQ-02). Confirm the rule wins over harness attribution (OQ-11). Budget the per-issue branch/PR overhead in R-06, or waive it for the 8 h build.
- **Effort:** 10–20 min if on the clock; 0 if done before M1.
- **Acceptance:** a test commit message passes `.claude/hooks/check-commit-format.sh`.

| Criterion | Score | Justification |
|---|---|---|
| A | 3 | SR-06/SR-07 are binding (C-09) |
| B | 3 | The hook denies the first commit with certainty; the fix is trivial |
| C | 4 | Blocks every commit from M1 |
| D | 2 | Indirect |
| E | 4 | Minutes |
| **Priority** | **62** | 15+15+16+8+8 |

Confidence: **High**.

### 5.4 Initial ranking (orchestrator, pre-review)

Ordering: blocker status → score within category → confidence → dependencies.

| Initial rank | ID | Category | Score | Confidence |
|---|---|---|---|---|
| 1 | R-01 | Mandatory | 94 | High |
| 2 | R-02 | Mandatory | 89 | High |
| 3 | R-03 | Mandatory | 76 | High |
| 4 | R-05 | Mandatory | 67 | Medium |
| 5 | R-06 | Improvement | 78 | Medium |
| 6 | R-07 | Improvement | 74 | High |
| 7 | R-10 | Improvement | 72 | Medium |
| 8 | R-04 | Improvement | 71 | High (tie with R-11; ranked first because R-03 depends on it) |
| 9 | R-11 | Improvement | 71 | High |
| 10 | R-08 | Improvement | 68 | High |
| 11 | R-09 | Improvement | 64 | High |
| 12 | R-12 | Improvement | 54–69 provisional | Low |
| 13 | R-13 | Improvement | 57 | High |
| 14 | R-14 | Optional | 46 | High |

R-12 is placed by its interval midpoint (61.5), below R-09. Its ordering is **provisional**.

### 5.5 Execution order (distinct from priority)

1. **Before M1 (doc/owner time):** R-07, R-08, R-01, R-02, R-04, R-03, R-05, R-11, R-09, R-06, R-10 are written into the revised plan (*r2: R-06 and R-10 were missing here in r1; S3 § 2.5*). The owner answers OQ-05, OQ-07, OQ-09, OQ-10, OQ-12, OQ-13, OQ-14 and settles R-15. R-14 is optional. *If OQ-09 = M4-pre, R-10's host preparation (PREP-08 § 10.2.G.1) must be approved before provisioning.*
2. **M1:** R-12 (verify + pin), R-09 (config), R-13 (CLAUDE.md), R-08 skeleton routes.
3. **M2:** R-05, R-04, R-03, plus the deck generator (R-06).
4. **M3:** R-02, R-01 calibration, R-11 tests.
5. **M4:** R-10 runbook + QG-09.

## 6. Independent review (S3)

S3 ran in a separate Herdr session and authored none of the reviewed documents. Its full text is in `delegation/S3-critic-review.md` (SR-36). The orchestrator reviewed it and decided as follows (D-13, D-14):

| S3 proposal | Evidence S3 gave | Orchestrator decision |
|---|---|---|
| Four citation errors (F-01, F-02, F-08, F-15) | Rule line checks | **Accepted.** Fixed in § 4. |
| F-02's L66 evidence is a reconstruction | D-07; SR-02 has no recoverable edges | **Accepted.** Tagged. Severity unchanged. |
| F-12 split; new F-16…F-20 | § 1.2 | **Accepted** with S3's severities (§ 4) |
| Score changes R-05 (B+1, E−1), R-07 (D−1), R-09 (C+1), R-11 (D−1), R-12 (C+1, D+1); R-01 confidence → Medium | § 2.2, criterion level | **Accepted.** Each is backed by new evidence (SR-30) or by removing a double count. |
| Merge R-04 → R-03 | Double count in C and the tie-break; one mechanism in PREP-08 §§ 6.3–6.5 | **Accepted** |
| Split R-14 → R-14 + R-15; new "owner precondition" category | F-19; OQ-02/OQ-10 block M1 | **Accepted** |
| Correct D-12's load-bearing list to QG-06/QG-07 | SR-05 L59 | **Accepted** (decision-log r2). The blocker results are unchanged. |
| Reclassify R-09 and R-10 as mandatory | SP L49 and L73 MUSTs; S2 DEP-04 evidence | **Accepted** |
| Ranks 8–13 as tiers, not ordinals | Sensitivity: a ±1 change reorders them | **Accepted** (§ 7.2) |
| Not challenged | — | The R-01, R-02, R-06, R-08, R-10, R-13, R-14 scores were held after challenge. Arithmetic re-verified (S3 § 2.1). |

**Sensitivity result (S3 § 3):** the blocker set cannot change through scores, only through D-12 classification. The top 5 is identical under score-only changes (S3 § 4.3). It changes only through the accepted reclassifications. **The initial ordering of the top recommendations was confirmed. The rank changes below come from classification, not from re-scoring.**

## 7. Re-ranking table

### 7.1 Initial vs final

| ID | Initial category | Initial score | Initial rank | Final category | Revised score | Final rank | What changed | Why |
|---|---|---|---|---|---|---|---|---|
| R-01 | Mandatory | 94 | 1 | Mandatory (M3) | 94 | 1 | Confidence → Medium | F-17 calibration circularity |
| R-02 | Mandatory | 89 | 2 | Mandatory (M3) | 89 | 2 | Bundled with R-01 | Shared output schema |
| R-03 | Mandatory | 76 | 3 | Mandatory (M2) | 76 | 3 | Absorbs R-04 | Double count; one mechanism |
| R-10 | Improvement | 72 | 7 | **Mandatory (M4 / pre-provision)** | 72 | 4 | Reclassified | SP L73 + L71 MUSTs; DEP-04 evidence |
| R-05 | Mandatory | 67 | 4 | Mandatory (M2) | 70 | 5 | B+1, E−1 | SR-30 full-read evidence; realised test cost |
| R-09 | Improvement | 64 | 11 | **Mandatory (M1)** | 68 | 6 | Reclassified; C+1 | SP L49 MUST; OQ-14 blocks M1 |
| R-15 | — | — | — | **Owner precondition (M1)** | 62 | 7 | New (from R-14) | F-19 |
| R-06 | Improvement | 78 | 5 | Improvement · Tier I | 78 | 8 | Rank only | Classification changes above it; needs the merged re-sum |
| R-07 | Improvement | 74 | 6 | Improvement · Tier II | 70 | 9 | D−1 | Double-counted readiness |
| R-12 | Improvement | 54–69 | 12 | Improvement · Tier II (M1 entry check) | 62–77 (provisional) | 10 | C+1, D+1 | Mandatory items depend on it |
| R-08 | Improvement | 68 | 10 | Improvement · Tier II | 68 | 11 | — | — |
| R-11 | Improvement | 71 | 9 | Improvement · Tier II | 67 | 12 | D−1 | QG-05 not load-bearing |
| R-13 | Improvement | 57 | 13 | Improvement · Tier III | 57 | 13 | — | — |
| R-14 | Optional | 46 | 14 | Optional | 46 | 14 | Narrowed | Precondition moved to R-15 |
| R-04 | Improvement | 71 | 8 | Merged into R-03 | — | — | Merged | — |

### 7.2 Final categories

- **Mandatory blockers** (D-12 r2), by milestone:
  - M1: R-09
  - M2: R-03 (incl. R-04), R-05
  - M3: R-01, R-02
  - M4 or pre-provision: R-10
- **Owner precondition:** R-15 (M1), together with the M1-blocking open questions OQ-02, OQ-05, OQ-07, OQ-10, OQ-14, OQ-19, OQ-25.
- **Ranked improvements:**
  - Tier I: R-06
  - Tier II: R-07, R-12, R-08, R-11 (adjacent ranks inside Tier II are not meaningful; S3 § 3)
  - Tier III: R-13
- **Optional:** R-14.
