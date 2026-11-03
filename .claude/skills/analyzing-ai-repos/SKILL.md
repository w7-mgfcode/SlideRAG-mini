---
name: analyzing-ai-repos
description: >
  Analyzes AI/ML repositories (agent frameworks, prompt pipelines, eval systems,
  workflow orchestrators) to extract logic flow, dependencies, and interconnections.
  Builds structured context documents with Mermaid diagrams in .kb/designs/<repo-name>/.
  Supports local paths and GitHub URLs with incremental diff on re-runs. Triggers on:
  "analyze this AI repo", "map this framework", "build context from this repository",
  "understand this toolkit's workflow", "deep dive into this AI project",
  "compare these AI repos". Do NOT use for: simple single-file questions, general
  coding tasks, quick keyword searches (use Explore agent), code debugging, or bug fixing.
---

# Analyzing AI Repos

## Overview

Performs deep structural and semantic analysis of AI/ML repositories — agent frameworks,
prompt pipelines, eval harnesses, workflow orchestrators — to extract logic flow,
dependencies, and interconnections. Produces structured output documents with Mermaid
diagrams plus a machine-readable `analysis.json`. Supports research-driven enrichment,
incremental re-analysis with diff tracking, focused subdirectory analysis, and multi-repo
comparison.

## Quick Start

```
User: "analyze this AI repo at ~/projects/langchain-agents"

-> Skill classifies repo type, scans file tree, extracts patterns
-> Builds dependency graph and logic flow map
-> Runs targeted research on detected frameworks
-> Generates output documents in .kb/designs/langchain-agents/
```

With URL:
```
User: "analyze https://github.com/anthropics/claude-code"

-> Clones repo, then runs the same four-phase pipeline
```

Focus on subdirectory:
```
User: "analyze ~/projects/big-monorepo --focus src/agents"

-> Scopes analysis to src/agents/ only
```

Multi-repo comparison:
```
User: "compare these repos: ~/projects/langchain-app ~/projects/crewai-app"

-> Analyzes each repo, then generates cross-repo comparison document
```

Flags:
```
--research deep|light|skip    (default: deep)
--incremental                 (diff against previous analysis)
--focus <directory>           (scope analysis to subdirectory)
```

## Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| classify_repo.py | `uv run scripts/classify_repo.py --path <repo>` | Detect repo type from file patterns |
| build_tree.py | `uv run scripts/build_tree.py --path <repo> --type <type>` | Filtered file tree with relevance scoring |
| diff_analysis.py | `uv run scripts/diff_analysis.py --current <path> --previous <path>` | Compare current vs .prev/ analysis |
| validate_mermaid.py | `uv run scripts/validate_mermaid.py <path>` | Validate Mermaid syntax in output docs |

## Templates

| Template | Purpose | Output location |
|----------|---------|-----------------|
| `assets/templates/overview.txt` | Architecture summary scaffold | `.kb/designs/<repo>/overview.md` |
| `assets/templates/logic_map.txt` | Interconnections and data flow | `.kb/designs/<repo>/logic-map.md` |
| `assets/templates/diagrams.txt` | Mermaid diagram collection | `.kb/designs/<repo>/diagrams.md` |
| `assets/templates/research_notes.txt` | Curated research findings | `.kb/designs/<repo>/research-notes.md` |
| `assets/templates/context.txt` | Distilled context document | `.kb/designs/<repo>/context.md` |
| `assets/templates/summary_card.txt` | One-page executive summary | `.kb/designs/<repo>/summary-card.md` |
| `assets/templates/analysis_json.txt` | Machine-readable analysis | `.kb/designs/<repo>/analysis.json` |

## Pipeline

### Phase 1: INGEST

Accept input and prepare the repo for analysis.

1. **Parse input** — determine if local path or URL. If multiple paths provided, enter multi-repo mode (see Multi-Repo Analysis below).
2. **If URL** — clone to a temp directory:
   ```bash
   git clone --depth 1 <url> /tmp/ai-repo-analyst/<repo-name>
   ```
   If clone fails (private repo, rate limit), ask the user for auth or a local path.
3. **If `--focus` provided** — validate the subdirectory exists, then scope all subsequent analysis to that path only. Report the narrowed scope to the user.
4. **Classify repo type**:
   ```bash
   uv run scripts/classify_repo.py --path <repo>
   ```
   Output: `{repo_type, confidence, signals[]}` where `repo_type` is one of:
   `agent-framework | prompt-library | eval-harness | workflow-orchestrator | hybrid`
5. **Build filtered file tree**:
   ```bash
   uv run scripts/build_tree.py --path <repo> --type <repo_type> --max-files 500
   ```
   Output: `{tree[], key_files[], stats}` — key_files are ranked by relevance.

**Validation gate:** `repo_type` assigned, `key_files` list non-empty, tree stats show reasonable file count.

### Phase 2: ANALYZE

Deep-read key files to extract patterns and build structural maps.

1. **Load analysis prompts** — read `references/analysis-prompts.md` and select the prompt set matching the detected `repo_type`. Use the universal prompts for every repo.

2. **Read key files** — use the `key_files` list from Phase 1. For each file extract:
   - Imports and dependencies (what frameworks, libraries, tools)
   - Function/class signatures (public API surface)
   - Tool calls and MCP references (agent tool usage patterns)
   - Prompt templates (system prompts, few-shot examples, chains)
   - State management patterns (config files, state machines, session handling)
   - Configuration and environment patterns

3. **Build pattern catalog** — classify detected patterns:

   | Pattern type | Detection signal |
   |---|---|
   | DAG workflow | Explicit step ordering, no cycles |
   | State machine | Phase/status enums, transition logic |
   | Chain/pipeline | Sequential function composition |
   | Agent loop | LLM call -> tool use -> LLM call cycles |
   | Eval harness | Test fixtures, scoring functions, benchmarks |
   | Prompt management | Template files, variable injection, versioning |
   | Retrieval | Vector stores, embedding calls, similarity search |
   | Routing | Conditional dispatch, intent classification |
   | Memory | Persistent context, conversation history |
   | Tool registry | Dynamic tool registration, function dispatch |
   | Config-driven | YAML/JSON-controlled behavior |
   | Error handling | Structured recovery, retry, fallback |

4. **Build dependency graph** — map how modules, files, and components reference each other. Use Mermaid `graph TD` syntax for the dependency structure.

5. **Build logic flow map** — trace the main execution path from entry point through phases/steps. Use Mermaid `flowchart TD` or `sequenceDiagram` as appropriate.

**For large repos (>200 key files):** Use the Agent tool with `subagent_type: Explore` to parallelize deep-reads across different directories.

**Validation gate:** `pattern_catalog` has >=1 entry. Dependency graph and logic flow are valid Mermaid. All key files processed or explicitly skipped with reason.

### Phase 3: RESEARCH

Generate targeted queries and gather best practices. Skip this phase if `--research skip`.

1. **Generate scoped queries** — based on detected patterns and frameworks:
   - `deep` mode: 5-8 queries, fetch top 3 results per query
   - `light` mode: 2-3 queries, fetch top 1 result per query

   Query template: `"<framework_name> <pattern_type> best practices <year>"`

   Example queries for a LangChain agent repo:
   - "LangChain agent routing patterns best practices 2025"
   - "LangChain state management ReAct loop architecture"
   - "AI agent evaluation frameworks comparison"

2. **Search and fetch**:
   ```
   WebSearch(query="<scoped query>")
   WebFetch(url="<top result URL>")
   ```

3. **Filter and rank** — keep only results that directly relate to patterns found in Phase 2. Discard generic "AI trends" content.

4. **Cross-reference** — link each research finding to a specific pattern or component from the analysis.

**Validation gate:** Each query returns >=1 relevant result. No unscoped queries. All findings linked to repo patterns.

### Phase 4: DOCUMENT

Synthesize everything into output documents.

1. **Check incremental mode** — if `--incremental` and `.kb/designs/<repo>/` exists:
   - Copy current outputs to `.kb/designs/<repo>/.prev/`
   - After generating new outputs, run diff:
     ```bash
     uv run scripts/diff_analysis.py --current .kb/designs/<repo> --previous .kb/designs/<repo>/.prev
     ```
   - Add diff annotations to each document header

2. **Generate output files** — read each template from `assets/templates/`, fill with analysis data, write to `.kb/designs/<repo-name>/`:

   | File | Template | Content |
   |------|----------|---------|
   | `overview.md` | `overview.txt` | Architecture summary, tech stack, repo classification, key decisions |
   | `logic-map.md` | `logic_map.txt` | Data flow, dependency chains, module interconnections |
   | `diagrams.md` | `diagrams.txt` | Mermaid flowcharts, sequence diagrams, component maps |
   | `research-notes.md` | `research_notes.txt` | Curated findings linked to specific repo patterns |
   | `context.md` | `context.txt` | Pure distilled context — the knowledge base artifact |
   | `summary-card.md` | `summary_card.txt` | One-page executive summary with top patterns and key diagram |
   | `analysis.json` | `analysis_json.txt` | Machine-readable: full pattern catalog, scores, metadata |

3. **Validate Mermaid syntax**:
   ```bash
   uv run scripts/validate_mermaid.py .kb/designs/<repo-name>
   ```
   Fix any reported errors before finalizing.

4. **Final validation**:
   - All 7 files exist and are non-empty
   - Mermaid syntax valid (validate_mermaid.py passes)
   - Cross-references between documents use consistent PAT_NNN IDs
   - analysis.json is valid JSON
   - If incremental, diff annotations are present

**Validation gate:** All files written. Mermaid valid. Cross-references consistent. JSON parseable.

## Multi-Repo Analysis

When multiple repo paths/URLs are provided, analyze each repo individually through the full pipeline, then generate an additional cross-repo comparison document.

1. **Run Phases 1-4** for each repo independently (use Agent tool to parallelize if >2 repos)
2. **Generate comparison** — `.kb/designs/_comparison/comparison.md` containing:
   - Side-by-side classification and pattern summary
   - Shared vs unique patterns across repos
   - Framework and dependency overlap
   - Architectural similarities and differences
   - Mermaid diagram showing cross-repo relationships

Only activate multi-repo mode when the user explicitly provides multiple repos or asks to "compare."

## Failure Mode Handling

| Failure | Response |
|---------|----------|
| URL clone fails | Detect error, ask user for auth credentials or local path fallback |
| Repo is huge (>10k files) | Cap at 500 files via build_tree.py, suggest `--focus` to narrow scope |
| classify_repo.py returns low confidence | Present classification with signals, ask user to confirm or override |
| Research queries return noise | Tighten query scope to exact framework + pattern. If still noisy, skip research with warning |
| Incremental diff on restructured repo | Fall back to full overwrite, keep .prev/, warn user |
| Mermaid diagram too complex | Split into sub-diagrams per module (max 30 nodes per diagram) |
| Key files are binary or non-text | Skip with log entry, focus on text-based source files |
| Empty or minimal repo | Report minimal findings, suggest the repo may be a stub or WIP |
| validate_mermaid.py reports errors | Fix syntax errors in diagrams, re-validate until clean |

## Safety Constraints

- **Never execute code** from analyzed repos — read-only analysis only
- **Never fabricate patterns** or dependencies not found in the actual repo source
- **Never overwrite .prev/** without user confirmation on incremental re-run
- **Never process secrets** — skip `.env`, credentials, tokens; log skipped files
- **Never run generic research** — all queries must be scoped to detected patterns
- **Never include PII** or sensitive data in output documents

## Restricted Paths

Do not read or analyze:
- `.git/`
- `.env`, `.env.*`
- `secrets/`, `credentials/`
- `node_modules/`, `__pycache__/`, `.venv/`, `venv/`
- Binary files (images, compiled artifacts, model weights)

## Dependencies

- Python 3.10+
- `uv` (for running scripts)
- `git` (for URL cloning)
- No external packages — scripts use Python stdlib only

## Reference Files

| File | Purpose |
|------|---------|
| `references/repo-type-guide.md` | Classification rules and detection signals per repo type |
| `references/pattern-catalog-schema.md` | Schema for the pattern catalog intermediate state |
| `references/output-format-guide.md` | Quality criteria and formatting rules for output documents |
| `references/analysis-prompts.md` | Pre-written analysis prompts per repo type for Phase 2 deep reads |

## Quick Reference Table

| Task | Command | Notes |
|------|---------|-------|
| Classify a repo | `uv run scripts/classify_repo.py --path <repo>` | Run first |
| Build file tree | `uv run scripts/build_tree.py --path <repo> --type <type>` | After classify |
| Validate Mermaid | `uv run scripts/validate_mermaid.py <path>` | Before finalizing |
| Full analysis | Provide repo path or URL | Runs all 4 phases |
| Focused analysis | "analyze <repo> --focus src/agents" | Scopes to subdirectory |
| Light research | "analyze <repo> --research light" | 2-3 queries only |
| Skip research | "analyze <repo> --research skip" | Analysis + docs only |
| Incremental re-run | "analyze <repo> --incremental" | Diffs against .prev/ |
| Compare repos | Provide multiple paths/URLs | Adds cross-repo comparison |
| Compare versions | `uv run scripts/diff_analysis.py --current <new> --previous <old>` | After incremental |
