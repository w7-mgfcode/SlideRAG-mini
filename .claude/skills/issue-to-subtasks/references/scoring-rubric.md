# Scoring Rubric

This rubric defines the 7 dimensions used in Step 7 (Research → Recommend → Rerank). Each dimension is scored on a 1–5 integer scale. The `score_directions.py` script consumes scores in this format and produces a weighted ranking.

## How to use it

For every candidate direction (or candidate subtask ordering):

1. Score each of the 7 dimensions, 1–5
2. For `risk` and `dependency_load`, the input represents the AMOUNT (so 5 = lots of risk, 1 = very safe). The script inverts these automatically when computing the weighted score.
3. Optionally adjust weights — defaults are 1.0 for all. Common reweights: bump `value` and `evidence_strength` to 1.5 for high-stakes work.

## The 7 dimensions

### 1. Value (1–5)

How much outcome impact does this direction produce for the user / stakeholder?

| Score | Meaning |
|---|---|
| 1 | Marginal — nice-to-have, no clear stakeholder impact |
| 2 | Limited — helps a small group, low traffic |
| 3 | Moderate — visible improvement on the relevant surface |
| 4 | High — addresses a stated need or unblocks meaningful work |
| 5 | Critical — directly closes the issue's stated outcome |

### 2. Risk (1–5, INVERTED)

Probability of failure or significant rework. Higher input = MORE risk.

| Score | Meaning |
|---|---|
| 1 | Trivial — well-trodden path, low chance of surprise |
| 2 | Low — minor uncertainty, recovery is cheap |
| 3 | Moderate — some unknowns, recovery requires effort |
| 4 | High — material chance of needing a redo |
| 5 | Severe — likely to fail or require redesign |

### 3. Readiness (1–5)

Are upstreams done? Are decisions made? Are owners present?

| Score | Meaning |
|---|---|
| 1 | Not ready — multiple critical decisions / upstreams missing |
| 2 | Partially ready — some unknowns block start |
| 3 | Ready with caveats — can begin, expect mid-flight clarification |
| 4 | Mostly ready — minor open items, won't block start |
| 5 | Fully ready — every input is in place, can start today |

### 4. Dependency load (1–5, INVERTED)

How many other things must move first? Higher input = MORE deps.

| Score | Meaning |
|---|---|
| 1 | Self-contained — no upstream work required |
| 2 | One small dep — quick to resolve |
| 3 | A few deps — manageable but real |
| 4 | Many deps or one large one — meaningful sequencing |
| 5 | Heavy chain — multiple cross-team / cross-repo dependencies |

### 5. Validation ease (1–5)

Can this be verified cleanly?

| Score | Meaning |
|---|---|
| 1 | Hard — outcomes are subjective or distributed across many surfaces |
| 2 | Slow — requires manual / staged validation |
| 3 | Mixed — some auto-checks, some manual |
| 4 | Mostly automatable — tests / metrics cover the bulk |
| 5 | Trivial — single test / single metric / single review confirms it |

### 6. Rollback safety (1–5)

If the work is wrong or causes a regression, how cheap is undoing it?

| Score | Meaning |
|---|---|
| 1 | Effectively unrollable — schema migration without down path, etc. |
| 2 | Costly to roll back — requires coordination |
| 3 | Possible but slow — feature flag flip plus cleanup |
| 4 | Easy — single revert, low blast radius |
| 5 | Trivial — toggle off, no state to clean up |

### 7. Evidence strength (1–5)

How well-grounded is this direction in source-of-truth (issue body, comments, linked PRs, repo files, official docs)?

| Score | Meaning |
|---|---|
| 1 | Speculative — based on guesses or analogies |
| 2 | Weak — one tangential reference |
| 3 | Decent — issue mentions it but not in detail |
| 4 | Strong — issue + linked PR / comment / doc back it up |
| 5 | Authoritative — explicitly stated in the issue or its source-of-truth |

---

## Weighted score formula

For each candidate:

```
effective_score(d) = (6 - score(d))   if d in {risk, dependency_load}
                     score(d)          otherwise

weighted_score = Σ (effective_score(d) × weight(d))  /  Σ weight(d)
```

Result is in [1, 5]. Higher = better candidate.

## Reading the table

The output table from `score_directions.py` shows raw input scores (NOT inverted), so a `risk = 4` cell still reads as "this is risky" even though it lowers the weighted score. This makes the table easier to scan when explaining the ranking to humans.

## When NOT to use the rubric

If the issue is genuinely a single one-action fix ("rotate API key", "bump dependency from 1.2.3 to 1.2.4"), there's no meaningful rerank — there's one direction. Skip this step, say so in the output, and produce a single-task plan with a note that the standard 5-subtask shape doesn't fit.
