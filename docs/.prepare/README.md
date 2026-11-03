# docs/.prepare — Preparation Workspace

| Field | Value |
|---|---|
| Document ID | PREP-01 |
| Revision | r3.1 (publication clarification) |
| Status | Current index; Option C direction approved |
| Last updated | 2026-11-03 |
| Baseline | docs-baseline-r3 |
| Approval | [decision-log.md § 4](decision-log.md#4-owner-approval-record), D-16…D-21 |

## Start here

[execution-plan.md](execution-plan.md) is the governing plan: Option C, a fixed-configuration MVP with explicit recovery. The owner approved the preceding architectural recommendation in conversation on 2026-11-03. This is not blanket approval of every historical proposal.

The active working set is the execution plan, decision log, and acceptance checklist within the execution plan. No application has been implemented. The r3 approval session aligned planning/policy only. GitHub bootstrap is a separate authorized task; its issues and pull requests record publication progress.

## Current baseline

Manual revision labels are not commit SHAs. The r3 preparation baseline predates the first commit; Git history records publication from the initial documentation commit onward. Publication clarification r3.1 changes this index and provenance presentation only; EXEC-01, approvals, contracts, and acceptance gates are unchanged.

| Document | r1 baseline | r2 baseline | r3 baseline | Role |
|---|---|---|---|---|
| PREP-01 README.md | r1 | r2 | r3 | Current index |
| PREP-02 core-context.md | r1 | r2 | r3 | Current project/state summary |
| PREP-03 source-register.md | r1 | r2 | r3 | Dated evidence and approval sources |
| PREP-04 decision-log.md | r1 | r2 | r3 | Decisions and owner approval |
| PREP-05 open-questions.md | r1 | r2 | r3 | Current dispositions plus historical questions |
| PREP-06 methodology-adaptation.md | r1 | r1 | r2 | Historical methodology with current workflow override |

r1 → r2 integrated the delegated review. Its historical impact assessment remains in brainstorm-plan-revised.md § 15.4.

r2 → r3 records the approved Option C direction. Impact review:
- PREP-07 and PREP-08 remain historical review/proposal bodies, with a current-status notice.
- PREP-09 remains a historical delegation record; it does not mandate another delegation cycle.
- PREP-10 now distinguishes direction approval from pending operational evidence.
- Product/security/test rules and GitHub planning references use EXEC-01.
- No new delegation or independent review of these alignment edits is claimed.
- EXEC-01 is the one added execution document. It preserves prior analysis while avoiding a rewrite of the full lifecycle proposal.

## Index and authority

| Document | Purpose and current status |
|---|---|
| [execution-plan.md](execution-plan.md), EXEC-01 r1 | Governing Option C direction and acceptance checklist; implementation pending |
| [decision-log.md](decision-log.md), PREP-04 r3 | D-16…D-21 record current approval; earlier entries retain their historical status |
| [core-context.md](core-context.md), PREP-02 r3 | Entry point for current state and constraints |
| [readiness-report.md](readiness-report.md), PREP-10 r2 | Approved scope; runtime/account/deployment evidence pending; historical r1 report retained |
| [open-questions.md](open-questions.md), PREP-05 r3 | Settled preferences versus remaining evidence obligations |
| [source-register.md](source-register.md), PREP-03 r3 | Dated sources; old authority/line counts describe their original baseline |
| [brainstorm-plan.md](brainstorm-plan.md) | Preserved original product/deck input; conflicting execution choices superseded |
| [Original archive summary](publication-notes.md#original-archive) | Byte-exact original retained locally and excluded from publication |
| [brainstorm-plan-revised.md](brainstorm-plan-revised.md), PREP-08 | Historical full-lifecycle proposal; not governing or blanket-approved |
| [plan-review.md](plan-review.md), PREP-07 | Original findings and delegated review history |
| [methodology-adaptation.md](methodology-adaptation.md), PREP-06 r2 | Methodology reference; EXEC-01 governs current delivery |
| [delegation-manifest.md](delegation-manifest.md), PREP-09 | Historical packets and completion reports |
| [starter-orchestrator-prompt.md](starter-orchestrator-prompt.md) | Historical mission, not current execution authorization |

Raw delegation files, handoffs, and the original archive remain local evidence. They are ignored and uncommitted, so they are not preserved in Git history. [Publication notes](publication-notes.md) explain their public summaries and limits. Historical plain-text paths identify local sources, not files promised in this public repository.

## Ownership and approval

- Only the repository owner approves direction. An assistant may record explicit conversation approval faithfully; it may not manufacture approval or broaden its scope.
- Current approval is the exact owner message recorded in decision-log § 4. It does not assert that the owner independently reviewed every later transcription line.
- Historical `ready-for-human-review` statuses do not mean approval.
- Keep one writer per document. Preserve `brainstorm-plan.md` and `archive/` unchanged.
- Historical process choices do not create new M1 approval gates.
- Changes to core documents bump the baseline and require a concise downstream impact check.

## Next gate

Option C scope is approved for implementation. The next execution verifies operational prerequisites and begins M1 from EXEC-01. Approval is not proof that credentials, dependency compatibility, GitHub/bootstrap, AWS, or any acceptance test are complete. Record preparation separately and report timebox variance honestly.
