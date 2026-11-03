# Commit Message Format

Every commit in this repository MUST follow this format:

```
type(scope): description (#issue)
```

## Rules

- **type** — one of: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `release`
- **scope** — one of the SlideRAG Mini scope allow-list (below). Comma-pairs are allowed when a change cuts across two scopes (e.g., `api,ui`).
- **description** — lowercase, imperative mood, no trailing period
- **#issue** — a valid GitHub issue number. Every commit MUST reference one.

### Scope allow-list

Maps to the flat module layout in `docs/.prepare/execution-plan.md` § 3. CI changes use `chore(ci)`; `ci` is a scope, not an allowed type.

| Scope     | Use for |
|-----------|---------|
| `api`     | `app/main.py` — routes, startup, `/health`, request handling |
| `ingest`  | `app/ingestion.py` — PPTX validation, SHA-256, slide extraction, chunking, idempotent indexing |
| `rag`     | `app/rag.py` — embeddings, Chroma access, retrieval, LangGraph state and nodes, source validation |
| `config`  | `app/config.py`, `.env.example` — settings and secret loading |
| `ui`      | `app/templates/**`, `app/static/**` — Jinja2 pages and plain CSS |
| `demo`    | `demo/**` — synthetic presentation generator and demo facts |
| `tests`   | `tests/**` — pytest suite and fixtures |
| `docs`    | `docs/**`, root `README.md`, `CHANGELOG.md` |
| `deploy`  | `Dockerfile`, `.dockerignore`, EC2 / EBS setup scripts and notes |
| `ci`      | `.github/workflows/**`, `.pre-commit-config.yaml` |
| `repo`    | Repo-wide hygiene (`.gitignore`, `.claude/`, `.agents/`, `pyproject.toml` tooling-only edits) |
| `release` | Version bumps and tags |

### No AI co-author trailer — ever

Do NOT include any of the following in commit messages — past, present, or future model versions:

- `Co-Authored-By: Claude <noreply@anthropic.com>`
- `Co-Authored-By: Claude <any-version> <noreply@anthropic.com>`
- `Generated with [Claude Code]` lines
- `🤖 Generated with …` lines
- Any other AI-attribution line

The session is already attributed via `git config user.name`. That is the only attribution we keep.

## Examples

Good:
- `feat(ingest): validate pptx zip signature and 10 mb cap (#4)`
- `feat(rag): add insufficient-evidence fallback node (#9)`
- `fix(api): escape document-derived text in answer view (#12)`
- `chore(repo): adapt .claude/ rules to sliderag mini (#1)`
- `docs(demo): list the five demonstration questions (#7)`
- `feat(api,ui): render slide-level source references (#10)`
- `release(repo): cut 0.1.0 (#20)`

Bad:
- `fixed bug` — no type, scope, or issue
- `feat: add new feature` — missing issue reference
- `feat(rag): Refactor graph.` — capitalized + trailing period
- `feat(misc): X (#17)` — `misc` is not in the allow-list
- `feat(forecast): X (#17)` — `forecast` belonged to the previous project's tooling, not this repo

## Scope exception

`docs` and `release` types may omit scope when the change is project-wide (e.g., root README, CHANGELOG bump).

## Before committing

Verify, in this order:
1. Message matches `type(scope): description (#issue)`
2. The issue exists and is open: `gh issue view <N> --json state`
3. The scope matches the primary path being changed
4. The type accurately reflects the change (`feat`=new, `fix`=bug, `chore`=non-functional, `release`=tag-cut)
5. There is NO AI co-author or "Generated with" trailer

If a user-supplied message doesn't match, reformat it. If no issue number is provided, ask — never commit without one.

A `commit-format-check` skill and a `PreToolUse` hook (`.claude/hooks/check-commit-format.sh`) enforce this rule deterministically.
