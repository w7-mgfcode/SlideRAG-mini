---
name: managing-llms-txt
description: Creates and updates the llms.txt and llms-full.txt files at a repository root, following the llms.txt convention (https://llmstxt.org). llms.txt is a curated, markup-free index of the documentation tree (H1 project name + blockquote summary + H2 link sections + an Optional section); llms-full.txt inlines the full content of the core docs for full-context LLM consumption. Use when a user asks to "create llms.txt", "update llms.txt", "generate llms-full.txt", "refresh the LLM docs index", "/managing-llms-txt", or after docs are added/moved/renamed so the index goes stale. Do NOT use for AGENTS.md / CLAUDE.md (use managing-agent-memory) or for editing the underlying docs themselves.
---

# managing-llms-txt

Create and maintain the **llms.txt convention** files at the repo root:

| File | Role |
|------|------|
| `llms.txt` | Curated, markup-free **index** of the documentation tree — navigation for reasoning engines. |
| `llms-full.txt` | The **full inlined content** of the core docs, concatenated for one-shot LLM context. |

The convention (Jeremy Howard / llmstxt.org) gives LLMs a clean map of a project's docs without
the navigation, scripts, and markup that bloat raw HTML or a sitemap.

## llms.txt format — follow exactly

1. An H1 with the project name: `# ProjectName`
2. A `>` blockquote with a one- or two-sentence project summary.
3. Zero or more free-text paragraphs of additional context (no headings).
4. H2 sections, each a list of links: `- [Title](url): one-line description`.
5. A final `## Optional` section for links an LLM may skip when context is tight.

```
# Project Name
> Brief project summary.

Additional context paragraph.

## Core Documentation
- [Quick Start](url): Description of the resource.

## Optional
- [Additional Resources](url): Supplementary information.
```

For a repo with **no hosted documentation site**, use relative repo paths as the link targets —
the file then serves LLMs reading the repository directly.

## llms-full.txt format

Same H1 + blockquote header, then the complete markdown content of the **core docs** inlined,
each section delimited by an `# ===== File: <path> =====` marker. "Core docs" means the
entry-point and reference files (README, AGENTS.md, CLAUDE.md, the `docs/_base/` suite) — not
every doc in the tree; inlining everything makes the file unmanageably large.

## Procedure

### 1. Scan the documentation surface

```bash
ls README.md AGENTS.md CLAUDE.md llms.txt 2>/dev/null
find docs -name '*.md' -type f 2>/dev/null | sort
ls PRPs/*.md PRPs/INITIAL/*.md 2>/dev/null
```

Group what you find: entry points, reference suite (`docs/_base/`), architecture/ADRs,
workflow docs, per-phase deep dives, validation standards, PRPs/specs, optional-feature briefs.

### 2. Write / update llms.txt

- H1 = project name; blockquote = the one-line summary from README/AGENTS.md.
- One context paragraph: note the llms.txt convention and (if applicable) that the repo has no
  hosted site so links are relative paths.
- H2 sections grouping the most important docs; each link gets a concise, accurate description.
- Lower-priority material (per-phase deep dives, PRPs, validation standards, optional features)
  goes under `## Optional`.
- **Update mode:** add new docs, drop links to deleted docs, fix moved paths, refresh stale
  descriptions. Preserve the existing section structure where it still fits.

### 3. Generate / regenerate llms-full.txt

Run `scripts/gen_llms_full.sh` (carried with this skill), or follow its logic: write the
header, then concatenate each core doc behind its `# ===== File: <path> =====` marker,
normalising CRLF to LF. Re-run it on every docs change so the full file never drifts.

### 4. Verify

```bash
head -3 llms.txt                       # H1 then blockquote
grep -c '^## ' llms.txt                # has H2 sections, incl. Optional
grep -oE '\]\(([^)]+)\)' llms.txt | sed -E 's/^\]\(//;s/\)$//' \
  | while read -r p; do [ -e "${p%%#*}" ] || echo "BROKEN: $p"; done
wc -l llms-full.txt
```

## Anti-Patterns — never do these

1. Inlining every doc into llms-full.txt — keep it to the core set.
2. Adding HTML, scripts, or navigation chrome — the whole point is clean markdown.
3. Letting link descriptions go stale after a doc is renamed or moved.
4. Skipping the H1-then-blockquote header — tools rely on that exact structure.
5. Editing the underlying docs — this skill only indexes and concatenates them.

## Reference Files

- `scripts/gen_llms_full.sh` — regenerates `llms-full.txt` from the core doc list.
