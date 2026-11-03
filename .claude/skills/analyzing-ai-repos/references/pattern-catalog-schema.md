# Pattern Catalog Schema

## Table of Contents

1. [Overview](#overview)
2. [Pattern Entry Fields](#pattern-entry-fields)
3. [Pattern Types](#pattern-types)
4. [Cross-References](#cross-references)
5. [Example Catalog](#example-catalog)

---

## Overview

The pattern catalog is the intermediate state produced during the ANALYZE phase.
It records every significant pattern detected in the repository, with evidence
linking each pattern to specific files and code locations.

The catalog is used in two downstream phases:
- **RESEARCH** — generates scoped search queries from pattern types and frameworks
- **DOCUMENT** — populates logic-map.md and diagrams.md with evidence-backed content

---

## Pattern Entry Fields

Each pattern entry in the catalog follows this structure:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier: `PAT_NNN` (e.g., `PAT_001`) |
| `type` | enum | yes | One of the defined pattern types (see below) |
| `name` | string | yes | Human-readable pattern name |
| `description` | string | yes | What this pattern does in the repo context |
| `files` | string[] | yes | File paths where this pattern is implemented |
| `evidence` | string | yes | Specific code snippets or structural signals |
| `frameworks` | string[] | no | Related frameworks/libraries (e.g., "langchain", "prefect") |
| `connections` | string[] | no | IDs of related patterns (e.g., `PAT_003`) |
| `confidence` | enum | yes | `high` (explicit code) / `medium` (inferred) / `low` (heuristic) |
| `notes` | string | no | Additional observations or caveats |

---

## Pattern Types

| Type | Description | Detection signals |
|------|-------------|-------------------|
| `dag-workflow` | Explicit step ordering without cycles | Task definitions with dependency declarations, topological execution |
| `state-machine` | Phase/status enums with transition logic | Enum types for states, transition functions, state validation |
| `chain-pipeline` | Sequential function composition | Pipe operators, `.then()` chains, sequential middleware |
| `agent-loop` | LLM call -> tool use -> LLM call cycles | While loops with LLM calls, tool dispatch, observation handling |
| `eval-harness` | Test fixtures, scoring functions, benchmarks | Test case loading, metric computation, result aggregation |
| `prompt-mgmt` | Template files, variable injection, versioning | Template loading, string formatting, prompt registries |
| `retrieval` | Document fetching, embedding, similarity search | Vector stores, embedding calls, retrieval chains |
| `routing` | Conditional dispatch based on input/state | Router classes, intent classification, conditional branching |
| `memory` | Persistent context across interactions | Memory stores, conversation history, context windows |
| `tool-registry` | Dynamic tool/function registration and dispatch | Tool decorators, function registries, schema definitions |
| `config-driven` | Behavior controlled by YAML/JSON configuration | Config loading, schema validation, environment-based settings |
| `error-handling` | Structured error recovery and fallback logic | Try/catch patterns, retry decorators, fallback chains |

---

## Cross-References

Patterns often connect to each other. Record these connections:

- **Feeds into**: Pattern A produces output consumed by Pattern B
- **Depends on**: Pattern A requires Pattern B to function
- **Alternatives**: Pattern A and Pattern B solve the same problem differently
- **Wraps**: Pattern A is a higher-level abstraction over Pattern B

Use the `connections` field with the related pattern's ID.

---

## Example Catalog

```yaml
patterns:
  - id: PAT_001
    type: agent-loop
    name: "ReAct agent loop"
    description: "Main agent execution loop using ReAct pattern — observe, think, act, repeat"
    files:
      - "src/agent/react.py"
      - "src/agent/executor.py"
    evidence: "while not done: observation = tool.run(action); thought = llm(observation)"
    frameworks: ["langchain"]
    connections: ["PAT_002", "PAT_003"]
    confidence: high

  - id: PAT_002
    type: tool-registry
    name: "Dynamic tool registry"
    description: "Tools registered via decorators and dispatched by name"
    files:
      - "src/tools/registry.py"
      - "src/tools/base.py"
    evidence: "@register_tool decorator, tool_map dict, dispatch by tool_name"
    frameworks: []
    connections: ["PAT_001"]
    confidence: high

  - id: PAT_003
    type: memory
    name: "Conversation buffer memory"
    description: "Sliding window memory storing last N messages for context"
    files:
      - "src/memory/buffer.py"
    evidence: "ConversationBufferMemory class, max_messages config, trim_messages()"
    frameworks: ["langchain"]
    connections: ["PAT_001"]
    confidence: high
```
