# Readiness Report

| Field | Value |
|---|---|
| Document ID | PREP-10 |
| Title | Readiness Report and Owner Approval Checklist |
| Revision | r2 |
| Status | APPROVED FOR IMPLEMENTATION — Option C scope; operational evidence pending |
| Owner | Orchestrator; approver: repository owner |
| Last updated | 2026-11-03 |
| Evidence baseline | source-register.md r3 |
| Core-context revision used | core-context.md r3 (docs-baseline-r3) |
| Dependencies | all PREP-01…PREP-09 |
| Supersedes | — |
| Approval record | decision-log.md § 4; D-16…D-21 |
| Change summary | r1: readiness assessment and proposed gates. r2: Option C scope approved; operational evidence separated from approval; historical report retained |

## Current verdict — 2026-11-03

**APPROVED FOR IMPLEMENTATION — Option C scope.** The owner approved the preceding architectural recommendation in conversation. [EXEC-01](execution-plan.md) governs. This is direction approval, not blanket approval of PREP-08 or evidence of a working application. This alignment turn changes planning/policy only.

- Settled: fixed configuration/manual rebuild, C1/native structured output, independent calibration probes, DATA_DIR, Python 3.12, cosine, focused failure testing, safe deployment, outcome-sized PRs, and separately accounted preparation/timebox.
- Pending evidence: pinned dependencies and real API access; full local flow; failure/recovery tests; retrieval/semantic behavior; AWS access/mounts; deployment/recreation; measured time/resource usage.
- Local state: no application, commits, or remote. Git identity is configured. Remote/cloud state has not been verified by this approval turn.
- Eight hours is a timebox, not a demonstrated estimate. Use EXEC-01 § 8, not the historical merged scope or unquantified test-tier savings.
- Historical A-1…A-7/B-1…B-7 below are not active blanket gates. [Open questions](open-questions.md) records their current disposition; routine file layout and retrospective process choices do not block M1.
- Current rules use EXEC-01, DATA_DIR, full configuration checks, consistency/recovery tests, and fresh-process persistence. CI uses `chore(ci)` under the existing grammar, without changing executable hooks.
- EXEC-01 is the one additional execution document: retain historical analysis, use one active plan/checklist, avoid rewriting the full proposal.

No acceptance checkbox in EXEC-01 is complete. No new independent review or runtime verification is claimed.

## Historical r1 report (2026-11-02)

The sections below preserve the earlier assessment for traceability. Their present-tense verdicts, open gates, and publication assumptions describe r1, not current state. Ignored/uncommitted provenance is not preserved in Git history and must not be deleted on that assumption.

## 1. Readiness checks

| # | Check | Result | Rationale |
|---|---|---|---|
| 1 | Intent and scope are clear | **Pass** | DoD, users, scope lock, and non-goals are in core-context §§ 1–4, unchanged from v1.0. PREP-08 adds no feature (§ 3). Scope-freeze exceptions are justified individually. |
| 2 | Requirements are sufficiently complete and testable | **Pass** | FR-01…FR-24 and NFR-01…NFR-16 each carry one decidable acceptance criterion (PREP-08 § 4). Every MUST HAVE maps to an FR and every QG to a test or manual check (§ 12, § 9.H.2). The remaining choices (OQ-13, OQ-23) are bounded alternatives with tests written for each. |
| 3 | Architecture is grounded in repository reality | **Pass** | It claims no existing code (the repo is pre-code, SR-17). Every library behaviour the design relies on is tagged [ASSUME] with a verification route (R-12 at M1). The verified ones cite source (SR-30…SR-33, weak provenance noted). |
| 4 | Major alternatives and trade-offs are documented | **Pass** | Gate topology (PREP-08 § 5.3), citation display C1–C4 (§ 5.6), data root D1–D3 (§ 7.3), image build B1–B3 (§ 10.2.G.3), M4-in vs M4-pre (§ 11), the reindex strategy (§ 6.4) |
| 5 | Mandatory blockers are resolved or explicitly awaiting an authorized decision | **Pass** | Each of R-01, R-02, R-03, R-05, R-09, R-10 has a written specification in PREP-08. The decisions they wait on are owner questions (OQ-12, 13, 14, 23, 24) listed in § 3 below. None is silently decided. |
| 6 | Recommendations have transparent scores and rationale | **Pass** | Criterion-level justifications, an unknown handled as an interval (R-12), confidence reported separately, and initial vs final rank on every record (plan-review §§ 5–7) |
| 7 | Agent outputs have been reviewed and reconciled | **Pass** | S3 reviewed S1, S2, and the orchestrator's scores. The orchestrator reviewed S3 and decided every proposal (plan-review § 6). 17 contradictions: 16 resolved on evidence, 1 escalated (PREP-08 § 15.1). |
| 8 | Dependencies and execution order are clear | **Pass, with a conflict flagged** | Execution order is in plan-review § 5.5 and PREP-08 § 11. **[CONFLICT]** The merged plan is estimated at 75–100 min over the 8 h budget unless OQ-25 / OQ-09 are decided (PREP-08 § 15.3). This is an explicit owner decision, not a hidden gap. |
| 9 | Verification and acceptance criteria exist | **Pass** | PREP-08 § 9 (fixtures, security MUST matrix, QG → test map, eval-set criteria) and milestone exit commands (§ 11) |
| 10 | Remaining questions have owners | **Pass** | OQ-01…OQ-28 each name an owner and a blocking status (open-questions.md r2) |
| 11 | The documentation baseline is revisioned and internally consistent | **Pass** | docs-baseline-r2 table in README. Link check: all internal links resolve except the verbatim raw S1 copy's two relative links (expected; the file is a provenance copy). ID ranges checked (OQ ≤ 28, R ≤ 15, F ≤ 20, D ≤ 15, SR ≤ 36). The C-xx collision is disambiguated. |

**Not independently reviewed:** README, methodology-adaptation, delegation-manifest, and this report were authored by the orchestrator and have not been reviewed by a second session. Their status is `in-review` until the owner reads them.

## 2. Verdict

**READY FOR HUMAN REVIEW**

The package is coherent and internally reconciled. **It is not approved.** Decision-log § 4 contains no owner lines, so `APPROVED FOR IMPLEMENTATION` is not available. Implementation has not started.

## 3. Owner approval checklist

Decide each item. To approve, write the line yourself in [decision-log.md § 4](decision-log.md#4-owner-approval-record), or tell the orchestrator in conversation and ask for it to be recorded. Format: `2026-MM-DD — Approved by owner — <IDs> — <note>`.

### 3.1 Before Milestone 1 can start

| # | Decide | Options / proposed default | Ref |
|---|---|---|---|
| A-1 | Which plan governs the build | Keep v1.0 as source of truth, or approve PREP-08 r2 and switch the pointer (rule change RC-01) | OQ-05 |
| A-2 | Python version | `uv python pin 3.12` (plan) or move to 3.14 | OQ-07 |
| A-3 | GitHub remote, issues, and `(#issue)` | Create remote + issue #1 before M1, or relax the rule (RC-04); budget or waive branch/PR overhead | OQ-02, OQ-10, R-15 |
| A-4 | Data root | **D1** derive from `CHROMA_PATH` (S2 recommends) / **D2** `DATA_DIR` / D3 literal `/data`; plus rule wording RC-02 | OQ-14, R-09 |
| A-5 | Fit the 8 h budget | Adopt test tiering (Tier 1/Tier 2) and/or M4-pre | OQ-25, OQ-09 |
| A-6 | Tree additions | `tests/test_main.py`, `CLAUDE.md`, `CHANGELOG.md`, `.python-version` (proposed: yes) | OQ-19 |
| A-7 | Process decisions | D-08…D-15 (staging/provenance files, no worktrees, tab topology, no ADRs, D-12 r2, S3 structural changes, reconciliations) | decision-log § 2 |

### 3.2 Before M2 / M3 (can be approved now or at that milestone)

| # | Decide | Proposed default | Ref |
|---|---|---|---|
| B-1 | Upload limits UV-L1…UV-L8 | As specified | OQ-24, R-05 |
| B-2 | Distance metric | Decide after M1 verification | OQ-15 |
| B-3 | Fixture injection reading of `test-requirements.md:72` | Injecting app-owned functions is allowed | OQ-26 |
| B-4 | Evidence-gate rule and calibration procedure (with held-out probe questions) | Two-layer gate; probes: yes | OQ-12, OQ-21, R-01 |
| B-5 | Citation display | **C1** cited-only, fail closed (S1 leans) | OQ-13, R-02 |
| B-6 | Malformed model output | Deterministic fallback | OQ-23 |
| B-7 | Where T lives | Config constant | OQ-20 |

### 3.3 Non-blocking (any time)

OQ-01, OQ-03, OQ-04, OQ-06, OQ-11, OQ-16, OQ-17, OQ-18, OQ-22, OQ-27 (UV-11 Host allow-list), OQ-28 (T-D04 template grep).

## 4. Proposed rule and policy changes (not applied)

The mission forbids editing `.claude/rules/`, CLAUDE.md, or skills in this phase. These are proposals only.

| ID | File | Change | Trigger |
|---|---|---|---|
| RC-01 | `product-vision.md` L3 | Point the source of truth at `docs/.prepare/brainstorm-plan-revised.md`, but only once the owner approves PREP-08 | OQ-05 |
| RC-02 | `security-patterns.md` L49, L78 | L49: "…every resolved path MUST be under the configured data root (`uploads/`, `chroma/`, `manifest.json`). The data root is `/data` in the container and a temporary directory in tests; it is derived once in `app/config.py` [as the parent of `CHROMA_PATH`] and never from request input. Reject anything that escapes." L78: "Resolve and contain every file path under the configured data root (`/data` in the container)." (PREP-08 § 8.C.2) | OQ-14 |
| RC-03 | `security-patterns.md` L31 | Only if A-4 = D2 or OQ-20 = env var: add `DATA_DIR` / `EVIDENCE_MAX_DISTANCE` to the closed key list | OQ-14, OQ-20 |
| RC-04 | `commit-format.md` L11 + hook L81 | Either add `ci` to the type list (it matches `versioning.md:26`), or remove `ci` from `versioning.md:26`. Make the hook's optional scope apply to `docs`/`release` only, matching L65–67. Fix the literal `\n` in the deny message (hook L109). If the owner relaxes `(#issue)` (OQ-02), change the L9–14 grammar and the hook regex together. | R-14, OQ-02, OQ-04 |
| RC-05 | `test-requirements.md` L9 | Add `tests/test_main.py` as the route-test home | OQ-19 |
| RC-06 | `test-requirements.md` L72 | Clarify: "Inject app-owned functions or clients at module boundaries. Do not patch LangChain internals." | OQ-26 |
| RC-07 | `test-requirements.md` L77 | Optional: allow one template guard test (T-D04) | OQ-28 |
| RC-08 | CLAUDE.md (new, at M1) | Create via `managing-agent-memory`: commands, the gate block, and a "Verifying your work" section (methodology M-06, M-09) | R-13 |
| RC-09 | `docs/.prepare/starter-orchestrator-prompt.md` § 0 | For future runs: "15 skills" (not 16); add "do not modify `.handoffs/`"; the archive step is already done | OQ-06 |

## 5. Files beyond the ten-file map (justification)

| File | Why | Decision |
|---|---|---|
| `archive/brainstorm-plan.v1.0-original.md` | Required by the mission (plan preservation) | mission § 9 |
| `delegation/S1-brainstorm-plan-revised.raw.md` | Verbatim S1 output, so the owner can audit what changed at integration. S3 reviewed this text. | D-15 |
| `delegation/S2-security-verification.md` | S2's assigned output. Writing to a separate file let S1 and S2 run in parallel without concurrent writes to one file. | D-08 |
| `delegation/S3-critic-review.md` | S3's assigned output. It keeps the independent review separate from the orchestrator's integration. | D-08 |

These three files are evidence, not canonical documents. The owner may delete them after committing, because the git history would then preserve them. No other files were created. `git init -b main` was run once. Nothing was committed, branched, tagged, or pushed.

## 6. Next gate

1. The owner reads core-context → plan-review → brainstorm-plan-revised (§ 15 first, for what changed) → this report.
2. The owner writes approval lines for § 3.1 (and § 3.2 if ready) in decision-log § 4, and applies or rejects RC-01…RC-09 personally.
3. Only then does M1 start, in a new session, beginning in plan mode (methodology M-03).
