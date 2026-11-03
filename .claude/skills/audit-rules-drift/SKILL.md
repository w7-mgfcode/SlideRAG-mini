---
name: audit-rules-drift
description: Detects drift between SlideRAG Mini policy artifacts and the codebase. Compares .claude/rules/*.md and .claude/hooks/*.sh against root README.md, CLAUDE.md, AGENTS.md, and pyproject.toml when present, and against the governing docs/.prepare/execution-plan.md otherwise. Surfaces orphan rules, dangling references, unused/undeclared scopes, hook-vs-rule mismatch, and stale paths. Read-only; triggers on "audit rules", "find rule drift", "are the rules current", "/audit-rules-drift", or before a docs-refresh PR. Do NOT use for code review, security audits, or rewriting rules.
---

# audit-rules-drift

Detect drift between `.claude/rules/`, root markdown anchors, and the repo state they describe. Read-only.

## Scope

- `.claude/rules/*.md`
- `.claude/hooks/*.sh`
- Root `README.md`, `CLAUDE.md`, `AGENTS.md` — each only if present
- `pyproject.toml` — only if present (ruff/pytest config blocks the rules cite)
- `docs/.prepare/execution-plan.md` §§ 2–3, 7–9 — governing scope, module/data paths, test layout, and workflow while code does not exist yet

## Procedure

1. **List rule files**: `find .claude/rules -name '*.md'`.
2. **List hooks**: `ls .claude/hooks/*.sh`.
3. **Build the path authority**: union of existing files and the approved execution plan's module/test/configuration/deployment paths, including normal scaffolding (`app/`, `demo/`, `tests/`, `docs/`, `Dockerfile`, `.dockerignore`, `.gitignore`, `.env.example`, `.python-version`, `pyproject.toml`, `uv.lock`, `README.md`, `CLAUDE.md`, `CHANGELOG.md`, minimal `.github/`). Runtime children are uploads/chroma/manifest under DATA_DIR (`/data` in the container; temporary roots in tests). Planned files need not already exist.
4. For each rule file, extract:
   - Every concrete file path it mentions (`app/...`, `demo/...`, `tests/...`, `docs/...`, `.github/...`)
   - Every shell command it cites (`uv run pytest`, `uv run ruff check .`, `docker build`, `git tag`)
   - Every scope/type/keyword it constrains (scope allow-list in `commit-format.md`, branch prefixes in `branch-naming.md`)
5. For root `README.md` / `CLAUDE.md` / `AGENTS.md` (when present), extract every rule path it references. When none of the three exists yet, report the orphan check as `⏭️ SKIP (no anchor docs yet)` instead of flagging every rule.
6. Run the checks below.

## Checks

1. **Orphan rules** — a `.claude/rules/<name>.md` that is referenced from NEITHER `README.md` NOR `CLAUDE.md` NOR `AGENTS.md`. Flag `⚠️ ORPHAN`. Skipped while none of the anchor docs exists.
2. **Dangling references** — `README.md` / `CLAUDE.md` / `AGENTS.md` cites a rule file (or section heading) that does not exist. Flag `❌ DANGLING`.
3. **Path / command drift** — a rule cites a concrete path that is neither on disk nor in the path authority from step 3. Flag `❌ PATH-DRIFT`. The most likely drift in this repo is a leftover from the previous project's tooling: `frontend/`, `alembic/`, `app/features/`, `app/core/`, `docs/PHASE/`, `docs/ADR/`, `PRPs/`, `docker-compose`, `pnpm`, `mypy --strict`, `pyright`.
4. **Empirical-vs-declared scope drift** (commit-format.md only; skipped when the repo has no git history) —
   - Run: `git log --pretty=%s -200 main | grep -oE '^[a-z]+\(([a-z,]+)\)' | sed 's/.*(\([a-z,]\+\))/\1/' | tr ',' '\n' | sort -u`
   - Diff vs. the scope allow-list in `commit-format.md` (and the `SCOPE_ALLOW` regex in `.claude/hooks/check-commit-format.sh`).
   - Scopes used but not declared → ❌ `UNDECLARED`.
   - Scopes declared but never used → ⚠️ `UNUSED` (low-value to fix; report only).
5. **Hook ↔ rule consistency** — the `SCOPE_ALLOW` regex in `check-commit-format.sh` MUST exactly mirror the scope allow-list table in `commit-format.md`, and the same set MUST appear in `.claude/skills/commit-format-check/SKILL.md`. Flag `❌ HOOK-DRIFT` on divergence.
6. **Plan ↔ rule consistency** — `product-vision.md` scope lock must agree with execution-plan.md § 2; `test-requirements.md` must preserve QG-01…QG-09 and the consistency/recovery contracts in § 7. Flag missing/weakened gates or conflicting current policies. Historical proposal bodies are not competing instructions when explicitly marked superseded.

## Report format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧭 Rules Drift Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Rules inventory
  ✅ 7 rule files discovered

📋 Orphan rules
  ⏭️ SKIP — no README.md / CLAUDE.md / AGENTS.md yet

📋 Dangling references
  ✅ none

📋 Path / command drift
  ❌ .claude/rules/security-patterns.md:9 — cites `alembic/` (not in repo or plan — previous-project leftover)

📋 Commit-format scope drift
  ⏭️ SKIP — no git history yet

📋 Hook ↔ rule consistency
  ✅ SCOPE_ALLOW matches commit-format.md allow-list and commit-format-check skill

📋 Plan ↔ rule consistency
  ✅ scope-lock table and QG table match the plan

────────────────────────────────────────────
  ❌ Result: 1 error, 0 warnings
────────────────────────────────────────────

👉 Next steps:
  1. Remove the `alembic/` reference from security-patterns.md:9
```

## Constraints

- **Read-only.**
- Cap report at 80 lines.
- Do NOT propose textual rewrites — list findings, the main session decides.
- The 200-commit window for empirical scope analysis is a deliberate limit: longer windows are noisy. Adjust if the user explicitly asks.
- If a `.claude/rules/` file is generic (e.g., `output-formatting.md`), it may legitimately reference no repo-specific path — don't flag it as PATH-DRIFT for that reason alone.
