---
name: managing-agent-memory
description: Generates and updates the AI-agent memory-file layer for a repository — the universal AGENTS.md, the Claude-specific CLAUDE.md, and the docs/_base/ reference-doc suite. Enforces the split model (shared content lives once in AGENTS.md; CLAUDE.md @imports it; no duplication). Supersedes the w7_generating-claudemd skill — it absorbs that skill's docs/_base/ suite generation, KB-vs-heuristic mode, the 150-line CLAUDE.md budget, the residual-question phase, and the quality gate. Use when a user asks to "create AGENTS.md", "generate CLAUDE.md", "set up agent memory files", "update AGENTS.md / CLAUDE.md", "refresh repo agent docs", "/managing-agent-memory", or after a structural change makes the agent docs stale. Do NOT use for llms.txt (use managing-llms-txt), for editing .claude/rules/, or for human-maintained docs like DEV_GUIDE.md.
---

# managing-agent-memory

Generate and maintain a repository's **AI-agent memory layer**:

| File | Role | Audience |
|------|------|----------|
| `AGENTS.md` | Universal cross-tool brief — stack, commands, conventions, safety, git flow | Any agent (Claude, Cursor, Copilot, Gemini CLI, Aider, …) |
| `CLAUDE.md` | Claude-specific operating index — `@import`s AGENTS.md + `docs/_base/` deep dives | Claude Code only |
| `docs/_base/*.md` | Deep-dive reference suite — architecture, API, runbooks, security, rules, domain model | Loaded on demand |

This skill **creates** these files when absent and **updates** them when present. It supersedes
`w7_generating-claudemd` and carries forward every capability of that skill.

## The Split Model — non-negotiable

- **AGENTS.md holds all shared content.** Plain Markdown, no YAML frontmatter, any headings.
  Recommended sections: Project Overview, Tech Stack, Setup, Build & Test Commands, Validation
  Gates, Architecture & Conventions, Testing Requirements, Safety, Git & PR Conventions,
  Deep-Dive Docs. Keep it focused — every token loads on every request.
- **CLAUDE.md is the thin Claude layer.** It opens with `@AGENTS.md`, then adds only
  Claude-specific material: the `@docs/_base/*.md` import list, the operating-index framing,
  a Safety pointer (not a copy), Verification, Workflow, Learnings.
- **Never duplicate.** If content belongs to both, it lives in AGENTS.md and CLAUDE.md
  references it. A line that appears verbatim in both files is a bug.
- **CLAUDE.md hard limit: 150 lines.** With AGENTS.md carrying the shared load, CLAUDE.md
  should land well under that (≈ 40–70 lines).

## Phase 1 — KB Read

Check for the structured KB before anything else:

```bash
ls docs/_kB/repo-map/00_README.md 2>/dev/null && echo KB_PRESENT || echo HEURISTIC_MODE
```

**KB Mode** — read in order, stop if a file is missing: `00_README.md`,
`03_COMPONENT_INVENTORY.md` (extract stack; set `K8S_REPO` / `CICD_REPO` flags),
`06_RUNTIME_ARCHITECTURE.md`, `08_DEPENDENCIES_AND_BLAST_RADIUS.md`,
`11_GLOSSARY_OPEN_QUESTIONS.md`, `interfaces/`, `knowledge-graph.yaml`, flat ADRs/RFCs.

**Heuristic Mode** — KB absent. Run minimal discovery (`find` for IaC/Docker, read
`package.json` / `pyproject.toml` / `Makefile`, scan `.github/workflows/`). Mark generated
content `[UNVERIFIED]` and tell the user to run `mapping-repo-context` for full fidelity.

## Phase 2 — Residual Questions

Auto-answered from KB when present. Always ask these (decisions, not facts; cap 8 total):

1. Primary audience? (platform team / app teams / external contributors)
2. Compliance frameworks in scope? (PCI-DSS / SOC2 / ISO27001 / HIPAA / none)
3. What does the repo OWN vs. CONSUME? (system boundary)
4. Change-management process? (Atlantis / manual / GitHub Environments)
5. [K8s only] Are SLO targets agreed with stakeholders?

Surface up to 3 UNKNOWNs from `11_GLOSSARY_OPEN_QUESTIONS.md` first. Skipped → `[ASSUMPTION]`.

## Phase 3 — Plan Output

Confirm the doc set with the user before generating:

```
Will generate / update:
  AGENTS.md                    (always)
  CLAUDE.md                    (always; ≤150 lines, @imports AGENTS.md)
  docs/_base/ARCHITECTURE.md   (always)
  docs/_base/API_CONTRACTS.md  (always)
  docs/_base/RUNBOOKS.md       (always)
  docs/_base/SECURITY.md       (always)
  docs/_base/RULES.md          (always)
  docs/_base/DOMAIN_MODEL.md   (always)
  docs/_base/REPO_MAP_INDEX.md (always; from gen_repo_map_index.py)
  docs/_base/DEV_GUIDE.md      (stub only if missing — NEVER overwrite human content)
  docs/_base/WORKLOAD_POLICY.md    [K8S_REPO=true]
  docs/_base/PLATFORM_SLO.md       [K8S_REPO=true]
  docs/_base/PIPELINE_CONTRACT.md  [CICD_REPO=true]
```

## Phase 4 — Generate

Use `templates/AGENTS.md` and `templates/skeleton.md` (CLAUDE.md); section specs for the
`docs/_base/` suite are in `references/doc-specs.md`; `references/question-pool.md` has the
question logic. Generate `REPO_MAP_INDEX.md` with `scripts/gen_repo_map_index.py`.

1. **AGENTS.md** — fill the template from KB/heuristic context. Verify every command against
   `Makefile` / `pyproject.toml` / `package.json` before writing it. Document capabilities,
   not brittle file paths.
2. **CLAUDE.md** — `@AGENTS.md` + the `@docs/_base/*.md` list + Safety pointer + Verification
   + Workflow + Learnings. Strip anything already in AGENTS.md.
3. **docs/_base/ suite** — per `references/doc-specs.md`.

### Update mode (files already exist)

- Refresh stale facts; do not clobber curated prose. Re-run `gen_repo_map_index.py`.
- If CLAUDE.md still carries content now owned by AGENTS.md, move it and leave a reference.
- If AGENTS.md and CLAUDE.md have drifted into duplication, de-duplicate toward AGENTS.md.
- Never overwrite `docs/_base/DEV_GUIDE.md` if it has content beyond the stub.

## Phase 5 — Quality Gate

```bash
wc -l CLAUDE.md                       # ≤ 150
grep -Fxf <(sed -n '/^./p' AGENTS.md) CLAUDE.md   # duplicated lines → empty
head -3 AGENTS.md && head -3 CLAUDE.md            # AGENTS.md has no frontmatter; CLAUDE.md @imports it
ls docs/_base/                        # all expected docs present
grep -rn "\[UNVERIFIED\]" AGENTS.md CLAUDE.md docs/_base/
```

Checklist: Phase 1 KB read (or heuristic declared) · Phase 2 questions asked · Phase 3 doc set
confirmed · Phase 4 generated · Phase 5 gate passed · summary delivered.

## Anti-Patterns — never do these

1. Duplicating shared content between AGENTS.md and CLAUDE.md.
2. Adding YAML frontmatter to AGENTS.md — it is plain Markdown.
3. Overwriting `docs/_base/DEV_GUIDE.md` human content.
4. Writing to `docs/_kB/` — it is a read-only input.
5. Letting CLAUDE.md exceed 150 lines / 1800 words.
6. Skipping Phase 3 plan confirmation.
7. Generic filler ("this is a Python project") — only what an agent would get wrong without it.
8. Documenting brittle file paths instead of capabilities.

## Reference Files

- `templates/AGENTS.md` — AGENTS.md template
- `templates/skeleton.md` — CLAUDE.md template
- `templates/{RULES,DOMAIN_MODEL,REPO_MAP_INDEX,WORKLOAD_POLICY,PLATFORM_SLO,PIPELINE_CONTRACT}.md`
- `references/doc-specs.md` — section structure for each `docs/_base/` doc
- `references/question-pool.md` — question logic + defaults
- `scripts/gen_repo_map_index.py` — REPO_MAP_INDEX.md generator
