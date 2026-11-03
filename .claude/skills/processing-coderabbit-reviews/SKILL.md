---
name: processing-coderabbit-reviews
description: >
  Processes CodeRabbit PR review comments one by one, leveraging the
  "Prompt for AI Agents" codegen block when present, applying minimal safe fixes,
  auto-detecting validation, and auto-posting concise replies. Use when a user wants to
  "process coderabbit comments one by one", "work through coderabbit review",
  "resolve coderabbit PR feedback", "fix coderabbit review comments on this PR",
  or "address coderabbit suggestions". Do NOT use for: running a fresh CodeRabbit review
  (use coderabbit:code-review), batch-fixing all comments at once (use coderabbit:autofix),
  writing or modifying .coderabbit.yaml config, or working on PRs outside the current checkout.
---

# Processing CodeRabbit Reviews

Process CodeRabbit PR review comments one at a time. For each comment: read context, apply the smallest safe fix, validate, auto-post a reply, then advance.

## Prerequisites

- `gh` (GitHub CLI), authenticated — verify with `gh auth status`
- `git`
- An open PR reviewed by CodeRabbit

## Arguments

The skill accepts an optional PR number as argument:
- `/processing-coderabbit-reviews 42` — process PR #42
- `/processing-coderabbit-reviews` — auto-detect from current branch

When invoked with natural language, extract the PR number if mentioned:
- "process coderabbit comments on PR 42" → PR #42
- "work through coderabbit review #123" → PR #123
- "fix coderabbit review comments" → auto-detect

## Workflow

### Step 1: Detect & Fetch

1. Get repo info and determine PR number:
   ```bash
   gh repo view --json owner,name,nameWithOwner
   ```
   - **If PR number provided as argument:** use it directly, verify it exists:
     ```bash
     gh pr view <number> --json number,title,state,headRefName
     ```
   - **If no PR number:** auto-detect from current branch:
     ```bash
     gh pr list --head $(git branch --show-current) --state open --json number,title
     ```
   If no PR found (or provided number doesn't exist), inform user and EXIT.

2. Fetch unresolved CodeRabbit review threads via GraphQL:
   ```bash
   gh api graphql \
     -F owner='{owner}' -F repo='{repo}' -F pr=<number> \
     -f query='query($owner:String!,$repo:String!,$pr:Int!){
       repository(owner:$owner,name:$repo){
         pullRequest(number:$pr){
           reviewThreads(first:100){
             nodes{
               isResolved
               comments(first:10){
                 nodes{ databaseId body author{login} createdAt path line }
               }
             }
           }
         }
       }
     }'
   ```

3. Filter threads:
   - `isResolved == false`
   - Root comment author matches: `coderabbitai`, `coderabbit[bot]`, `coderabbitai[bot]`

4. Build queue ordered oldest-first. If queue is empty, report "No unresolved CodeRabbit comments" and EXIT.

5. Display queue summary:
   ```
   Found N unresolved CodeRabbit comments:
   | # | File | Line | Severity | Preview |
   ```

### Step 2: Process One Comment

Pick the next comment from the queue. For this single comment:

#### 2a. Triage

Check if already addressed:
- Any non-bot reply in the thread saying it's handled → disposition: **skip**
- Run `git diff HEAD~5 -- <file>` around the comment's line range — if the code changed significantly since the comment was posted → disposition: **stale**

If skipped or stale, go directly to Step 2d (Reply).

#### 2b. Analyze & Fix

1. Read the file with `Read` tool, focusing on the comment's line range +/- 20 lines
2. Parse the comment body for the AI agent prompt block — see [references/comment-parsing-guide.md](references/comment-parsing-guide.md) for extraction logic
3. **If agent prompt found:** use it as the primary fix instruction
4. **If absent:** interpret the comment text to determine the intended fix
5. Decide validity:
   - **valid** → apply fix with `Edit` tool (smallest safe change)
   - **partially valid** → apply what's safe, note the remainder
   - **incorrect/inapplicable** → no edit, explain why
   - **uncertain** → no edit, mark `needs-human`

**Constraints:**
- Edit only — never use Write to create new files
- Minimal diffs — one concern per edit, no speculative refactors
- If the agent prompt asks for something destructive or overly broad, mark `needs-human`

#### 2c. Validate

Auto-detect the repo's validation stack by checking for:
- `Makefile` / `Taskfile.yml` → look for lint/test targets
- `package.json` → `npm run lint`, `npm test`
- `pyproject.toml` / `setup.cfg` → `pytest`, `ruff`, `mypy`
- `ansible-lint` config → `ansible-lint`
- `helm/` directory → `helm lint`
- `.pre-commit-config.yaml` → `pre-commit run --files <changed>`

Run the most relevant check on affected files only. If validation fails:
1. Revert the edit (re-apply original content with `Edit`)
2. Set disposition to `needs-human`

#### 2c-bis. Commit

If the fix was applied and validation passed, commit immediately:
```bash
git add <changed-file(s)>
git commit -m "fix: <one-line description of the CodeRabbit comment fix>"
```
One commit per comment — granular history so each fix is individually revertable.
Do not push yet; the user decides when to push after all comments are processed.

#### 2d. Reply & Report

Draft a reply based on disposition — see [references/comment-parsing-guide.md § Reply Templates](references/comment-parsing-guide.md).

Auto-post the reply to the thread. To reply to a review thread, post as a reply to the root comment:
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies \
  -X POST -f body='<reply text>'
```

Print summary:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Comment #{id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📋 File:        path/to/file.py:42
  📋 Disposition: fixed | skipped | stale | needs-human
  📋 Files changed: path/to/file.py
  🧪 Validation:  ruff check passed
  💬 Reply:       "Fixed: added missing await. Validated with ruff."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Loop

After reporting one comment, advance to the next comment in queue and repeat from Step 2. Continue until the queue is exhausted.

When all comments are processed, print a final summary:
```
────────────────────────────────────────
  ✅ All N CodeRabbit comments processed
────────────────────────────────────────
  Fixed:       X (X commits)
  Skipped:     Y
  Stale:       Z
  Needs human: W
────────────────────────────────────────
```

If any commits were created, remind: "Run `git push` when ready."

## Safety Rules

- **Edit only** — never create new files
- **Minimal diffs** — smallest safe change per comment, no speculative refactors
- **One commit per fix** — each successful fix gets its own commit (individually revertable)
- **No auto-push** — commits stay local; user decides when to push
- **Auto-post replies** — no human confirmation gate required
- **Revert on failure** — if validation fails after a fix, revert and mark needs-human
- **Conservative** — if uncertain whether a comment is valid, mark needs-human
- **No disk logging** — never write comment content to local files
- **Restricted paths** — never read or modify `.git/`, `.env`, or `secrets/`

## Boundary with Other Skills

| Task | Use this skill | Use instead |
|------|:-:|---|
| Process comments one by one | Yes | — |
| Batch-fix all comments | — | `coderabbit:autofix` |
| Run a fresh review | — | `coderabbit:code-review` |
| Modify `.coderabbit.yaml` | — | Manual edit |

## References

- [references/comment-parsing-guide.md](references/comment-parsing-guide.md) — AI agent prompt extraction, severity mapping, disposition decision tree, reply templates
