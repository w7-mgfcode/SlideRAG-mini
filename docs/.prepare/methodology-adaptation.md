# Methodology Adaptation — AI-Native SDLC Playbook → SlideRAG Mini

| Field | Value |
|---|---|
| Document ID | PREP-06 |
| Title | Methodology Adaptation |
| Revision | r2 |
| Status | Historical methodology with approved Option C workflow override |
| Owner | Orchestrator; approver: repository owner |
| Last updated | 2026-11-03 |
| Evidence baseline | SR-20 at upstream commit `4a48004`, retrieved 2026-11-02 |
| Core-context revision used | r1 for historical body; r3 for current override |
| Dependencies | source-register.md r3, core-context.md r3, execution-plan.md r1 |
| Supersedes | — |
| Approval record | decision-log.md § 4, D-16…D-21; no blanket approval of historical process |
| Change summary | r1: initial adaptation. r2: current Option C workflow override; historical rationale preserved |

## Current delivery override — 2026-11-03

[EXEC-01](execution-plan.md) governs after owner approval. Keep its plan, decision log, and acceptance checklist as the active working set. Do not require new milestone planning documents, repeated rubric scoring, or another S1/S2/S3 cycle. Historical delegation/process choices do not block implementation.

Retain the owner-requested GitHub hierarchy with outcome-sized issues/PRs. Minimal offline CI belongs within the M1 outcome under the later GitHub plan, using `chore(ci)`; this supersedes the historical “no CI” adaptation below. Preparation/bootstrap/AWS provisioning is accounted for separately; actual implementation time and variance remain visible. The tables below record the original adaptation, not competing current instructions.

## Source and access

- **Fetched successfully** on 2026-11-02 as raw markdown: 1,374 lines, upstream commit `4a48004` (2026-09-03), sha256 `37dbc5d6c40d`. Recorded as SR-20.
- **Limitation:** per its own header (L3–6), the file is a community transcription of the Anthropic Claude Academy course. Fidelity to the official course is unverified. Line references below point to that file.
- The playbook is a **methodology source only**. Nothing in it is evidence about SlideRAG Mini.
- **Not claimed:** the playbook does not prescribe this package's ten-file structure, the weighted rubric, or the S1/S2/S3 topology. Those are owner choices (mission § 0, D-04, D-05).

## Scale translation

The playbook assumes an organisation: product owners, policy owners, platform teams, CI, managed settings. SlideRAG Mini has **one person**, an **8-hour build**, and **no remote or CI yet**. The general rule here: adopt the *artifact chain* and the *human gate*, and drop the organisational machinery.

| Playbook role | Here |
|---|---|
| Product owner, tech lead, policy owner, release manager | The repository owner (one person, all roles) |
| intent.md → spec.md → plan.md | `brainstorm-plan.md` (intent + design, v1.0) → `brainstorm-plan-revised.md` (spec-grade, proposed) → per-milestone plans in `.agents/plans/` during the build |
| Committed artifact as stage trigger | Owner "Approved by owner" line (D-02), then the owner commits |

## Principles

| # | Principle | Source (SR-20) | Decision | Project-specific application | Required artifact / workflow | Verification | Limitations / prerequisites |
|---|---|---|---|---|---|---|---|
| M-01 | **Intent-driven planning.** Capture what is wanted, why, constraints, and open questions in a human- and machine-readable file that the owner corrects. | Stage 1, L144–240 (template L181–193) | **Adopt (adapted)** | No separate `intent.md`. The problem, outcomes, constraints, and open questions live in core-context.md §§ 1–6 and open-questions.md. | core-context.md, open-questions.md | Owner reads core-context § 1–2 and confirms intent. Recorded as an approval line. | Intent was written by an agent from the owner's plan. Owner correction is the gate (L174, L196). |
| M-02 | **Requirements and design before implementation**, with areas of concern flagged | Stage 2, L241–320 (flagged concerns L262–264; example prompt asks to "describe clearly any areas of concern") | **Adopt** | `brainstorm-plan-revised.md` plays the role of spec.md: FR/NFR with IDs, interfaces, data lifecycle, security. Flagged concerns = plan-review.md findings + open questions. | brainstorm-plan-revised.md, plan-review.md | Every MUST HAVE maps to ≥ 1 FR, and every FR to a QG or a manual check (traceability table) | "Org skills for brand/compliance" do not exist. `.claude/rules/` serve as the policy layer. |
| M-03 | **Explicit implementation plan**: files that change, order of work, risks, proof. Iterate until someone who never saw the conversation could implement from it. | Plan mode, L321–374 (L338–341, example L349–368) | **Adopt** | Each milestone in the revised plan lists files, order, risks, and proof commands. During the build, each milestone starts in Claude Code plan mode and saves the accepted plan to `.agents/plans/M<n>.md`. | brainstorm-plan-revised.md § implementation plan (conditional on blockers); `.agents/plans/` at build time | Milestone exit command passes (e.g. `uv run pytest -m "not integration"`) | Full plan only once blockers R-01/R-02 are decided. Otherwise a conditional outline. |
| M-04 | **Version-controlled artifacts and a traceable decision chain** ("who asked, what was produced, who approved") | Intro L83–85; Stage 1 governance L196 | **Adopt (deferred enforcement)** | `git init` done. Until the owner commits, traceability is manual: revision labels, `docs-baseline-r1`, decision-log IDs. The first owner commit becomes the audit anchor. | README baseline table, decision-log.md | Owner commits the package. Revision labels match the README table. | No SHA exists (D-03). Labels are honour-system. |
| M-05 | **One named source of truth per artifact** | Plan mode § Legacy systems, L381–428 (L385–389) | **Adopt** | core-context § 9 names the SoT per artifact. The rule SR-03 names v1.0. A switch to the revised plan is an explicit owner decision (OQ-05). | core-context.md § 9; readiness-report proposed rule change | No artifact has two competing SoTs without a recorded conflict | — |
| M-06 | **Shared repository context (CLAUDE.md)** under a page, with commands and things agents get wrong | CLAUDE.md, L435–519 (L448–452) | **Defer to M1** | There are no commands to document yet. core-context.md serves as interim shared context for agent sessions. Create CLAUDE.md at scaffold (via `managing-agent-memory`) with the `ruff`/`pytest` commands. | R-13; CLAUDE.md at M1 | CLAUDE.md exists, is under ~1 page, and lists the verification commands | Mission forbids creating CLAUDE.md in this phase |
| M-07 | **Skills as institutional knowledge; hooks as the deterministic layer behind them** | Skills, L520–622 (advisory vs deterministic L563; build hooks L568–577) | **Adopt existing, add nothing** | `.claude/rules/` + project skills (`commit-format-check`, `library-claim-verify`, `audit-rules-drift`) are the policy layer. The commit hook is the deterministic layer. No new skills or hooks are proposed for the 8 h build. | none new; rule fixes in readiness-report | `audit-rules-drift` after M1 | Rules have drift (F-12). Fixes are proposals only. |
| M-08 | **Scoped delegation, isolated sessions; 2–3 parallel sessions; ceiling = what one person can review** | Parallel sessions, L623–710 (L646–648) | **Adopt (adapted isolation)** | Three Herdr Claude sessions in named tabs, each with a written packet, disjoint write paths, and a completion report. Worktree isolation is replaced by disjoint paths plus orchestrator diff review (D-09). | delegation-manifest.md | Orchestrator checks that each session wrote only its assigned paths | Worktrees need a branch and commit (forbidden now) |
| M-09 | **Give the agent a feedback loop**: one-command checks, quantified targets, failing test first for bugs, protect the check from being weakened | Feedback loop, L711–796 (L729–735) | **Adopt** | Gates `ruff` + `pytest` as single commands (SR-05). Each milestone gets a quantified exit target. The QG-06/07 tests are load-bearing (SR-05 L57–59). The test-file-protection hook is **optional** (not proposed for 8 h). | Revised plan milestone exits; CLAUDE.md "Verifying your work" at M1 | Exit commands are pasted in build session reports | — |
| M-10 | **Continuous evals in CI** (20–50 tasks, gate config changes) | Evals, L797–891 (L814–818) | **Adapt down** | Five eval questions as pytest parameters, integration-marked. No CI eval suite and no eval framework (SR-03 L56). | test-requirements eval set | Integration run with a key, results pasted | Five questions cannot measure regression statistically |
| M-11 | **Human accountability and approval gates; separation of duties** (the authoring agent cannot approve its own work) | Intro L85; PR review L934; approval hooks L979–1132 (L997) | **Adopt** | Owner-only approval (D-02). S3 critic reviews S1/S2 and the orchestrator's scores. The orchestrator reviews S3. No agent self-approves. | decision-log § 4; plan-review § independent review | decision-log § 4 holds only owner lines | No branch protection (no remote) |
| M-12 | **AI in the PR review loop (REVIEW.md)** | PR review, L892–978 | **Defer** | Useful once a GitHub remote exists (OQ-10). Not in the 8 h budget. | none now | — | No remote |
| M-13 | **CI/CD integration, rollback rehearsed** | CI/CD, L1133–1215 (rollback L1154) | **Adopt the rollback idea only** | No CI in scope. The deployment runbook should include a one-command rollback to the previous image tag (R-10). | Revised plan deploy runbook | Rollback rehearsed once on EC2 before the demo | Pipeline automation inapplicable in 8 h |
| M-14 | **Closing the loop on metrics** (control bands, autonomous intents) | Metrics, L1216–1315 | **Inapplicable** | Private demo. No production metrics and no on-call. | — | — | Revisit only if the app goes public (LATER) |

## Workflow change summary

1. **Before M1:** the owner reviews this package and writes approval lines (M-01, M-02, M-11).
2. **At M1:** CLAUDE.md with commands (M-06). Pin Python. Verify model/library claims (M-02 flagged concerns).
3. **Each milestone:** plan mode → `.agents/plans/M<n>.md` → implement → exit command → commit (M-03, M-09).
4. **Before v0.1.0:** DoD on EC2 + QG-09 manual check (SR-08 L11–17).
