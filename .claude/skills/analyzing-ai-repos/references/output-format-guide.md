# Output Format Guide

## Table of Contents

1. [General Rules](#general-rules)
2. [overview.md](#overviewmd)
3. [logic-map.md](#logic-mapmd)
4. [diagrams.md](#diagramsmd)
5. [research-notes.md](#research-notesmd)
6. [context.md](#contextmd)
7. [Cross-Reference Rules](#cross-reference-rules)
8. [Incremental Diff Annotations](#incremental-diff-annotations)

---

## General Rules

All output documents follow these conventions:

- **Markdown format** with consistent heading hierarchy
- **Mermaid diagrams** use fenced code blocks with `mermaid` language tag
- **Cross-references** between documents use `[text](filename.md#section)` format
- **Pattern IDs** from the catalog (`PAT_NNN`) are used consistently across all docs
- **No fabrication** — every claim must trace to a specific file or code location
- **File paths** are relative to the repo root
- **Incremental mode** adds a diff header when `.prev/` exists

---

## overview.md

**Purpose:** High-level architecture summary for someone encountering the repo for the first time.

**Required sections:**

| Section | Content |
|---------|---------|
| Repository Identity | Name, URL (if available), primary language, repo type classification |
| Tech Stack | Languages, frameworks, key libraries with versions if detectable |
| Architecture Summary | 2-3 paragraph description of how the system works |
| Key Decisions | Notable architectural choices and their rationale (if inferrable) |
| Entry Points | Main entry files and how to run/use the system |
| Directory Structure | Tree view of important directories with purpose annotations |

**Quality criteria:**
- Someone unfamiliar with the repo should understand its purpose and structure after reading
- Tech stack lists specific versions where detectable (e.g., "LangChain 0.2.x" not just "LangChain")
- Architecture summary explains the WHY, not just the WHAT

---

## logic-map.md

**Purpose:** Detailed interconnections, data flow, and dependency chains.

**Required sections:**

| Section | Content |
|---------|---------|
| Module Dependencies | Which modules import/use which other modules |
| Data Flow | How data moves through the system (input -> processing -> output) |
| Control Flow | Decision points, routing logic, branching paths |
| Integration Points | External services, APIs, databases, file systems |
| Pattern Connections | How detected patterns (PAT_NNN) relate to each other |

**Quality criteria:**
- Every connection is backed by a specific import, function call, or data reference
- Includes at least one Mermaid diagram showing the dependency graph
- Pattern IDs link back to the catalog and forward to diagrams.md

---

## diagrams.md

**Purpose:** Visual representations of the repo's architecture and logic.

**Required diagrams:**

| Diagram type | Mermaid syntax | When to include |
|---|---|---|
| Component map | `graph TD` | Always — shows major components and connections |
| Execution flow | `flowchart TD` | Always — traces the main execution path |
| Sequence diagram | `sequenceDiagram` | When agent interactions or multi-step processes exist |
| State diagram | `stateDiagram-v2` | When state machines or phase transitions are detected |
| Class diagram | `classDiagram` | When significant class hierarchies exist |

**Quality criteria:**
- Maximum 30 nodes per diagram — split larger systems into sub-diagrams
- Every node label is a real module, class, or function name from the repo
- Diagrams use consistent styling (no mixing of arrow types within one diagram)
- Each diagram has a descriptive title and brief explanation paragraph

---

## research-notes.md

**Purpose:** Curated external research findings linked to specific repo patterns.

**Required sections:**

| Section | Content |
|---------|---------|
| Research Scope | What was searched and why (linked to detected patterns) |
| Findings per Pattern | Grouped by pattern ID, each finding with source URL |
| Best Practices | Recommended approaches from authoritative sources |
| Alternatives | Alternative frameworks or patterns that solve similar problems |
| Trends | Current direction of the ecosystem relevant to this repo |

**Quality criteria:**
- Every finding links to a specific pattern (PAT_NNN) from the catalog
- Source URLs are included for all external findings
- "Best practices" are from authoritative sources (official docs, reputable blogs)
- No generic "AI trends" content — everything is scoped to detected patterns

**Note:** This file is empty if `--research skip` was used. Include a note explaining why.

---

## context.md

**Purpose:** Pure distilled knowledge base artifact — the primary downstream deliverable.

**Structure:**
```markdown
# <Repo Name> — Context Document

## Identity
[One paragraph: what this is, what it does, who it's for]

## Core Concepts
[Key abstractions, mental models, terminology specific to this repo]

## Architecture
[Condensed architecture from overview.md — essential facts only]

## Patterns
[Condensed pattern catalog — type, name, purpose, key files]

## Integration Points
[External dependencies, APIs, services]

## Key Files
[Top 10-15 files with one-line purpose descriptions]

## Usage
[How to run, configure, and extend the system]

## Research Context
[Condensed research findings — only the most relevant best practices]
```

**Quality criteria:**
- Self-contained — someone can understand the repo from this file alone
- Under 300 lines — aggressively condense, link to other docs for details
- No redundant content — if it's better explained in another output file, summarize and link
- Optimized for LLM context — structured so an AI can use this as reference material

---

## Cross-Reference Rules

Documents reference each other using these conventions:

1. **Pattern IDs** (`PAT_001`, `PAT_002`) are consistent across all documents
2. **File links** use relative markdown links: `[overview](overview.md#section)`
3. **Diagram references** from logic-map.md point to specific diagrams in diagrams.md
4. **Research links** from research-notes.md reference patterns by ID

---

## Incremental Diff Annotations

When running in incremental mode, each document gets a diff header:

```markdown
> **Incremental update** — compared against previous analysis from [date]
> - Sections added: [list]
> - Sections changed: [list]
> - Sections removed: [list]
```

Place this immediately after the document title (# heading).
