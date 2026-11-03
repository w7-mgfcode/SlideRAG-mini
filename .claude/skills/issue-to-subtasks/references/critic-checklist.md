# Critic Checklist

Apply this checklist after producing the draft (Step 8 of the pipeline) and BEFORE finalizing the 5 subtasks. The critic role is constructive: it strengthens the work, not dismisses it. Goal is to surface scope creep, weak anchoring, and over-engineering — then revise once.

Run through each section in order. For every item, mark one of:

- ✅ **Pass** — issue is sound on this dimension
- ⚠️ **Soft fail** — note in critic findings; revise if quick fix exists
- ❌ **Hard fail** — must revise before finalizing

If three or more items hit ⚠️ or ❌, revise the draft and re-run the checklist. One revision round only — multi-agent research shows gains saturate fast.

---

## Section 1: Source-of-truth anchoring

- [ ] Every material claim in the brief is traceable to issue body, comment, linked PR, or repo file
- [ ] No claims about decisions that aren't actually decided
- [ ] No invented context (e.g., "the team agreed X" when no comment shows that)
- [ ] When source-of-truth conflicts, both perspectives are surfaced — not silently picked
- [ ] Vendor / external doc references are the ones the issue actually cites, not adjacent ones

## Section 2: Scope discipline

- [ ] Nothing in scope that isn't in the issue or its parent
- [ ] No "while we're at it" expansions
- [ ] If a related issue's work is referenced, it's properly attributed (not folded in)
- [ ] Out-of-scope section is non-empty and specific (vague "out of scope: anything else" fails)
- [ ] MVP is the *smallest* useful slice — not "phase 1 of the grand plan"

## Section 3: Blocker / dependency completeness

- [ ] Every "depends on" mention in body/comments is reflected in dependencies
- [ ] Cross-repo dependencies (if visible from referenced PRs) are flagged
- [ ] CODEOWNERS / approval requirements are noted if visible
- [ ] Missing decisions are called out as blockers, not assumed away
- [ ] If a parent epic is open and unscoped, that's a blocker — say so

## Section 4: Subtask quality (apply to each of the 5)

For every subtask:

- [ ] **Title** is imperative and specific (not "investigate X" unless investigation IS the deliverable)
- [ ] **Scope** is bullets and would fit on one screen
- [ ] **Out of scope** is non-empty
- [ ] **Acceptance criteria** is *testable* — someone could write a check for it
- [ ] **Dependencies** are explicit subtask IDs or external work, not "after stuff is ready"
- [ ] **Why it matters now** ties back to source-of-truth in one line
- [ ] An implementer could pick this up without re-reading the parent issue

## Section 5: Sequencing and shape

- [ ] If subtasks have ordering dependencies, the order matches the rerank table
- [ ] Parallel-safe subtasks are flagged as such (so multiple people can pick up work)
- [ ] No subtask is a hidden epic (>3 days of work for one person)
- [ ] No subtask is trivial filler (<1 hour) just to hit the count of 5
- [ ] If 5 subtasks doesn't fit the issue, that's stated honestly — don't pad

## Section 6: Risk and ownership

- [ ] Each subtask's risk is specific (not "could fail")
- [ ] Rollback / revert path is implied or stated for risky subtasks
- [ ] Ownership ambiguity is flagged (no assignee, multiple plausible owners, etc.)
- [ ] Milestone-critical work is labeled as such — not buried

## Section 7: Anti-over-engineering

- [ ] No multi-week roadmap when the issue is one bug
- [ ] No new abstractions unless the issue itself argues for one
- [ ] No "let's first refactor" preludes that don't shorten the actual work
- [ ] No subtasks that exist only to validate the agent did its homework

## Section 8: Honesty about uncertainty

- [ ] Anything labeled `[ASSUMPTION]` would be obvious to the reader
- [ ] Where source-of-truth is missing, it's stated — not papered over with confidence
- [ ] Recommendations carry their evidence strength (see scoring rubric)
- [ ] If the issue can't be properly scoped from current context, that's said plainly with a list of unanswered questions

---

## Critic findings format

After running the checklist, summarize findings in the output package's "Critic findings" section as bulletpoints in this shape:

```
- [Section 2] ⚠️ Subtask 3 expands scope beyond the issue — refactor of module X isn't requested
- [Section 4] ❌ Subtask 1 acceptance criterion is "looks correct" — not testable
- [Section 7] ⚠️ Two-week sequencing for what reads like a 2-day fix
```

If everything passes, say so explicitly:

```
- All checks passed. No revisions applied.
```

---

## Notes on the multi-agent critique principle

This checklist embodies the "single critic, structured pass" pattern from multi-agent critique research. Findings:

- **One revision round is enough.** Empirical studies show critique-revision gains saturate at 1–2 cycles; further rounds introduce echo-chamber dynamics.
- **Specialized critic role works better than self-critique.** Hence this checklist is applied as a distinct pass after drafting, not interleaved during.
- **Constructive framing.** Identify both the issue and the fix; don't just flag.
- **Bound the scope of the critic.** Eight sections, capped. Don't let the critic invent new dimensions on the fly.
