# Delivery Context (Working Scaffold for Step 4)

Use this as a private working document while you build the brief. It is NOT part of the final output — it feeds into Sections 1-5 of `output-package.md`. Discard or roll into the package when done.

---

## Issue identity

- **Repo:** `{{owner/repo}}`
- **Issue:** `#{{N}}` — {{title}}
- **URL:** {{url}}
- **State:** {{open/closed}}
- **Created:** {{date}} · **Last updated:** {{date}}
- **Author:** @{{user}}

## Milestone

- **Milestone name:** {{name or none}}
- **Milestone-critical?** {{yes/no/unclear}}
- **Timing pressure:** {{e.g. "must ship before X freeze", "no fixed date", "blocks N other issues"}}
- **Notes from milestone discussion:** {{quote relevant comments}}

## Risks

| Type | Risk | Severity (1–5) | Notes |
|---|---|---|---|
| Delivery | {{...}} | {{N}} | {{...}} |
| Technical | {{...}} | {{N}} | {{...}} |
| Sequencing | {{...}} | {{N}} | {{...}} |
| Dependency | {{...}} | {{N}} | {{...}} |
| Ownership | {{...}} | {{N}} | {{...}} |

## Blockers

**Hard blockers (work cannot start):**

- ❌ {{...}}

**Soft blockers (work can start but stalls mid-flight):**

- ⚠️ {{...}}

**Implied blockers (not stated but implied by source-of-truth):**

- {{e.g. "missing decision from @owner on whether to support legacy API"}}

## Dependencies

**Parent / epic:** {{#N or none}}

**Upstream (this depends on):**

- {{#N — title — state}}
- {{external: PR / vendor / decision}}

**Downstream (depends on this):**

- {{#N — title — state}}

**Cross-repo work:**

- {{repo#N if visible}}

## Source-of-truth inventory

Walk every claim in your draft brief against this list:

- [ ] Issue body (canonical)
- [ ] Issue comments — pick which ones are decision-bearing vs noise
- [ ] Linked PRs — open and closed
- [ ] Referenced files in repo (paths from body/comments)
- [ ] Parent epic body (if present)
- [ ] CODEOWNERS / ownership signal
- [ ] Project board context (if visible)
- [ ] Sibling open issues (workload signal only — not source-of-truth for THIS issue)
- [ ] External docs / vendor pages (only if issue cites them directly)

## Inferred user role

- **Best guess:** {{engineering lead / implementer / reviewer / infra owner}}
- **Signal used:** {{...}}
- **Confidence:** {{high / medium / low — if low, ask one clarifying question}}

## Open questions (cannot proceed without answers)

- {{...}}
- {{...}}

## Questions that don't block but should be flagged in output

- {{...}}

## Candidate directions (to feed into Step 7)

| ID | Description | Rough origin |
|---|---|---|
| A | {{...}} | {{issue body / comment / PR / our analysis}} |
| B | {{...}} | {{...}} |
| C | {{...}} | {{...}} |

When done with this scaffold, hand A/B/C/... to `score_directions.py` along with rubric scores.
