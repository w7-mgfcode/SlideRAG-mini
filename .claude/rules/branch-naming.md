# Branch Naming

Branch names mirror the `type` field of `commit-format.md`. This rule applies to every `git checkout -b` / `git switch -c` Claude runs.

## Format

```
<type>/<scope-slug>
```

- **type** — one of: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `release`
- **scope-slug** — kebab-case, ≤ 50 chars, no issue number (the issue lives in commit + PR)
- The slug should hint at the scope from `commit-format.md` so a glance reveals intent (`feat/ingest-...`, `fix/rag-...`).

## Examples

Good:
- `feat/ingest-pptx-validation`
- `feat/rag-evidence-fallback`
- `fix/api-escape-answer-html`
- `chore/repo-claude-rules-adapt`
- `docs/architecture-persistence-notes`
- `release/v0-1-0`

Bad:
- `add-feature` — no type prefix
- `feat/issue-42` — embeds the issue number
- `feat/My_Feature_Branch` — not kebab-case, capitalized
- `feature/foo` — wrong type prefix (use `feat/`)
- `feat/` — empty slug

## Rules

- Branch model is `main` plus short-lived branches. Every branch is cut from an up-to-date `main` and merged back to `main` by PR. There is no `dev` branch and no separate hotfix flow; a fix is a `fix/...` branch like any other.
- One branch per issue. If a single issue grows beyond one branch, split the issue.
- `release/*` branches are ephemeral — delete after the tag is pushed.
- Don't reuse a branch name after it's been merged and deleted.

## Before creating a branch

1. There is an issue (`gh issue list --search "<topic>"`) — if not, open one first.
2. Pick the right `type` for the work.
3. Pick a kebab-case slug ≤ 50 chars.
4. `git switch -c <type>/<slug>` from an up-to-date `main`.

If the user asks for a branch that doesn't fit this format, propose a corrected name and explain why.
