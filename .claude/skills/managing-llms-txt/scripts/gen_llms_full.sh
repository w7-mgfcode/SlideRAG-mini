#!/usr/bin/env bash
# Regenerate llms-full.txt from the core documentation set.
#
# Run from the repository root:  bash .claude/skills/managing-llms-txt/scripts/gen_llms_full.sh
#
# "Core docs" = the entry points an LLM needs for full context. Add docs/_base/*.md
# entries here if the managing-agent-memory skill generates that suite later.
set -euo pipefail

OUT="llms-full.txt"

# Edit this list when the core doc set changes.
CORE_DOCS=(
  README.md
  AGENTS.md
  CLAUDE.md
  docs/architecture.md
  demo/README.md
)

{
  printf '# SlideRAG Mini — Full Documentation\n\n'
  printf '> Presentation-grounded RAG assistant (Python 3.12 + FastAPI + Jinja2; python-pptx extraction; LangChain + LangGraph; persistent Chroma; OpenAI embeddings and chat; one Docker container on AWS EC2). This file inlines the complete content of the core documentation set for full-context LLM consumption. For a navigable index, see `llms.txt`.\n\n'
  printf 'Generated from the core docs listed below. Each section is delimited by an `# ===== File: <path> =====` marker.\n'
  for f in "${CORE_DOCS[@]}"; do
    if [ -f "$f" ]; then
      printf '\n\n# ===== File: %s =====\n\n' "$f"
      sed 's/\r$//' "$f"
    else
      printf '\n\n# ===== File: %s (MISSING) =====\n' "$f" >&2
      echo "WARNING: core doc not found: $f" >&2
    fi
  done
} > "$OUT"

echo "Wrote $OUT ($(wc -l < "$OUT") lines, $(wc -c < "$OUT") bytes)."
