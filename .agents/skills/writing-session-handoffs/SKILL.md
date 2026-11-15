---
name: writing-session-handoffs
description: >
  Generates a structured session handoff document so the next session can resume
  without context loss. Gathers git state, extracts decisions with rationale,
  surfaces dead ends, and enforces that Next Step #1 is immediately actionable.
  Triggers on: "write a handoff", "session handoff", "end of session", "hand off
  to next session", "save session context". Do NOT use for: git commit messages,
  changelogs, PR descriptions, meeting notes, retrospectives.
---

# Writing Session Handoffs

## Overview

Automates end-of-session context capture into a structured `HANDOFF.md` that the
next session reads to resume work. Uses git state as the ground truth for "what
changed", then layers in decisions, dead ends, and open questions from the
conversation. The key quality gate: **Next Step #1 must be specific enough to
execute without reading anything else in the handoff.**

## Quick Start

```
User: "write a handoff"
```

The skill gathers git state, fills the template, validates Next Step #1, and
writes `HANDOFF.md` to the workspace root. Reports: *"Handoff written. Next
session should start by reading HANDOFF.md."*

## Resolve workspace and resources

- Resolve this shared `SKILL.md` from its discovered file path. Its template is
  [assets/templates/handoff-template.md](assets/templates/handoff-template.md),
  relative to this file's directory, not to the shell's current directory or a
  client wrapper. Read the template before rendering.
- For the target repository, resolve `handoff_root` with
  `git rev-parse --show-toplevel` from the requested working directory. This
  selects the current worktree root even when invoked from a subdirectory.
- If Git is unavailable or the directory is not a repository, use the user's
  explicit workspace root, otherwise the starting directory; disclose the lack
  of Git evidence. Do not guess a parent directory.
- Default output is `HANDOFF.md` under `handoff_root`. Honor a user-specified
  output path; resolve relative output paths against `handoff_root`, not the
  invocation directory. Do not change any other handoff or root pointer unless
  that update was requested. Synthetic checks use a disposable workspace and
  an explicit output path, leaving real session files untouched.

## When NOT to Write a Handoff

Unless the user explicitly requests a handoff, skip it when:
- **Session made no progress** — nothing to hand off. A blank handoff is worse than none.
- **Work is fully committed and self-explanatory** — git log + code tells the story.
- **Single-task session with no open threads** — if the task is done and nothing follows, a handoff is overhead.

**Rule of thumb:** Write a handoff when the next session would waste >5 minutes
figuring out where to start without one.

## Workflow

### Phase 1: Gather State

Collect raw data from the repository and conversation context.

**Git state (read-only, after resolving `handoff_root`):**

```bash
git -C "$handoff_root" status --short
git -C "$handoff_root" diff --stat
git -C "$handoff_root" diff --name-only
git -C "$handoff_root" diff --cached --stat
git -C "$handoff_root" diff --cached --name-only
git -C "$handoff_root" log --oneline -5
git -C "$handoff_root" branch --show-current
git -C "$handoff_root" remote
```

Remote names are sufficient; do not print remote URLs, which may contain
credentials. These commands do not fetch or verify remote state. Separate
staged, unstaged and untracked changes. Do not equate a clean Git status with
unchanged ignored handoffs. An unborn repository has no commit log; report that
condition without inventing history or requiring a first commit.

**Conversation context:**
- Scan the current conversation for decisions, failed approaches, and unresolved questions
- Note any user-stated goals that were or were not completed
- Determine session status: `completed` (all goals met), `partial` (some goals met), `blocked` (unable to proceed)

**Facts and evidence:**
- Record observed file/Git state under Verified Facts, with the command or file
  and observation date. Attribute user-reported results rather than claiming
  to have independently verified them.
- Keep decisions and their authority/rationale in Decisions Made. Put proposed
  actions, assumptions, and untested claims in Open Questions or Context, clearly
  labeled. A planned test is not a passing test; a handoff is not authorization.

**Phase output:** Raw state snapshot — file lists, branch, diff stats, conversation notes, status.

**Validation:** All git commands return successfully. If not in a git repo, fall
back to manual file listing via `ls` and note this in the handoff.

### Phase 2: Extract Decisions & Dead Ends

Review conversation for structured insights. For each item, capture the **WHY** —
the next session needs reasoning, not just outcomes.

**Decisions:**
- What was chosen and the rationale behind it
- Format: `**{{decision}}** — because {{rationale}}`
- If rationale or approval is unstated, say so; label any interpretation as an assumption, not an approved decision
- Prioritize decisions that constrain future work (architecture, naming, scope)

**Dead ends:**
- Approaches that were tried and abandoned
- Format: `**Tried:** {{approach}} → **Failed because:** {{reason}}`
- If the session was purely creative/additive, write: "N/A — creation session, no failed approaches"
- Include dead ends from tool errors, not just design choices

**Open questions:**
- Unresolved items surfaced during the session
- Format as checkboxes for the next session to track
- Include questions that were deferred, not just unanswered

**Phase output:** Structured lists of decisions, dead ends, and open questions.

**Validation:** Every decision has a "because" clause. Every dead end has a failure
reason. If either is missing, re-read the conversation context before proceeding.
If still missing after re-read, record it as unknown; ask only if it is needed to choose the next action.

### Phase 3: Compose Next Steps

Define what the next session should do first.

**Rules for Next Step #1 (the actionable gate):**

| Quality | Example | Pass? |
|---------|---------|-------|
| Vague | "Continue working on auth" | No |
| Directional | "Fix the auth tests" | No |
| Actionable | "Run `pytest tests/auth/` to verify JWT refresh works after `token_rotation.py` changes" | Yes |
| Actionable | "Open `src/api/routes.ts:45` and add the missing `validateToken` middleware" | Yes |

**The test:** Could someone start a new session with ONLY Next Step #1 and know
exactly what command to run or file to open? If not, it's not specific enough.

**What makes a step pass:**
- Names a specific **file path**, **command**, or **test**
- Describes the **expected outcome** (not just the action)
- Can be executed without reading other sections of the handoff

Remaining steps (2, 3, ...) can be directional but should still reference
specific files or commands where possible.

**Phase output:** Ordered list of next steps with #1 passing the actionable gate.

**Validation gate:** Re-read Next Step #1. Apply the pass/fail table above. If it
doesn't pass, rewrite it. If you cannot make it specific (e.g., the next step is
genuinely open-ended research), ask the user: *"What should the next session do first?"*

### Phase 4: Render & Save

Fill the template from `assets/templates/handoff-template.md` (relative to this shared skill) with all gathered data.

**Output location decision:**

| Condition | Action |
|-----------|--------|
| Explicit output path supplied | Use that path only, applying the existing-file safeguard below |
| No explicit path and no root `HANDOFF.md` | Write `HANDOFF.md` under `handoff_root` |
| Target already exists | Read it first. Follow already-given update/archive authorization; otherwise ask before replacing it |
| User requests accumulation | Archive to a non-colliding `.handoffs/{{DATE}}.md` path; update the root pointer only if requested |

Preserve unresolved items when updating an existing handoff. Never overwrite an
archive with the same date; choose a distinct filename. Do not seek the same
confirmation again when the user has already authorized the specific update.

**Date handling:** Always use absolute dates (YYYY-MM-DD), never relative ("today",
"yesterday", "this morning").

**Phase output:** Handoff written at the resolved output path.

**Post-render validation checklist:**

- [ ] Observed facts, decisions and untested claims are separated and attributed
- [ ] Output is the requested path; existing handoffs and archives are preserved as agreed
- [ ] All template placeholders (`{{...}}`) are filled or removed
- [ ] No `TODO` / `TBD` markers remain for items that are known
- [ ] Unknown items moved to Open Questions, not left as placeholders
- [ ] Next Step #1 passes the actionable gate (re-check after render)
- [ ] No secrets, tokens, or `.env` values appear anywhere
- [ ] Date is absolute YYYY-MM-DD format

If any check fails, fix and re-render before saving.

**Final report to user:**
```
Handoff written to {{resolved_output_path}}. Next session should start by reading that file.
```

## Failure Mode Handling

| Failure | Recovery |
|---------|----------|
| Not a git repo | Fall back to `ls -la` for file listing; note "no git context" in handoff |
| No changes detected | Write a minimal handoff noting "no code changes — session was research/discussion only" |
| Conversation too short for decisions | Write "No decisions recorded" rather than fabricating |
| Next Step #1 can't be made specific | Ask the user: "What should the next session do first?" |
| Existing target would be overwritten | Read it; honor existing update authorization, otherwise ask or offer a distinct archive |
| Git commands fail (permissions, corrupt repo) | Log the error in Context section; continue with what's available |

## Safety Constraints

- **NEVER** include secrets, tokens, API keys, or `.env` contents in the handoff — because handoffs may be committed to version control or shared
- **NEVER** overwrite an existing handoff or archive without authorization — preserve unresolved items and honor any specific update already requested
- **NEVER** fabricate decisions or dead ends — if the conversation doesn't contain them, say so explicitly rather than inventing plausible-sounding rationale
- **NEVER** use relative dates — because handoffs are read days or weeks later when "today" is meaningless
- **NEVER** include raw diffs or large code blocks — reference file paths and line numbers instead; the reader has the repo

## Dependencies

- `git` (for state gathering; graceful fallback if unavailable)
- No other runtime dependencies

## Reference Files

- [`assets/templates/handoff-template.md`](assets/templates/handoff-template.md) — Skeleton template filled during Phase 4. Contains the validation gate comment inline so every render reminds the author of the quality bar.

## Quick Reference Table

| Task | Command/Method | Notes |
|------|---------------|-------|
| Gather git state | `git -C "$handoff_root" status --short` plus the Phase 1 commands | Include staged and unstaged changes |
| Check for existing handoff | Inspect the resolved output path and any root handoff | Read before an authorized update |
| Validate Next Step #1 | Apply pass/fail table from Phase 3 | Must name file, command, or test |
| Write handoff | Fill template → validate → Write to path | Never skip validation |
| Archive old handoff | Preserve existing content at a distinct `.handoffs/` path under the target root | Only when requested or already authorized |
| Minimal handoff (no changes) | Skip git diff, note "research/discussion only" | Still require Next Step #1 |

For the workflow overview and actionable-step gate, see
[writing-session-handoffs-diagrams.md](writing-session-handoffs-diagrams.md).
