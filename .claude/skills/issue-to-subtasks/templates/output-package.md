# Issue {{ISSUE_NUMBER}} — Execution Package

> Repository: `{{OWNER/REPO}}` · Issue: [#{{ISSUE_NUMBER}}]({{ISSUE_URL}}) · Generated: {{DATE}}

---

## 1. Brief

- **What this issue is really about:** {{1-2 sentences capturing the actual outcome that matters, not just the title}}
- **Type:** {{bug fix / feature / refactor / spike / doc / infra / migration / other}}
- **Why it matters now:** {{1 sentence linking to milestone or stakeholder need}}

## 2. Source of Truth

Authoritative:

- {{File path / issue / PR / doc — the things to treat as canonical}}
- {{...}}

Supporting context (not authoritative — corroborates):

- {{...}}

Not source-of-truth (mentioned in comments but not actionable):

- {{...}}

## 3. Issue Context

| Field | Value |
|---|---|
| State | {{open / closed}} |
| Milestone | {{name or "—"}} |
| Assignees | {{@user1, @user2}} |
| Labels | {{label1, label2}} |
| Project / Board | {{project name or "—"}} |
| Parent / Epic | {{#N or "—"}} |
| Linked PRs | {{#N (state), ...}} |
| Referenced issues | {{#N, #N, ...}} |
| Created / Updated | {{date}} / {{date}} |

**Sibling open issues from same assignees** (workload context):

- {{#N — title — milestone}}
- {{...}}

## 4. Risks / Blockers / Dependencies

**Risks:**

- {{Specific risk — not "this could fail"}}
- {{...}}

**Blockers:**

- ❌ {{Hard blocker — work cannot start}}
- ⚠️ {{Soft blocker — work can start but stall mid-flight}}

**Dependencies:**

- **Upstream (must finish first):** {{#N, external work}}
- **Downstream (will be unblocked / break):** {{#N, system X}}
- **Sequencing constraint:** {{e.g. "must land before milestone freeze"}}

## 5. Role-Relevant Scope

> Framed for: **{{inferred role}}**

**In scope:**

- {{...}}

**Out of scope (explicit):**

- {{...}}

**Minimum MVP:**

- {{Smallest useful slice}}
- {{Required proof / test / observation to declare done}}

**Pipeline:**

```
{{step 1}} → {{step 2}} → {{step 3}} → {{validation}} → {{review/merge}}
```

**Not yet decided:**

- {{Open question that doesn't block start but needs answer before merge}}

**Intentionally deferred:**

- {{Adjacent work that surfaced but isn't this issue}}

## 6. Research / Recommendation / Rerank

**Candidate directions considered:**

| ID | Description | Origin |
|---|---|---|
| A | {{description}} | {{issue body / comment / PR / external doc}} |
| B | {{...}} | {{...}} |
| C | {{...}} | {{...}} |

**Rerank (using `score_directions.py`):**

{{paste the table_markdown output from the scoring script here, OR fill manually using references/scoring-rubric.md}}

**Recommended path:** **{{winning direction}}**

**Why:** {{1-2 sentences tying the recommendation to the score table and source-of-truth}}

## 7. Critic Findings

{{If all checks passed: "All checks passed. No revisions applied."}}

{{Otherwise:}}

- [Section X] ⚠️/❌ {{specific finding and what was changed in response}}
- {{...}}

**Revisions applied:** {{summary of what was changed in the draft after the critic pass, OR "none"}}

## 8. Proposed 5 Subtasks

> {{If the issue genuinely doesn't fit a 5-subtask shape, replace this section with: "This issue decomposes into N subtasks instead of 5 because {{reason}}. Here they are." and proceed.}}

### Subtask 1 — {{title}}

- **Purpose:** {{1 sentence}}
- **Scope:**
  - {{bullet}}
  - {{bullet}}
- **Out of scope:**
  - {{bullet}}
- **Dependencies:** {{none / Subtask N / external work}}
- **Risks / blockers:** {{specific}}
- **Acceptance criteria:**
  - {{testable / observable}}
  - {{...}}
- **Why it matters now:** {{1 line tying back to source-of-truth}}

### Subtask 2 — {{title}}

(same shape)

### Subtask 3 — {{title}}

(same shape)

### Subtask 4 — {{title}}

(same shape)

### Subtask 5 — {{title}}

(same shape)

**Sequencing summary:**

```
Subtask 1 ──┬──► Subtask 3 ──► Subtask 5
            │
Subtask 2 ──┴──► Subtask 4
```

(Adjust the diagram to reflect actual dependencies. If all 5 are parallel, say so.)

## 9. Final Recommendation

- **What should happen next:** {{single concrete next action}}
- **What should be reviewed first:** {{which subtask should land before others lock in}}
- **What must NOT be overbuilt:** {{specific anti-scope-creep guardrail}}

---

**Ready for your review.** I can edit, reorder, drop, or merge any subtask. Once you approve, I can:

- Create them as GitHub sub-issues linked to the parent
- Post a comment on the parent issue summarizing the breakdown
- Hand them to a project board column
- Or just hand the markdown to you to paste manually

Your call. **No GitHub write actions taken yet.**
