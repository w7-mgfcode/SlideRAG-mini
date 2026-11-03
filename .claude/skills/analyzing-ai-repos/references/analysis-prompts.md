# Analysis Prompts by Repo Type

## Table of Contents

1. [Agent Framework](#agent-framework)
2. [Prompt Library](#prompt-library)
3. [Eval Harness](#eval-harness)
4. [Workflow Orchestrator](#workflow-orchestrator)
5. [Hybrid](#hybrid)
6. [Universal Prompts](#universal-prompts)

Pre-written analysis prompts the skill asks itself during Phase 2 deep reads.
Each prompt targets a specific aspect of the repo type and guides structured extraction.

---

## Agent Framework

### Architecture probes
- "What is the main agent execution loop? Trace from user input → LLM call → tool dispatch → observation → next step."
- "How are tools registered and discovered? Is it static (hardcoded list) or dynamic (decorator/registry pattern)?"
- "What memory/context management strategy is used? Buffer, summary, vector, or hybrid?"
- "How does the agent decide when to stop? Max iterations, confidence threshold, explicit stop tool, or task completion signal?"

### Integration probes
- "What LLM providers are supported? How is the provider abstracted (direct API, SDK wrapper, adapter pattern)?"
- "How are tool results formatted and fed back to the LLM? Raw text, structured JSON, or template?"
- "Is there a routing layer that dispatches to different agents or sub-agents based on input type?"

### Quality probes
- "What error handling exists for tool failures, LLM timeouts, or malformed responses?"
- "Is there retry logic, and if so, does it modify the prompt on retry?"
- "Are there guardrails or safety checks on tool invocations (e.g., confirmation for destructive actions)?"

---

## Prompt Library

### Architecture probes
- "How are prompts organized? By task type, by model, by domain, or flat?"
- "Is there a templating system? Jinja2, f-strings, custom variable injection?"
- "How are prompts versioned? Git history, explicit version fields, or separate version directories?"
- "Is there a prompt composition pattern (chaining, nesting, includes)?"

### Integration probes
- "How are prompts loaded at runtime? File read, registry lookup, or embedded?"
- "Are there prompt-specific configs (temperature, max_tokens, stop sequences) stored alongside templates?"
- "Is there a testing/evaluation layer for prompts (golden outputs, A/B comparison)?"

### Quality probes
- "Are there prompt quality guidelines or style constraints enforced?"
- "How are prompt variables documented? Type hints, descriptions, required vs optional?"
- "Is there a migration path when prompts need updating (deprecation, backwards compatibility)?"

---

## Eval Harness

### Architecture probes
- "What evaluation types are supported? Accuracy, faithfulness, relevance, safety, latency?"
- "How are test cases structured? Input/expected-output pairs, rubrics, or reference-free?"
- "What scoring mechanism is used? LLM-as-judge, exact match, regex, custom metrics?"
- "How are results aggregated? Per-test, per-suite, per-model, with statistical analysis?"

### Integration probes
- "What models/providers can be evaluated? How is the model interface abstracted?"
- "How are test datasets managed? Files, databases, generated on-the-fly?"
- "Is there CI/CD integration for automated eval runs?"

### Quality probes
- "Is there inter-rater reliability measurement for LLM-as-judge evals?"
- "How are eval results stored and compared across runs?"
- "Are there baseline comparisons or regression detection mechanisms?"

---

## Workflow Orchestrator

### Architecture probes
- "How are workflow steps/tasks defined? Python functions, YAML configs, decorators, or classes?"
- "What is the execution model? Sequential, parallel, DAG-based, event-driven?"
- "How are dependencies between steps declared and resolved?"
- "Is there state persistence? Checkpoints, resume-from-failure, idempotent steps?"

### Integration probes
- "What external systems are orchestrated? Databases, APIs, file systems, message queues?"
- "How are credentials and secrets managed? Environment variables, vault, config?"
- "Is there a UI or CLI for workflow management and monitoring?"

### Quality probes
- "What happens when a step fails? Retry, skip, compensate, or abort?"
- "Is there observability (logging, tracing, metrics) for workflow execution?"
- "How are workflow definitions tested? Unit tests for steps, integration tests for flows?"

---

## Hybrid

For hybrid repos, combine probes from all detected types, then add:

### Integration probes
- "How do the different components (agents, prompts, evals, workflows) reference each other?"
- "Is there a shared data model or schema across components?"
- "What is the primary component vs supporting components?"
- "Are components tightly coupled or loosely coupled (shared interfaces, events, direct calls)?"

---

## Universal Prompts

Apply these to every repo regardless of type:

### Entry point analysis
- "What is the main entry point? How does a user start using this system?"
- "What are the configuration options? Environment variables, config files, CLI flags?"
- "What is the minimum viable setup to get this running?"

### Dependency analysis
- "What are the hard dependencies vs optional dependencies?"
- "Are there version constraints or compatibility issues noted in the codebase?"
- "What external services must be available at runtime?"

### Code quality signals
- "Is there a testing strategy? Unit, integration, e2e?"
- "Is there type checking (mypy, TypeScript strict, Go interfaces)?"
- "Is there documentation beyond README? API docs, architecture docs, contributing guide?"
- "What CI/CD pipeline exists? What checks run on every PR?"
