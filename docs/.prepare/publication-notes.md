# Publication provenance

This public preparation package preserves the governing Option C plan, the owner's existing approval record, and historical analysis. No application acceptance or deployment result is implied by publication.

## Local-only records and public summaries

| Local source | Public account | What it establishes |
|---|---|---|
| Raw S1 architecture draft (SR-34) | [Delegation completion reports](delegation-manifest.md#51-completion-reports-verbatim-from-each-sessions-output), [integrated proposal](brainstorm-plan-revised.md) | Historical module, ingestion, and retrieval proposals; superseded where EXEC-01 differs |
| Raw S2 security draft (SR-35) | [Delegation manifest](delegation-manifest.md), [integrated proposal](brainstorm-plan-revised.md) §§ 8–10 | Proposed upload limits, security boundaries, deployment precautions and verification cases; not executed tests |
| Raw S3 critique (SR-36) | [Plan review](plan-review.md) §§ 6–7 and [integrated proposal](brainstorm-plan-revised.md) § 15 | Historical risk scores, contradictions and integration decisions; not independent runtime validation |
| Handoffs, agent memory and local settings (SR-12–15) | [Core context](core-context.md), [source register](source-register.md), [decision log](decision-log.md) | Dated state observations and the existing approval; no publication of machine credentials or raw session state |

These originals remain local and ignored. Their historical path/hash references are provenance identifiers, not public download links. The included completion reports are the historical orchestrator's record, not a fresh re-verification of those sessions. Current implementation authority is [EXEC-01](execution-plan.md); old unresolved proposals do not add approval blockers.

## Original archive

The byte-exact original `archive/brainstorm-plan.v1.0-original.md` (SR-02, recorded SHA-256 prefix `2c576598359a`) is preserved locally and excluded from Git. The source register notes a real operator name and pasted stylesheet content, making that raw copy unsuitable for public reuse. The amended [brainstorm plan](brainstorm-plan.md) (SR-01, recorded prefix `8a5e41cc903a`) supplies the synthetic product and deck input. The historical changes reconstruct the diagram and replace the operator name; neither archive is runtime evidence.

The historical starter prompt replaces its machine-specific checkout path with a repository-relative description for publication. Its original is preserved in the ignored local handoff directory. No owner-approval line or original plan bytes were changed.

## Publication scope

Excluded: `.env` values, local Claude settings, raw delegation records, handoffs, legacy ZIP assets, runtime data and the original archive. Included: project policies/tooling, preparation documents, the current execution plan and this summary. The initial bootstrap is documentation only; Python lint/tests, live model calls and EC2 checks remain future work under M1–M4.

Preparation is accounted for separately. The implementation allocation is 480 minutes: 60 + 150 + 105 + 75 for M1–M4, 30 workflow, 60 reserve. These are timeboxes, not measured forecasts.
