---
name: preparing-skill-briefs
description: >
  Runs a role-based intake interview that progressively elicits skill requirements
  from the user, validates completeness against complexity tier rules, and outputs
  a structured input brief ready for the skill-generator pipeline. Accepts URLs as
  input and fetches them to pre-fill brief fields. Triggers on: "help me design a
  skill", "prepare a skill brief", "interview me about the skill I need", "fill out
  the input brief template", "walk me through skill requirements", "here's the docs
  page, help me build a skill for this". Do NOT use for: generating skills directly
  from descriptions, editing existing SKILL.md files, validating or packaging
  already-generated skills, or explaining what skills are.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebFetch
---

# Preparing Skill Briefs

## Overview

Guides users through a structured intake interview to produce a complete input brief
for the skill-generator pipeline. Adopts three interviewer personas — Domain Analyst,
Workflow Architect, and Safety Auditor — switching roles as the conversation moves
through different brief sections. Tracks which sections are complete, infers reasonable
defaults for unanswered fields, and loops until the user approves the assembled brief.

## Quick Start

```
User: "Help me design a skill for running Ansible playbooks"

→ Skill classifies domain (infrastructure/automation), estimates complexity (moderate),
  and begins the interview with Domain Analyst questions about scope and triggers.
→ After 3-5 exchanges, presents a draft brief for review.
→ User approves → formatted brief ready for /skill-generator.
```

**Fast-path** — paste a partial brief and skip answered sections:

```
User: [pastes a brief with Sections 1-4 filled, Sections 5-8 empty]

→ Skill parses the brief, finds 12 fields filled, 8 gaps remaining.
→ Skips to Workflow Architect questions for Sections 5-6, then Safety Auditor for Section 7.
→ Assembles complete brief → review → handoff.
```

## Pipeline

### Phase 1: Seed

Capture the user's raw idea and establish baseline parameters.

1. **Accept any input format** — a sentence, URL, keyword, vague concept, or a pre-filled brief
2. **If the input contains a pre-filled brief** (partial or complete) — enter fast-path:
   - Parse the brief and identify which fields are already filled vs empty/TBD
   - Run the completeness check against the stated or inferred complexity tier:
     ```bash
     uv run scripts/validate_brief.py --brief output/draft-brief.yaml --tier <tier>
     ```
   - If **complete** — skip directly to Phase 4 (Review & Refine) with the brief as-is
   - If **partially filled** — map filled fields, identify gaps, then enter Phase 2 (Interview) starting from the first section with missing required fields. Skip all sections that are already complete.
   - Announce: "I found [N] fields already filled across Sections [X, Y, Z]. I'll only ask about the gaps in Sections [A, B]."
3. **If the input contains a URL** — fetch it immediately and extract:
   - Product/tool name and domain classification
   - API surface, CLI commands, or configuration patterns
   - Complexity signals (how many moving parts, external dependencies, failure modes)
   - Candidate trigger phrases from the documentation's own language
   - Store extracted data as pre-fill candidates for the interview
3. **Classify domain** — map the idea to a primary domain (e.g., CI/CD, research, documentation, infrastructure). When a URL was fetched, use extracted content as the primary classification signal.
4. **Estimate complexity tier** — use signals from the input:

   | Signal | Tier |
   |--------|------|
   | Single tool, linear steps, no state | Simple (1-3) |
   | Multi-phase, some branching, validation gates | Moderate (4-6) |
   | Loop-back, cross-referencing, state management, safety model | Complex (7-10) |

5. **Record the raw idea verbatim** — never paraphrase or filter at this stage
6. **Announce the plan** — tell the user which sections you'll cover and approximately how many questions to expect. If a URL was fetched, summarize what was extracted and which fields were pre-filled.

**Validation gate:** Domain is classified, complexity tier is estimated, raw idea is captured.

### Phase 2: Interview

Adopt role-appropriate personas and ask targeted questions to fill each brief section.
See `references/interviewer-roles.md` for full persona definitions.

#### Role switching rules

| Brief section | Active role | Focus |
|--------------|-------------|-------|
| Section 1 (Identity) | Domain Analyst | Name, domain, one-liner precision |
| Section 2 (Triggers) | Domain Analyst | Realistic trigger phrases, exclusion boundaries |
| Section 3 (Workflow) | Workflow Architect | Phases, transitions, validation gates |
| Section 4 (Complexity) | Workflow Architect | Conditional routing, loop-back, state needs |
| Section 5 (Tools) | Workflow Architect | Tool selection, runtime dependencies |
| Section 6 (Outputs) | Workflow Architect | Scripts, templates, references design |
| Section 7 (Safety) | Safety Auditor | Constraints, restricted paths, data sensitivity |
| Section 8 (References) | Domain Analyst | URLs, existing skills, prior art |

#### Interview conduct rules

- Ask **2-4 questions per exchange** — never overwhelm with all questions at once
- Each question includes a **one-sentence explanation** of why it matters
- Each question offers a **default value** the user can accept by skipping
- **Probe deeper** when answers are vague — see `references/field-elicitation-guide.md`
- **Skip sections** when complexity tier doesn't require them (see `references/complexity-tier-rules.md`):

  | Tier | Required sections | Optional sections |
  |------|------------------|-------------------|
  | Simple (1-3) | 1, 2 | 3-8 (defaults inferred) |
  | Moderate (4-6) | 1, 2, 3, 4 | 5, 6, 7, 8 |
  | Complex (7-10) | 1, 2, 3, 4, 5, 6 | 7, 8 |

- Track which fields are answered, which are defaulted, and which are still open
- If the user says "skip" or "default" — accept the default and move on
- **During Section 2** — check proposed triggers against `references/trigger-collision-guide.md`. If a collision is detected, warn the user and suggest resolution strategies (add domain qualifier, strengthen exclusions, or accept overlap)

#### URL handling during interview

When the user provides a URL at any point during the interview (not just Phase 1):

1. **Fetch the URL** and extract domain-relevant content
2. **Pre-fill candidate answers** for open fields based on extracted content
3. **Present pre-fills to the user** — "Based on that page, I'd suggest: [field]: [value]. Accept or change?"
4. **Mark URL-derived values** with `[from URL]` in the draft brief so they're distinguishable from user-stated and inferred values
5. **Continue the interview** from where you left off — don't restart

If the fetch fails, note the failure and suggest the user paste the relevant content directly.

#### Tier upgrade detection

Monitor interview answers for signals that the initial complexity estimate is too low.
See `references/complexity-tier-rules.md` § Tier Upgrade Signals for the full trigger list.

When a tier upgrade is detected:

1. **Pause the current question flow**
2. **Explain the upgrade**: "Based on your answers, this looks more like a **[new tier]** skill than **[original tier]**. Specifically: [signal that triggered the upgrade]."
3. **Show what changes**: "This means I'll also need to cover Sections [X, Y] which weren't required at the original tier."
4. **Ask for confirmation**: "Should I proceed with the upgraded tier, or keep the original scope?"
5. **If confirmed** — add the newly-required sections to the interview queue
6. **If rejected** — continue at the original tier but note the mismatch as a warning in the draft brief

**Validation gate:** Every answered question maps to a specific brief field. No orphan answers.

### Phase 3: Synthesize

Assemble all gathered answers into a complete draft brief.

1. **Map answers to fields** — place each response into the correct brief section
2. **Infer defaults** for unanswered fields based on domain and complexity tier
3. **Mark inferred defaults** with `[inferred]` so the user can spot and override them
4. **Run completeness check**:
   ```bash
   uv run scripts/validate_brief.py --brief output/draft-brief.yaml --tier <tier>
   ```
5. **Fill gaps** — if validation reports missing required fields, either:
   - Infer a reasonable default (mark as `[inferred]`), or
   - Queue a follow-up question for the Review phase

**Validation gate:** All required fields populated. Defaults visibly marked. Brief passes tier-appropriate completeness check.

### Phase 4: Review & Refine

Present the assembled brief with a quality score and iterate until approved.

1. **Show the full draft brief** in YAML format
2. **Show the brief quality score** (1-10) with per-dimension breakdown:

   | Dimension | Weight | What it measures |
   |-----------|:------:|-----------------|
   | Field specificity | 25% | Are answers concrete and detailed, or vague/one-word? |
   | Trigger realism | 20% | Do triggers read like real user input? Are there enough? Are exclusions specific? |
   | Phase boundary clarity | 20% | Does each phase have distinct inputs, outputs, and validation gates? |
   | Completeness | 20% | Ratio of filled fields to tier-required fields (penalizes `[inferred]` at half weight) |
   | Safety coverage | 15% | Are safety rules proportional to the skill's risk profile? |

   **Score display format:**
   ```
   Brief Quality: 7.2 / 10
     Field specificity:     8/10  — strong, most fields have concrete answers
     Trigger realism:       6/10  — triggers are generic, consider adding domain-specific phrases
     Phase boundary clarity: 8/10  — all phases have validation gates
     Completeness:          7/10  — 3 fields inferred, 1 field TBD
     Safety coverage:       7/10  — standard rules present, no domain-specific constraints
   ```

3. **Highlight all provenance markers** in a summary list. Three marker types indicate value source:

   | Marker | Source | Specificity score | Completeness weight | Meaning |
   |--------|--------|:-----------------:|:-------------------:|---------|
   | *(none)* | User-stated | 10/10 | 1.0 | User directly provided this value |
   | `[from URL]` | Extracted from fetched URL | 7/10 | 0.7 | Concrete source, but user hasn't confirmed |
   | `[inferred]` | Default or tier-based inference | 5/10 | 0.5 | No direct evidence — user should review |
4. **Offer 3 targeted refinement suggestions** — prioritize suggestions that would raise the lowest-scoring dimension
5. **Ask**: "Approve this brief, or tell me what to change."

**Refinement loop:**
- User provides feedback → integrate changes → re-score → re-render brief → ask again
- Maximum **3 refinement rounds** — after that, present final version and proceed
- User says **"approve"**, **"looks good"**, or **"finalize"** → move to Handoff
- Show the updated score after each round so the user can see improvement

**Minimum quality gate:** If the brief scores **below 5.0** after all 3 refinement rounds:
1. **Do not proceed to Handoff** automatically
2. Show the score breakdown and identify the weakest dimension(s)
3. Warn: "This brief scores [X]/10 — the skill-generator may produce a weak skill. The weakest areas are: [dimensions]. I recommend addressing these before proceeding."
4. Offer specific, actionable fixes for each weak dimension (e.g., "Add 2 more trigger phrases with 4+ words each" for low trigger realism)
5. Ask: "Fix these issues now, or proceed anyway?"
6. If the user says **"proceed anyway"** — move to Handoff but include a `# ⚠ Quality Warning` header in the brief noting the low score

**Validation gate:** User has explicitly approved, or 3 rounds completed. Score ≥5.0, or user has overridden the quality gate.

### Phase 5: Handoff

Output the finalized brief in a format the skill-generator can consume.

1. **Format the brief** as a clean YAML block inside a fenced code block
2. **Validate YAML syntax**:
   ```bash
   uv run scripts/assemble_brief.py --answers output/answers.yaml --tier <tier> --output output/final-brief.yaml
   ```
3. **Present two options**:
   - **Copy-paste**: "Copy the brief below and pass it to `/skill-generator`"
   - **Direct handoff**: "Say 'generate' and I'll invoke the skill-generator with this brief"
4. **Report what was captured**: total fields filled, fields defaulted, sections completed

**Validation gate:** Brief parses as valid YAML. All sections present.

## Scripts

| Script | Purpose | Interface |
|--------|---------|-----------|
| `scripts/validate_brief.py` | Check draft brief completeness and quality score | `--brief <path> --tier <simple\|moderate\|complex> [--score]` → JSON `{complete, missing_fields, warnings, quality_score}` |
| `scripts/assemble_brief.py` | Merge answers into formatted brief, fill defaults | `--answers <path> --tier <tier> --output <path> [--format yaml\|markdown]` → JSON `{output_path, fields_filled, fields_defaulted, fields_from_url}` |

Run via `uv run scripts/<name>.py`.

## Templates

| Template | Purpose | Location |
|----------|---------|----------|
| Blank brief | Clean KB_INPUT_BRIEF template for user preview | `assets/templates/blank_brief.txt` |
| Example brief | Fully filled autoresearch example | `assets/templates/example_brief.txt` |

## Reference Files

| File | Purpose |
|------|---------|
| `references/interviewer-roles.md` | Three persona definitions with switching rules, question banks, and probing strategies |
| `references/field-elicitation-guide.md` | Per-field guidance: good answers, common mistakes, follow-up probes, default inference rules |
| `references/complexity-tier-rules.md` | Required vs optional sections per tier, minimum completeness criteria |
| `references/trigger-collision-guide.md` | Known trigger phrases from common skills, collision detection protocol, resolution strategies |

## Failure Mode Handling

| Failure | Response |
|---------|----------|
| User gives a single word with no context | Ask 2-3 seed questions to establish domain and intent before proceeding |
| User skips all questions | Fill all fields with tier-appropriate defaults, present for review |
| User contradicts earlier answers | Flag the contradiction, ask which version is correct, update the brief |
| URL fetch fails | Note the failure, continue interview without URL data, suggest the user paste relevant content |
| Validation script reports errors | Show the errors, explain what's missing, ask targeted questions to fill gaps |
| User wants to change complexity tier mid-interview | Re-evaluate which sections are required, adjust remaining questions |
| User pastes a brief with invalid YAML | Attempt to parse what's recoverable, show the parse error, and ask the user to fix the broken section or dictate it conversationally |
| User pastes a brief that looks complete but has shallow answers | Run validation — flag fields that technically have values but fail quality checks (e.g., one-word triggers, missing phase validation gates), then interview those specific fields |

## Safety Constraints

- **Never fabricate skill requirements** the user did not express or imply
- **Never output a brief marked as "approved"** without explicit user confirmation
- **Never skip the review phase** — always show the assembled brief before handoff
- **Never infer safety rules or restricted paths** — always ask explicitly
- **Mark all inferred defaults** visibly with `[inferred]` so the user can override them
- **Never read or write** to `.git/`, `.env`, or `secrets/`

## Dependencies

- Python 3.10+
- `uv` (for running scripts)
- No external packages — scripts use Python stdlib only

## Quick Reference Table

| Task | Command/Method | Notes |
|------|---------------|-------|
| Start interview | Describe your skill idea | Any format: sentence, URL, keyword, or partial brief |
| Fast-path from brief | Paste a pre-filled brief | Skips answered sections, interviews only gaps |
| Preview blank template | Read `assets/templates/blank_brief.txt` | Shows all sections and fields |
| See a worked example | Read `assets/templates/example_brief.txt` | Autoresearch skill, fully filled |
| Validate draft brief | `uv run scripts/validate_brief.py --brief <path> --tier <tier>` | JSON output with missing fields |
| Score draft brief | `uv run scripts/validate_brief.py --brief <path> --tier <tier> --score` | Adds quality_score with 5 dimensions |
| Assemble final brief (YAML) | `uv run scripts/assemble_brief.py --answers <path> --tier <tier> --output <path>` | Default YAML format |
| Assemble final brief (Markdown) | `uv run scripts/assemble_brief.py --answers <path> --tier <tier> --output <path> --format markdown` | Copy-pasteable Markdown |
| Skip to handoff | Say "approve" or "finalize" during review | Outputs formatted YAML brief |
| Hand off to generator | Say "generate" after approval | Invokes `/skill-generator` with brief |
