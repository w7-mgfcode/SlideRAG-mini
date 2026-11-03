# Open Questions

| Field | Value |
|---|---|
| Document ID | PREP-05 |
| Title | Open Questions |
| Revision | r3 |
| Status | Current dispositions recorded; runtime evidence pending |
| Owner | Orchestrator maintains; each question names its responsible owner |
| Last updated | 2026-11-03 |
| Evidence baseline | source-register.md r3 |
| Core-context revision used | core-context.md r3 |
| Dependencies | source-register.md r3, decision-log.md r3, execution-plan.md r1 |
| Supersedes | — |
| Approval record | decision-log.md § 4; D-16…D-21 |
| Change summary | r1: initial questions. r2: OQ-15…OQ-28 integrated. r3: current dispositions after Option C approval; historical question tables retained |

## Current disposition — 2026-11-03

The owner approved Option C. [EXEC-01](execution-plan.md) governs; the later r2 tables preserve historical question wording/status, not active blockers.

| IDs | Current disposition | Remaining action / owner |
|---|---|---|
| OQ-02, OQ-10 | Keep issue references and recorded public repository/hierarchy preference; bundle outcome-sized work | Bootstrap/build session verifies external state and creates only authorized objects; not done here |
| OQ-05 | Resolved: execution-plan.md governs | Pointer aligned; no blanket approval of PREP-08 |
| OQ-07 | Resolved: Python 3.12 | Builder verifies/pins compatible dependencies at M1 |
| OQ-08 | Public model documentation checked; account access/runtime compatibility not demonstrated | Builder proves embedding and structured output at M1; refresh prices when making cost claims |
| OQ-09, OQ-25 | Option C 480-minute timebox; preparation/bootstrap/AWS provisioning tracked separately | Record actual durations/variance; no unquantified test-tier savings |
| OQ-12, OQ-20, OQ-21a | Empty/optional distance/model gate; T constant bound to index configuration; separate probes | Builder measures; acceptance set does not tune T; T=None if separation unsupported |
| OQ-13, OQ-23 | C1 cited-only fail closed; native structured output; malformed response cannot pass live refusal evaluation | Builder implements/verifies |
| OQ-14, OQ-15 | DATA_DIR with derived children; explicit cosine | Rules aligned; verify pinned API behavior |
| OQ-16, OQ-17, OQ-18 | Routine defaults: 409 busy, degraded 503 for absent credentials/inconsistent data, strip inline markers | Builder verifies; no new owner gate |
| OQ-19, OQ-26 | Route tests/plain dependency injection allowed; ordinary layout is not an owner gate | Builder creates only needed files |
| OQ-21b | Superseded: preserve incompatible root, rebuild explicitly in a clean root | No automatic stale-state migration |
| OQ-22, OQ-24 | Extraction/limits in EXEC-01, including corrected total-request cap | Verify boundaries; limits are not performance guarantees |
| OQ-27, OQ-28 | Routine boundary/test decisions, not separate approvals; no template-grep quota | Preserve real escaping/host boundaries and behavior tests |
| OQ-01, OQ-03, OQ-04, OQ-06, OQ-11 | Non-blocking tooling/history; existing attribution rule remains in force | Leave tooling intact unless relevant |

Optional publication choice: publish reviewed raw provenance, or retain it privately with self-contained public summaries. Default to summaries and preserve local originals. Ignored/uncommitted files are not Git history. Credentials, account readiness, performance, and deployment remain evidence obligations, not unanswered product-preference questions.

## Historical r2 questions

Historical blocking legend: **Blocks M\<n\>** meant an answer was needed before that old milestone. The current dispositions above supersede these statuses.

An open question is **not** a decision. Unanswered items must not be treated as implicitly decided.

## Carried forward from HANDOFF.md (SR-13) and the prior handoff (SR-14)

| ID | Question | Why it matters | Affects | Blocking | Evidence needed / owner | Status |
|---|---|---|---|---|---|---|
| OQ-01 | Keep `enableAllProjectMcpServers: true` and the `skill-codex` / `understand-anything` plugins in `.claude/settings.local.json`? | Every enabled MCP server or plugin widens the agent's tool surface in a repo that sends text to external APIs | SR-12 | Non-blocking | Owner preference | open |
| OQ-02 | Keep `(#issue)` mandatory in every commit? | Every commit then needs an existing GitHub issue, which needs a remote (none exists, SR-17). It is the first commit's prerequisite. | SR-06, SR-10, R-14 | **Blocks M1** (first commit) | Owner; depends on OQ-10 | open |
| OQ-03 | Are the 27 generic commands under `.claude/commands/` worth keeping for an 8-hour build? | Noise in the agent's command surface; several reference other projects' conventions | SR-11 | Non-blocking | Owner | open |
| OQ-04 | Fix the commit hook's deny message, which ends with a literal `\n`? | Cosmetic. The deny still works. | SR-10 L109 | Non-blocking | Owner | open |
| OQ-05 | Once approved, should `brainstorm-plan-revised.md` replace `brainstorm-plan.md` as the file `product-vision.md:3` names as source of truth? | Until then, rule SR-03 makes v1.0 authoritative, so revised-plan content cannot govern the build | SR-03, D-02, readiness-report.md § proposed rule changes | **Blocks M1** if the revised plan is meant to govern the build | Owner | open |
| OQ-06 | Add "do not modify `.handoffs/`" to the mission prompt's § 0? | Protects archived handoffs from future runs. This run did not modify `.handoffs/`. | SR-16 | Non-blocking | Owner | open |
| OQ-07 | Pin Python 3.12 with `uv python pin 3.12` (plan) or move the plan to the host's 3.14? | Dependency wheels (chromadb and its transitive deps) may lag on newer Python. The Docker base image must match. | P-01, R-12 | **Blocks M1** (scaffold) | Owner. Evidence: `uv sync` on 3.12 and on 3.14 at scaffold | open |

## New in this package

| ID | Question | Why it matters | Affects | Blocking | Evidence needed / owner | Status |
|---|---|---|---|---|---|---|
| OQ-08 | Are `gpt-4.1-mini` and `text-embedding-3-small` still available, and are the prices in SR-01 L120–122 still current on the build date? | The plan's model defaults and cost estimate depend on them. A retired model blocks M3. | P-04, A-01, R-12 | **Blocks M2** (embedding) / **M3** (chat) | Owner or build session: provider model list + pricing page, recorded in source-register | open |
| OQ-09 | Does AWS provisioning (account, key pair, SG, EC2 launch, EBS attach/format/mount) count inside the 2 h of M4, or may it be done before M1? | SR-01 § 12 already rates one-day feasibility 3.5/5 because deployment "may consume the buffer". Pre-provisioning outside the clock changes that risk materially. | R-06, M4 | **Blocks M4** planning | Owner decision | open |
| OQ-10 | Will a GitHub repository (public?) be created before M1, and will issues be used? | Commit and branch rules presuppose issues. The interview reviewer reads the repo. | OQ-02, SR-06, SR-07 | **Blocks M1** (first commit) | Owner | open |
| OQ-11 | The harness's default commit attribution adds a `Co-Authored-By: Claude …` trailer, which `commit-format.md` L35–45 and the hook (L89–99) forbid. Confirm the rule wins. | Otherwise every agent-made commit is denied by the hook | SR-06, SR-10 | Non-blocking (the rule already wins under user-instruction precedence) | Owner confirmation | open |
| OQ-12 | What exact evidence-gate rule decides `generate_answer` vs `no_evidence` (beyond "empty retrieval")? | With ≥ 5 chunks indexed, top-5 similarity retrieval returns 5 results for **any** question, so "empty retrieval" never fires for the unsupported demo question. QG-07 then rests entirely on model behaviour. | F-01, R-01, QG-07 | **Blocks M3** | Proposed rule in brainstorm-plan-revised.md. Owner accepts the rule and calibration procedure. The threshold value is measured in M3. | open |
| OQ-13 | Which citations are displayed: only model-cited labels that validate against the retrieved set, or all retrieved slides? And what happens when the model cites nothing? | QG-06 cannot be written as a deterministic test without this contract | F-02, R-02, QG-06 | **Blocks M3** | Owner choice between alternatives in brainstorm-plan-revised.md | open |
| OQ-14 | `security-patterns.md` L49 says every runtime path "MUST be under `/data`". Local dev and pytest temp dirs are not. Should the rule read "under the configured data root (default `/data`)"? | Without that wording, every local run or test violates a MUST, or the containment check is weakened ad hoc | F-11, R-09, SR-04 | **Blocks M1** (config design) | Owner. Proposed wording in readiness-report.md | open |

## Added in r2 (from delegated sessions and integration)

| ID | Question | Why it matters | Affects | Blocking | Evidence needed / owner | Status |
|---|---|---|---|---|---|---|
| OQ-15 | Which distance metric does the Chroma collection use: the library default (to verify) or explicit cosine? | T is valid for one metric only | PREP-08 § 6.4, § 5.5 | **Blocks M2** (fixed before the first index) | M1 verification (R-12), then owner | open |
| OQ-16 | Does a second concurrent upload get 409 immediately (proposed) or wait for the lock? | UX vs simplicity | NFR-02 | Non-blocking | Owner | open |
| OQ-17 | When `OPENAI_API_KEY` is missing: start degraded with 503 on upload/ask (proposed), or fail fast at startup? | Tests run without a key | PREP-08 § 7.1 | Non-blocking | Owner | open |
| OQ-18 | Inline `[S<n>]` markers in the answer: strip all (proposed), or rewrite valid ones to display labels? | A stray marker must never look like a citation | PREP-08 § 5.6 | Non-blocking (M3) | Owner | open |
| OQ-19 | Add `tests/test_main.py`, `CHANGELOG.md`, `CLAUDE.md` to the tree? (proposed: yes) | `test-requirements.md:9` names only two test files | PREP-08 § 11 tree | **Blocks M1** (file layout) | Owner; possible rule edit (readiness-report) | open |
| OQ-20 | Where is T configured: a config constant (proposed) or a new env var (which changes SR-04 L31)? | Rule key list is closed | PREP-08 § 5.5 | **Blocks M3** | Owner | open |
| OQ-21 | (a) Add 2–3 held-out unsupported *probe* questions for calibration only? S3 recommends **yes** (F-17). (b) Reindex after a model change by re-upload (proposed) or automatically? | Calibrating T on the same Q5 that QG-07 tests is circular | PREP-08 § 5.5, § 6.4; F-17 | (a) **Blocks M3** calibration; (b) non-blocking | Owner | open |
| OQ-22 | Extraction depth: recurse group shapes (proposed); exclude notes (proposed)? | Citations should point at visible text | FR-03, PREP-08 § 6.2 | Non-blocking (M2) | Owner | open |
| OQ-23 | Unparseable or schema-invalid model output: deterministic fallback (S1, proposed default) or an error page (S2's original)? | It changes a row of the load-bearing QG-07 decision table | PREP-08 § 5.5 row 4, § 8.D UT-03; C-02 | **Blocks M3** | Owner | open |
| OQ-24 | Approve the numeric upload limits UV-L1…UV-L8 (10 MiB, 100 MiB uncompressed, 2,000 members, 200 slides, 1,000,000 characters, 120-character name, 1–1,000-character question)? | SP L42 requires a "fixed ceiling" but gives no number | PREP-08 § 8.B.1; R-05 | **Blocks M2** | Owner | open |
| OQ-25 | The merged plan is estimated at 75–100 min over 8 h. Adopt test tiering (Tier 1 required, Tier 2 cut after CSS polish) and/or M4-pre? | Feasibility of the 8 h budget (C-01) | PREP-08 § 15.3, § 11; R-06 | **Blocks M1** (plan must fit before starting) | Owner; linked to OQ-09 | open |
| OQ-26 | Confirm the reading of `test-requirements.md:72`: injecting app-owned functions (`build_graph(retrieve_fn, …)`, deterministic `Embeddings`) is allowed; only patching LangChain internals is forbidden? | Test fixture design | PREP-08 § 5.1, § 9.H.0 | **Blocks M2** (fixtures) | Owner | open |
| OQ-27 | Keep UV-11 (`TrustedHostMiddleware`, DNS-rebinding defence) or accept residual risk RR-06? | One-line security fix vs scope freeze | NFR-14, § 8.B | Non-blocking | Owner | open |
| OQ-28 | Keep T-D04 (template grep for `\| safe`), given that `test-requirements.md:77` exempts templates from tests? | One-minute guard on an SP L60 MUST | § 9.H.3 | Non-blocking | Owner | open |

