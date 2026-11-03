# Repo Type Classification Guide

## Table of Contents

1. [Agent Framework](#agent-framework)
2. [Prompt Library](#prompt-library)
3. [Eval Harness](#eval-harness)
4. [Workflow Orchestrator](#workflow-orchestrator)
5. [Hybrid](#hybrid)
6. [Detection Priority](#detection-priority)

---

## Agent Framework

Repos that implement or extend AI agent systems with tool use, memory, and reasoning loops.

**Strong signals:**
- Directories: `agents/`, `tools/`, `chains/`, `memory/`, `retrieval/`
- Files: `agent.py`, `tool_registry.py`, `react.py`, `chain.py`
- Imports: `langchain`, `langgraph`, `autogen`, `crewai`, `semantic_kernel`
- Configs: `agent.yaml`, `tools.yaml`, `agent_config.json`
- README mentions: "agent", "tool use", "ReAct", "function calling", "chain of thought"

**Weak signals:**
- Generic `src/` with LLM API calls but no agent structure
- Single-file scripts that call OpenAI/Anthropic APIs

**Key analysis targets:**
- Entry points (how agents are initialized and run)
- Tool definitions (what tools are available, how they're registered)
- Memory/state management (how context persists across turns)
- Routing logic (how the agent decides which tool/action to take)

---

## Prompt Library

Repos focused on managing, versioning, or composing prompts and templates.

**Strong signals:**
- Directories: `prompts/`, `templates/`, `instructions/`, `examples/`
- Files: `*.prompt`, `*.jinja2`, `system_prompt.md`, `few_shot.yaml`
- Imports: `jinja2`, `promptflow`, `guidance`, `dspy`
- Configs: `prompts.yaml`, `templates.yaml`
- README mentions: "prompt engineering", "template", "few-shot", "system prompt"

**Weak signals:**
- A single `prompts/` directory inside a larger app
- Inline prompt strings without a management layer

**Key analysis targets:**
- Template structure (variables, conditionals, includes)
- Composition patterns (how prompts chain or nest)
- Versioning strategy (how prompt versions are tracked)
- Testing approach (how prompts are evaluated)

---

## Eval Harness

Repos designed to evaluate, benchmark, or test AI model outputs.

**Strong signals:**
- Directories: `evals/`, `benchmarks/`, `scoring/`, `metrics/`, `judges/`
- Files: `eval_*.py`, `benchmark.py`, `scorer.py`, `judge.py`
- Imports: `pytest`, `evaluate`, `ragas`, `deepeval`, `promptfoo`, `inspect_ai`
- Configs: `eval.yaml`, `benchmark.yaml`, `promptfooconfig.yaml`
- README mentions: "evaluation", "benchmark", "scoring", "metrics", "accuracy"

**Weak signals:**
- Standard unit tests without AI-specific evaluation logic
- A single eval script inside a larger project

**Key analysis targets:**
- Test case structure (inputs, expected outputs, scoring criteria)
- Metric definitions (what's being measured, how scores are computed)
- Dataset management (how test data is loaded, versioned, sampled)
- Judge/scorer patterns (LLM-as-judge, rubric-based, statistical)

---

## Workflow Orchestrator

Repos that define and execute multi-step workflows, pipelines, or DAGs.

**Strong signals:**
- Directories: `workflows/`, `pipelines/`, `dags/`, `flows/`, `steps/`
- Files: `workflow.py`, `pipeline.py`, `dag.py`, `orchestrator.py`
- Imports: `prefect`, `airflow`, `dagster`, `luigi`, `celery`, `temporal`
- Configs: `workflow.yaml`, `pipeline.yaml`, `dag.yaml`, `flow.yaml`
- README mentions: "workflow", "pipeline", "orchestration", "DAG", "task graph"

**Weak signals:**
- Simple sequential scripts without explicit workflow definitions
- Makefile-only build pipelines

**Key analysis targets:**
- Step/task definitions (what each step does, inputs/outputs)
- Dependency graph (how steps connect, parallel vs sequential)
- Error handling (retries, fallbacks, compensating actions)
- State persistence (checkpoints, resume from failure)

---

## Hybrid

Repos that combine multiple types (e.g., an agent framework with built-in evals).

**Detection rule:** When the top two types score within 15% of each other, or when
three or more types have significant presence.

**Key analysis targets:**
- Identify the primary type (highest score) and secondary types
- Map how the types interact (e.g., agents use prompts from the prompt library)
- Focus the analysis on the integration points between types
- Document each type's contribution separately in the logic map

---

## Detection Priority

When signals conflict, prioritize in this order:

1. **Config files** (strongest signal — explicit declarations)
2. **Import patterns** (framework-specific, hard to fake)
3. **Directory names** (structural intent)
4. **File name patterns** (weaker, more ambiguous)
5. **README mentions** (weakest — aspirational vs actual)
