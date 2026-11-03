---
name: repo-visibility-audit
description: Audits the SlideRAG Mini public-facing surface — README.md, CHANGELOG.md, docs/architecture.md, demo/README.md, .env.example. Detects broken internal links, dead anchors, CHANGELOG↔pyproject↔tag version drift, .env.example↔app/config.py drift, stale docs (>90d unchanged), orphan docs, badge failures (HTTP probe), and outdated screenshots. Read-only — produces a scannable report. Triggers on "audit the README", "check the docs", "find stale docs", "find orphan docs", "/repo-visibility-audit". Do NOT use for code review, dependency audits, security scanning, or rewriting docs.
---

# repo-visibility-audit

Read-only audit of the SlideRAG Mini public-facing surface. **You print a scannable report. You NEVER edit files.**

## Scope

Audit ONLY these paths:

- Root: `README.md`, `CHANGELOG.md`
- `docs/architecture.md`
- `demo/README.md`
- `.env.example`
- Cross-checked against (read-only, not audited themselves): `pyproject.toml`, `app/config.py`, `tests/test_rag.py`

Anything else: skip. `docs/.prepare/` is a planning area and is never in scope. A scope file that does not exist yet is reported as `⏭️ SKIP (not created yet)`.

## Procedure

1. Build the scope list:
   ```bash
   for f in README.md CHANGELOG.md docs/architecture.md demo/README.md .env.example; do
     [ -f "$f" ] && echo "$f"
   done
   ```
2. For each file, extract:
   - Markdown links: `grep -nE '\]\([^)]+\)' "$f"`
   - Headings: `grep -nE '^#+ ' "$f"`
   - Image refs: `grep -nE '!\[[^]]*\]\(([^)]+)\)' "$f"`
   - Badge URLs (README only): first 30 lines
3. Run checks 1–8 below.
4. Cap HTTP probes at 5s timeout. Use `xargs -P 8` for parallelism.
5. Use `git log -1 --format=%cs -- <file>` per scope file for freshness.

## Checks

1. **Broken internal links / anchors** — resolve every `](path)` and `](#anchor)` relative to the source file. Miss = ❌.
2. **Badge sanity** — README badges (if any): probe via `curl -sI -o /dev/null -w "%{http_code}" --max-time 5 <url>`. 2xx/3xx = ✅, 4xx/5xx = ❌, transient 5xx may be ⚠️.
3. **Stale anchor list** — every `## Heading` produces a slug (lowercased, spaces→`-`, punctuation stripped). Cross-check incoming `#anchor` links against the slug list.
4. **Version drift** — the top `CHANGELOG.md` section, `version` in `pyproject.toml`, and `git describe --tags --abbrev=0` (if any tag exists) must agree. Mismatch = ❌.
5. **Env drift** — keys read in `app/config.py` (`grep -oE '"[A-Z_]+"' app/config.py`) vs keys in `.env.example`. Missing in either direction = ❌.
6. **Quick-start drift** — every repo path or script the README quick start names must exist on disk; every route it names (`/health`, upload, ask) must appear in `app/main.py`. Miss = ❌.
7. **Demo-question drift** — the five questions in `demo/README.md` must match the parametrized set in `tests/test_rag.py`. Mismatch = ⚠️.
8. **Stale docs** — `now - git-mtime > 90 days` → ⚠️ STALE (warning only; not a failure).

## Report format

Use `.claude/rules/output-formatting.md` exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔍 Repo-Visibility Audit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Internal links & anchors
  ✅ README.md — 12/12 links resolve
  ❌ docs/architecture.md:40 — link to ../missing/foo.md not found

📋 Badges (README)
  ✅ 2/2 badges return 2xx

📋 Version drift
  ❌ CHANGELOG.md says 0.1.0 but pyproject.toml says 0.0.1

📋 Env drift
  ⚠️ LLM_BASE_URL read in app/config.py but missing from .env.example

📋 Quick-start drift
  ✅ all 5 referenced paths and routes exist

📋 Demo-question drift
  ✅ 5/5 questions match tests/test_rag.py

📋 Stale docs (>90 days, unchanged)
  ⚠️ demo/README.md — last touched 142 days ago

────────────────────────────────────────────
  ❌ Result: NOT CLEAN — 2 errors, 2 warnings
────────────────────────────────────────────

👉 Next steps:
  1. Fix broken link at `docs/architecture.md:40`
  2. Bump `version` in `pyproject.toml` to match CHANGELOG.md
  3. Add `LLM_BASE_URL` to `.env.example`
```

## Constraints

- **Read-only.** If a check needs to write, ABORT with `❌ Tool restriction violated`.
- Cap output at 80 lines. If more findings, append `(+N more)` footer.
- Do NOT call the network for anything beyond the README badge probe list.
- Do NOT analyze code files beyond the three cross-check reads named in Scope — markdown only.
- Do NOT propose textual rewrites — that's the operator's call.
