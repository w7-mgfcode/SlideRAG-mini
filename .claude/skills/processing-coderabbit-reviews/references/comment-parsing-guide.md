# Comment Parsing Guide

## Extracting the AI Agent Prompt

CodeRabbit review comments may contain a collapsible section with codegen instructions.

### Format

```html
<details>
<summary>🤖 Prompt for AI Agents</summary>

[Codegen instruction text here — may be multi-line, may contain code blocks]

</details>
```

### Extraction logic

1. Search comment body for `<details>` block containing `🤖 Prompt for AI Agents`
2. Extract content between the closing `</summary>` and `</details>` tags
3. Strip leading/trailing whitespace from extracted content
4. If the block is absent or empty, fall back to the full comment body text

### Regex pattern

```
<details>\s*<summary>🤖 Prompt for AI Agents</summary>\s*([\s\S]*?)\s*</details>
```

Group 1 is the agent prompt. If no match, use the full comment body.

## Comment Metadata

Each CodeRabbit comment contains structured metadata in the first line:

```
_Issue Type_ | _Severity_
```

Extract with: `_([^_]+)_ \| _([^_]+)_`

### Severity mapping

| Raw severity | Level | Priority |
|-------------|-------|----------|
| Critical, High | CRITICAL | Must fix |
| Medium | HIGH | Should fix |
| Minor, Low | MEDIUM | Consider |
| Info, Suggestion | LOW | Optional |
| Security (any level) | CRITICAL | Must fix |

## CodeRabbit Bot Identifiers

Match root comment author against:
- `coderabbitai`
- `coderabbit[bot]`
- `coderabbitai[bot]`

## Disposition Decision Tree

For each comment, determine disposition by checking in order:

```
1. Is the thread already resolved?
   → YES: skip (already resolved)

2. Does any reply from a non-bot user say it's handled?
   → YES: skip (human addressed)

3. Has the code at the comment's line range changed significantly
   since the comment was posted?
   → YES: stale

4. Parse the comment — is the suggestion valid for the current code?
   → NO (code already does what's suggested): stale
   → NO (suggestion is incorrect/inapplicable): not-applied
   → PARTIALLY (part applies, part doesn't): partially-fixed
   → YES: fixed (apply the fix)

5. If uncertain about validity:
   → needs-human
```

## Reply Templates

### Fixed
```
Fixed: [one-line description of change]. Validated with [validation command].
```

### Partially fixed
```
Partially addressed: [what changed]. Remaining: [what wasn't applied and why].
```

### Not applied
```
Not applied: [brief reason — e.g., "suggestion targets code that was already refactored in commit abc123"].
```

### Stale
```
Stale: code at this location has changed since the review. The original concern no longer applies.
```

### Needs human
```
Flagged for human review: [brief reason the automated fix isn't confident enough].
```
