# Complexity Tier Rules

Documents which brief sections are required vs optional at each complexity tier,
minimum completeness criteria, and scoring methodology.

## Table of Contents

- [Tier Definitions](#tier-definitions)
- [Section Requirements by Tier](#section-requirements-by-tier)
- [Completeness Criteria](#completeness-criteria)
- [Scoring Methodology](#scoring-methodology)
- [Tier Upgrade Signals](#tier-upgrade-signals)

## Tier Definitions

| Tier | Score | Characteristics | Example skills |
|------|-------|-----------------|----------------|
| Simple | 1-3 | Linear workflow, 2-3 steps, single tool, no state, no branching | codebase-visualizer, file-formatter |
| Moderate | 4-6 | Multi-phase, conditional logic, validation gates, possible loop-back | run-nx-generator, preparing-skill-briefs |
| Complex | 7-10 | Loop-back, cross-referencing, state management, progressive disclosure, full safety model | autoresearch, skill-generator |

## Section Requirements by Tier

| Section | Simple (1-3) | Moderate (4-6) | Complex (7-10) |
|---------|:---:|:---:|:---:|
| 1. Identity | **Required** | **Required** | **Required** |
| 2. Triggers | **Required** | **Required** | **Required** |
| 3. Workflow | Default (3 steps) | **Required** | **Required** |
| 4. Complexity | Default (simple) | **Required** | **Required** |
| 5. Tools | Default (standard set) | Optional | **Required** |
| 6. Outputs | Default (SKILL.md only) | Optional | **Required** |
| 7. Safety | Default (standard rules) | Optional | Recommended |
| 8. References | Optional | Optional | Optional |

**"Default" means:** The field is populated automatically with a tier-appropriate
default value. The user is informed of the default but not required to answer.

**"Required" means:** The field must have a non-default answer — either from the
user directly or inferred from sufficient context with `[inferred]` marking.

**"Optional" means:** The field can be left as TBD. The generator will handle it.

**"Recommended" means:** Not strictly required, but skipping it produces a weaker
brief that the generator will need to compensate for.

## Completeness Criteria

### Simple tier (1-3)

A simple brief is **complete** when:
- [ ] `name` is kebab-case and ≤64 chars
- [ ] `domain` is classified
- [ ] `one_liner` describes what the skill DOES
- [ ] At least 3 trigger phrases provided
- [ ] At least 2 exclusions provided
- [ ] Complexity tier confirmed as simple

**Minimum fields:** 6

### Moderate tier (4-6)

A moderate brief is **complete** when all simple criteria are met, plus:
- [ ] `workflow_type` is specified (linear, multi-phase, or iterative-loop)
- [ ] At least 3 workflow phases defined with inputs, outputs, and validation
- [ ] `has_conditional_routing` answered (yes/no with explanation if yes)
- [ ] `has_loop_back` answered
- [ ] `has_state_management` answered
- [ ] `autonomous` answered

**Minimum fields:** 12

### Complex tier (7-10)

A complex brief is **complete** when all moderate criteria are met, plus:
- [ ] `tools_needed` lists specific tools with MCP qualifiers where applicable
- [ ] `runtime_dependencies` specified
- [ ] At least 1 script defined with name, purpose, and interface
- [ ] At least 1 reference file defined with name and purpose
- [ ] Safety rules addressed (even if "standard defaults apply")

**Minimum fields:** 17

## Scoring Methodology

Calculate the complexity score by summing applicable signals:

| Signal | Points | Condition |
|--------|:------:|-----------|
| Base workflow | +1 | Every skill gets 1 |
| Multi-phase | +1 | 3+ distinct phases |
| Many phases | +1 | 5+ distinct phases |
| Conditional routing | +2 | Workflow branches based on conditions |
| Loop-back | +2 | Workflow can return to earlier phases |
| State management | +2 | Persistent state across invocations |
| External dependencies | +1 | Requires web access, APIs, or MCP tools |
| Autonomous operation | +1 | Runs without user input |
| Multiple output types | +1 | Produces 3+ different document/file types |

**Score → tier mapping:**
- 1-3 → Simple
- 4-6 → Moderate
- 7-10 → Complex

**Maximum possible score:** 12 (cap at 10)

## Tier Upgrade Signals

During the interview, watch for signals that the initial tier estimate is too low:

| Signal during interview | Action |
|------------------------|--------|
| User describes "if this then that" logic | Upgrade to moderate if currently simple |
| User mentions "go back to step 1 if..." | Upgrade to moderate (loop-back = +2) |
| User wants the skill to "remember" between runs | Upgrade to moderate or complex (state = +2) |
| User describes 5+ phases | Consider complex |
| User mentions external APIs or MCP tools | Add +1, re-evaluate tier |
| User describes safety-critical operations | Recommend complex tier for safety model |

When upgrading, inform the user: "Based on what you've described, this looks more
like a [tier] skill than [original tier]. I'll adjust the interview to cover the
additional sections needed."
