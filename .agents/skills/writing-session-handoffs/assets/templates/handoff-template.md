# Session Handoff

> **Date:** {{DATE}}
> **Session focus:** {{ONE_SENTENCE_FOCUS}}
> **Status:** {{completed | partial | blocked}}

## What Was Done

<!-- List every concrete change. Be specific: file paths, function names, config values.
     If no code changes were made, describe what was discussed or researched. -->

- {{CHANGE}}

## Verified Facts

<!-- List only observations backed by a command/file and date. Attribute reported
     results. Keep decisions below and label assumptions or untested claims in
     Context/Open Questions. A planned check is not a passing check. -->

- **Observed:** {{FACT}} — **Evidence:** {{COMMAND_OR_FILE_AND_DATE}}

### Files Changed

```
{{FILE_LIST}}
```

## Decisions Made

<!-- Each decision + WHY. The next session needs the reasoning, not just the outcome.
     If no decisions were made, write: "No decisions recorded — session was exploratory." -->

- **{{DECISION}}** — because {{RATIONALE}}. **Authority:** {{USER_OR_SOURCE_OR_UNCONFIRMED}}

## Dead Ends

<!-- What was tried and failed. Prevents next session from repeating mistakes.
     If nothing failed, write: "N/A — creation session, no failed approaches." -->

- **Tried:** {{APPROACH}} → **Failed because:** {{REASON}}

## Open Questions

<!-- Unresolved items that need answers before continuing. Use checkboxes. -->

- [ ] {{QUESTION}}

## Next Steps

<!-- VALIDATION GATE — Step #1 must pass this test:
     "Could someone start a new session with ONLY this step and know exactly
      what command to run or file to open?"

     FAIL: "Continue working on auth"
     FAIL: "Fix the auth tests"
     PASS: "Run `pytest tests/auth/` to verify JWT refresh after token_rotation.py changes"
     PASS: "Open `src/api/routes.ts:45` and add the missing validateToken middleware" -->

1. **Immediate:** {{EXACT_FIRST_ACTION}}
2. {{NEXT}}
3. {{NEXT}}

## Context for Next Session

<!-- Anything not captured above: branch state, remote status, blocking dependencies,
     related PRs, environment setup needed. -->

{{ADDITIONAL_CONTEXT}}
