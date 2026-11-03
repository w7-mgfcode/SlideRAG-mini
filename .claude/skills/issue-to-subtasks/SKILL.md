---
name: issue-to-subtasks
description: >
  Turns a GitHub issue (number or URL) into an execution-ready 5-subtask
  work package. Resolves the issue across enterprise repos via gh CLI,
  traces parents, children, dependencies, blockers, milestones, builds a
  brief + source-of-truth + role-relevant scope, derives MVP and in/out
  scope, runs research-recommend-rerank scoring, executes a critic pass,
  then decomposes into 5 self-contained executable subtasks with
  acceptance criteria. Use when the user mentions a GitHub issue number
  (e.g. "issue 654"), pastes a GitHub issue URL, asks to plan, break
  down, decompose, scope out, or split into subtasks any GitHub issue,
  asks for an execution plan or delivery plan for an issue, references
  gh issue view, asks to triage or analyze a GitHub issue, or wants to
  turn a ticket, issue, or epic into actionable work. Stays
  delivery-oriented; avoids over-engineering and speculative roadmaps.
allowed-tools: Read, Write, Bash, Grep, Glob, WebFetch
---

# Issue to Subtasks

Transform a single GitHub issue into a clean, review-ready, 5-subtask execution package.

## Overview

This skill is invoked when a user references a specific GitHub issue (by number or URL) and wants it decomposed into actionable work. It follows a strict pipeline that **resolves → enriches → analyzes → researches → critiques → decomposes**, presenting everything for user review before any GitHub write actions.

Core philosophy: **brief, source-of-truth-anchored, role-relevant**. Never bloat. Never speculate. Never silently expand scope.

## Quick Start

```
User: "Break down issue 654"
                    │
                    ▼
1. Run `scripts/resolve_issue.sh 654` to find candidate repositories
2. If multiple match → present interactive shortlist, let user pick
3. Run `scripts/fetch_issue_graph.sh <repo> <issue>` for full context
4. Run `scripts/score_directions.py` after drafting candidate directions
5. Apply critic checklist from `references/critic-checklist.md`
6. Fill in `templates/output-package.md` with the 5 subtasks
7. Present to user → wait for approval before any write actions
```

## The Pipeline (MANDATORY ORDER)

```
RESOLVE TARGET ISSUE
        │
        ▼
DISCOVER ACCESSIBLE REPOSITORIES (gh CLI)
        │
        ▼
SELECT REPOSITORY / ISSUE (interactive if ambiguous)
        │
        ▼
LOAD ASSIGNEE + OPEN-ISSUE CONTEXT
        │
        ▼
TRACE ISSUE HISTORY / PARENT LINKS / RELATED WORK
        │
        ▼
BUILD DELIVERY CONTEXT (milestone / risks / blockers / dependencies)
        │
        ▼
EXTRACT BRIEF / SOURCE OF TRUTH / ROLE-RELEVANT SCOPE
        │
        ▼
RESEARCH → RECOMMEND → RERANK
        │
        ▼
RUN CRITIC PASS  ◄──── (multi-agent critique principles)
        │
        ▼
PRODUCE 5 EXECUTABLE SUBTASKS
        │
        ▼
PRESENT FOR USER REVIEW (no writes yet)
```

Progress checklist Claude SHOULD track during execution:

```
- [ ] Step 1: Issue resolved (URL or number → confirmed repo + issue)
- [ ] Step 2: Issue graph fetched (parents, children, blockers, PRs, comments)
- [ ] Step 3: Delivery context built (milestone, risks, deps)
- [ ] Step 4: Brief / source-of-truth / role-relevant scope extracted
- [ ] Step 5: Candidate directions scored and reranked
- [ ] Step 6: Critic pass executed against checklist
- [ ] Step 7: 5 subtasks drafted with acceptance criteria
- [ ] Step 8: Output package presented to user for review
```

---

## Step 1 — Resolve the Target Issue

If the user provides a **full URL** like `https://github.com/org/repo/issues/654`, parse it directly. Skip to Step 2 with that repo+issue.

If the user provides **only a number** (e.g. `issue 654`, `654`, `#654`), the issue could exist in any accessible repo. Run:

```bash
bash scripts/resolve_issue.sh 654
```

This script lists every repo accessible via `gh repo list` (current user + every org they belong to), checks which contain an issue with that number, and prints a numbered shortlist.

**MUST**: If more than one repo matches, present the shortlist verbatim and ask the user to pick. **Never guess.** Example presentation:

```
Issue #654 found in 3 repos:
  1. acme/api-gateway     — "Rate limiter blocks legit traffic"  (open, 2 days ago)
  2. acme/billing         — "Stripe webhook retries"               (open, 1 week ago)
  3. acme/internal-tools  — "Migrate legacy CLI to v2"             (closed)

Which one?
```

If exactly one repo matches → confirm it inline (`Working on acme/api-gateway#654`) and continue.

If zero repos match → tell the user, suggest possible reasons (typo, no `gh` auth, private repo not in their list), and stop.

---

## Step 2 — Discover Accessible Repositories (when needed)

If the user is choosing between repos, or the issue context references work in *other* repos that may need cross-checking, surface the accessible repo list:

```bash
bash scripts/list_repos.sh
```

Keep this concise. The goal is helping the user choose, not enumerating their entire org.

---

## Step 3 — Load Assignee & Open-Issue Context

Once repo + issue are confirmed, fetch the full delivery picture:

```bash
bash scripts/fetch_issue_graph.sh <owner/repo> <issue_number>
```

This single script returns JSON containing:

- The target issue: title, body, labels, assignees, milestone, state, projects
- Linked PRs (open and closed)
- Issues that reference this one (`gh issue list --search "654 in:body"`)
- Issues this one references (parsed from body + comments)
- All open issues assigned to the same user(s)
- Comment timeline (filter for substantive scope changes / decisions)

Read the output. Pay particular attention to:

- **Parent/epic links** (look for `Parent issue: #N`, `Epic: #N`, GitHub native `Tasklist` parents)
- **Blocked-by / depends-on** mentions
- **"Closes #N" / "Fixes #N"** in linked PRs
- **Historical comments** that materially changed scope or deferred decisions
- **Previous failed attempts** (closed PRs that referenced this issue)

---

## Step 4 — Build Delivery Context

Synthesize what was loaded into four delivery dimensions. Use `templates/delivery-context.md` as the working scaffold.

### Milestone
- Which milestone (if any)
- Whether the issue is milestone-critical
- Whether timing affects scope (e.g. "must ship before X")

### Risks
- Delivery risk (will it land on time?)
- Technical risk (is the approach sound?)
- Sequencing risk (does order matter?)
- Dependency risk (anything fragile upstream?)
- Ownership risk (is anyone actually owning this?)

### Blockers
- Explicit (mentioned in body/comments)
- Implied (missing decisions, missing infra access, missing validation)

### Dependencies
- Parent issues
- Upstream work (must finish first)
- Downstream consumers (will break / be unblocked when this lands)
- Sequencing requirements

---

## Step 5 — Extract the Core Decision Frame

Three sections must always appear, regardless of issue type:

### Brief
- Short explanation of what the issue is *really* about (not just the title)
- What outcome actually matters
- What kind of issue it is (bug fix / feature / refactor / spike / doc / infra / etc.)

### Source of Truth
- Which documents, issue comments, PRs, files, or repo paths matter most
- What should be treated as authoritative
- What is only supporting context (label as such)

### Role-Relevant Output
Tailor the output to the inferred user role:

- **Engineering lead** → emphasize sequencing, owner assignment, milestone fit
- **Implementer** → emphasize scope boundary, exact file paths, acceptance criteria
- **Reviewer** → emphasize what to verify, regression surface
- **Infra / platform owner** → emphasize blast radius, rollback, observability
- **Other** → ask one clarifying question if role isn't inferable from context

Skip detail that the user's role wouldn't act on.

---

## Step 6 — Derive Planning Primitives

For each issue, derive these primitives. They feed directly into the 5 subtasks. Keep each tight.

- **Bulletpoints** — short execution / scope / blocker / dependency bullets
- **Documentation references** — exact docs, comments, PRs, file paths worth reading next
- **Terms** — domain vocabulary that must stay consistent across subtasks
- **Minimum MVP** — smallest useful delivery slice; what proof is required; what can defer safely
- **Pipeline** — likely execution flow, validation path, review/merge path
- **Scope** — in scope / out of scope / not yet decided / intentionally deferred

---

## Step 7 — Research, Recommend, Rerank

Run the structured evaluation:

### Research
Gather only what materially improves decision quality:
1. Internal first: issue, repo, related PRs, project board, ownership files (`CODEOWNERS`)
2. Then external official/vendor docs only when the issue depends on them
3. Stop. Don't go fishing.

### Recommend
Identify the best practical next direction. Stay inside real constraints (repo conventions, milestone window, ownership reality). Avoid speculative big-design answers.

### Rerank with a Score System

Use the script:

```bash
python3 scripts/score_directions.py < candidates.json
```

Or apply manually using these dimensions (each scored 1–5):

| Dimension | What it measures |
|---|---|
| **Value** | Outcome impact for the user / stakeholder |
| **Risk** | Probability of failure or rework (lower = better, invert when scoring) |
| **Readiness** | Are upstreams done, decisions made, owners present? |
| **Dependency load** | How many other things must move first (lower = better, invert) |
| **Validation ease** | Can this be verified cleanly? |
| **Rollback safety** | If wrong, how cheaply can it be undone? |
| **Evidence strength** | How well-grounded is this in source-of-truth? |

Rerank candidate directions / subtask order accordingly. Show the table in the final output.

---

## Step 8 — Run the Critic Pass

This is non-negotiable. Multi-agent critique reliably catches scope creep, weak source-of-truth anchoring, and over-engineering that single-pass planning misses.

Apply `references/critic-checklist.md` against the draft. The critic checks:

- Scope creep (new asks not in the issue)
- Missing blockers
- Weak source-of-truth anchoring (claims without citation)
- Dependency mistakes
- Overconfident claims
- Over-engineering (multi-week plans where a one-day fix exists)
- Mismatch between milestone urgency and proposed scope
- Whether each subtask is truly executable and reviewable

If the user attached a specific critic document, use that as the additional lens.

If the critic pass surfaces material problems → **revise the draft once** before producing the 5 subtasks. Do not loop indefinitely; one revision round is enough (research shows critique-revision gains saturate at 1–2 rounds).

---

## Step 9 — Produce Exactly 5 Subtasks

Use `templates/subtask.md` for each. Five is the number — not four, not six. If the issue genuinely doesn't decompose into 5, say so explicitly and propose a different shape (e.g. "this is a single 1-day fix; here's the one task" or "this issue is an epic and needs 3 sub-issues first").

Each subtask MUST include:

- **Title** (imperative, ≤ 80 chars)
- **Purpose** (1 sentence)
- **Scope** (bullets — what's IN)
- **Out of scope** (bullets — what's explicitly NOT this subtask)
- **Dependencies** (which other subtasks or external work block this)
- **Risks / blockers** (specific, not generic)
- **Acceptance criteria** (testable, observable)
- **Why it matters now** (1 line linking back to source-of-truth)

Subtasks must be:

- Bullet-based (not prose walls)
- Concise but rich
- Self-contained (an implementer could pick one up without re-reading the issue)
- Not over-engineered

---

## Step 10 — Present for Review

Output the full package using `templates/output-package.md`. It contains nine sections in this order:

1. Brief
2. Source of truth
3. Issue context
4. Risks / blockers / dependencies
5. Role-relevant scope (in / out / MVP / pipeline)
6. Research / recommendation / rerank table
7. Critic findings
8. Proposed 5 subtasks
9. Final recommendation

End with a clear handoff:

> **Ready for your review.** I can edit, reorder, drop, or merge any subtask. Once you approve, I can create them as GitHub sub-issues, post a comment on the parent, or hand them to a project board — your call.

**MUST NOT** create issues, post comments, or take any other GitHub write action without explicit approval.

---

## Constraints (HARD)

- **NEVER** guess which repo an issue belongs to. Use the resolver script. If ambiguous, ask.
- **NEVER** silently expand scope beyond what the issue and its source-of-truth justify.
- **NEVER** produce subtasks that depend on undocumented assumptions — flag the assumption instead.
- **NEVER** skip the critic pass.
- **NEVER** take a GitHub write action (create issue, comment, label, assign, close) without user approval.
- **MUST** prefer source-of-truth-backed conclusions over plausible-sounding ones.
- **MUST** prefer practical delivery framing over theoretical completeness.
- **MUST** keep outputs concise. Five subtasks. Nine output sections. Done.

## Dependencies

Required tools the agent must have available in the environment:

| Tool | Install | Purpose |
|---|---|---|
| `gh` | https://cli.github.com (`brew install gh` / `apt install gh`) | All GitHub queries |
| `jq` | `brew install jq` / `apt install jq` | JSON parsing in scripts |
| `python3` | preinstalled | Running `score_directions.py` |

`gh` MUST be authenticated: run `gh auth status` first; if not authenticated, instruct user to run `gh auth login` and stop.

## Reference Files

- [references/critic-checklist.md](references/critic-checklist.md) — full multi-agent critic checklist applied in Step 8
- [references/scoring-rubric.md](references/scoring-rubric.md) — detailed rubric for the 7 rerank dimensions
- [references/role-output-guide.md](references/role-output-guide.md) — what to emphasize per inferred user role
- [scripts/resolve_issue.sh](scripts/resolve_issue.sh) — find which repo(s) contain a given issue number
- [scripts/list_repos.sh](scripts/list_repos.sh) — enumerate accessible repos
- [scripts/fetch_issue_graph.sh](scripts/fetch_issue_graph.sh) — full issue + linked-work JSON dump
- [scripts/score_directions.py](scripts/score_directions.py) — rerank candidate directions deterministically
- [templates/output-package.md](templates/output-package.md) — final 9-section output template
- [templates/subtask.md](templates/subtask.md) — single-subtask template
- [templates/delivery-context.md](templates/delivery-context.md) — Step-4 working scaffold
- [assets/example-output.md](assets/example-output.md) — fully-worked example for reference

## Quick Reference Table

| Task | Command / Method |
|---|---|
| Resolve a bare issue number | `bash scripts/resolve_issue.sh <N>` |
| List accessible repos | `bash scripts/list_repos.sh` |
| Fetch full issue graph | `bash scripts/fetch_issue_graph.sh <owner/repo> <N>` |
| Score directions | `python3 scripts/score_directions.py < input.json` |
| Critic checklist | `references/critic-checklist.md` |
| Final output shape | `templates/output-package.md` |
