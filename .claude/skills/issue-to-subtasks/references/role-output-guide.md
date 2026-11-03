# Role Output Guide

The "Role-relevant output" section (Step 5 of the pipeline) tailors the brief and subtask emphasis to the inferred user role. This guide defines what each role cares about, what to emphasize, and what to drop.

## How to infer the role

In order of signal strength:

1. **Explicit statement** — user says "I'm the tech lead", "I'll be implementing this", "I'm reviewing this PR"
2. **Issue assignee match** — if the user is logged into `gh` as the assignee, they are likely the implementer
3. **Comment patterns** — leadership comments ("let's prioritize this for M3") suggest engineering lead
4. **Path of the conversation** — "split this so I can hand to the team" → eng lead; "what should I open the PR with" → implementer
5. **Default fallback** — engineering lead, since that's the most common user of issue-decomposition tooling

If signal is weak, ask **one** clarifying question:

> Who's picking these subtasks up — you, or someone on your team?

---

## Engineering lead

**Cares about:** sequencing, owner assignment, milestone fit, parallelism opportunities, risk surface, milestone-critical path

**Emphasize:**

- Which subtasks can be parallelized vs sequenced
- Suggested owner per subtask (based on assignees, recent contributors, CODEOWNERS)
- Milestone risk if any subtask slips
- Cross-team / cross-repo coordination flags
- Total estimated effort range (e.g. "5–8 days across 2 engineers")

**Drop:**

- File-level implementation guidance unless the lead is also implementing
- Inline code snippets
- Verbose acceptance criteria — keep them tight

---

## Implementer

**Cares about:** exact scope boundary, files to touch, edge cases, test obligations, what NOT to do

**Emphasize:**

- Specific file paths or modules to modify (if visible from issue / source-of-truth)
- Tests that must pass / be added
- Edge cases pulled from comment history
- Concrete acceptance criteria — testable, observable
- "Out of scope" with examples ("don't touch X, don't refactor Y")
- Build / lint / CI commands the implementer should run before the PR

**Drop:**

- Strategic / sequencing context beyond the immediate subtask
- Owner assignment guidance
- Project-level milestone framing — give them the work, not the org context

---

## Reviewer

**Cares about:** what to verify, regression surface, what changed semantically, what could go wrong, what to push back on

**Emphasize:**

- Regression surface — which existing behavior could break
- Test coverage expectations (was this tested at the right layer?)
- Performance / security / observability implications
- Style of feedback expected (architectural, line-level, smoke-test only)
- Specific review questions tied to acceptance criteria

**Drop:**

- Implementation details — that's the implementer's job to write
- Future-work plans
- Owner assignment (reviewer didn't choose the assignee)

---

## Infra / platform owner

**Cares about:** blast radius, rollback path, observability, capacity, tenant isolation, on-call burden

**Emphasize:**

- What changes in the running system (config, schema, traffic shape)
- Rollback path — explicit, tested, fast
- Metrics / alerts that should exist before vs after
- Capacity implications (CPU, memory, GPU, network, storage)
- On-call playbook updates required
- Migration ordering (forward vs back compatibility windows)

**Drop:**

- Application-layer feature work unless it changes infra contract
- UI / UX details
- Detailed test fixtures

---

## Other / unclear

If you can't infer the role and the user doesn't clarify after one ask, default to **engineering lead** framing — it's the broadest baseline and least likely to mislead. Add a short note at the top of the output:

> Output framed for an engineering-lead role. Tell me if you're the implementer / reviewer / infra owner and I'll re-frame.

---

## Cross-role rules

These apply regardless of inferred role:

- **Source of truth section** is identical across roles — it's the anchor.
- **Critic findings** are shown to all roles. They're shorter for implementers (just risks to their subtask) and fuller for leads (full eight-section output).
- **Acceptance criteria** are testable for all roles, but the *level* differs: implementer gets unit-level, lead gets feature-level, infra gets system-level.
