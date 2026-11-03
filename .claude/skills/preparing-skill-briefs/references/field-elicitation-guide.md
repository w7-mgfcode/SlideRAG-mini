# Field Elicitation Guide

Per-field guidance for every input brief field. For each field: what good answers
look like, common mistakes, follow-up probes, and default inference rules.

## Table of Contents

- [Section 1: Identity](#section-1-identity)
- [Section 2: Trigger Boundary](#section-2-trigger-boundary)
- [Section 3: Workflow Shape](#section-3-workflow-shape)
- [Section 4: Complexity Signals](#section-4-complexity-signals)
- [Section 5: Tools & Environment](#section-5-tools--environment)
- [Section 6: Output Expectations](#section-6-output-expectations)
- [Section 7: Safety & Constraints](#section-7-safety--constraints)
- [Section 8: Reference Material](#section-8-reference-material)

## Section 1: Identity

### name

| Aspect | Guidance |
|--------|----------|
| Good answer | `running-ansible`, `preparing-skill-briefs`, `fixing-ci-pipelines` |
| Bad answer | `ansible`, `helper`, `my-tool`, `skill_v2` |
| Probe | "What verb describes the primary action? Use that as the gerund." |
| Default rule | Extract the main verb + domain noun from the one-liner, kebab-case it |
| Constraints | Kebab-case, max 64 chars, gerund preferred, must match folder name |

### domain

| Aspect | Guidance |
|--------|----------|
| Good answer | `infrastructure`, `CI/CD`, `research`, `documentation`, `meta-tooling` |
| Bad answer | `coding`, `stuff`, `general` |
| Probe | "If this skill lived in a bookstore, which section would it go in?" |
| Default rule | Classify from keywords in the raw idea |
| Constraints | Single primary domain; secondary domains noted but not primary |

### one_liner

| Aspect | Guidance |
|--------|----------|
| Good answer | "Runs Ansible playbooks against inventory with dry-run validation and rollback safety." |
| Bad answer | "Helps with Ansible." / "An Ansible skill." |
| Probe | "Complete this sentence: 'When you invoke this skill, it...'" |
| Default rule | Combine domain + primary action + key differentiator |
| Constraints | One sentence, describes what the skill DOES (not what it IS) |

## Section 2: Trigger Boundary

### triggers

| Aspect | Guidance |
|--------|----------|
| Good answer | `["run the ansible playbook", "deploy to staging with ansible", "execute playbook on hosts"]` |
| Bad answer | `["ansible", "deploy"]` (too broad) |
| Probe | "Imagine a developer typing in Claude Code. What exact words would they use?" |
| Default rule | Derive 3-5 phrases from one-liner, varying verb and context |
| Constraints | 3-6 realistic phrases, specific enough to avoid false triggers |

### exclusions

| Aspect | Guidance |
|--------|----------|
| Good answer | `["write new ansible playbooks from scratch", "debug ansible module code", "manage ansible galaxy collections"]` |
| Bad answer | `["other stuff"]` |
| Probe | "What tasks sound similar but should trigger a different skill or no skill?" |
| Default rule | Identify 2-3 adjacent tasks in the same domain that this skill should NOT handle |
| Constraints | Must be concrete — "other tasks" is not an exclusion |

## Section 3: Workflow Shape

### workflow_type

| Aspect | Guidance |
|--------|----------|
| Good answer | `iterative-loop`, `multi-phase`, `linear` |
| Bad answer | `complex`, `standard` |
| Probe | "Does the workflow ever go backward to an earlier step? Does it branch?" |
| Default rule | Linear if no loops or branches mentioned; multi-phase if 3+ steps; iterative-loop if user describes repetition |

### phases

| Aspect | Guidance |
|--------|----------|
| Good answer | Each phase has: name, description (one sentence), inputs, outputs, validation |
| Bad answer | "Step 1: do the thing. Step 2: finish." |
| Probe | "What does step N need to start? What does it produce? How do you know it worked?" |
| Default rule | Derive 3-4 phases from the workflow description; add validation gates between each |
| Constraints | 2-6 phases typical; each must have clear boundaries |

**Common mistakes:**
- Phases that overlap ("analyze and execute" should be two separate phases)
- Missing validation gates between phases
- Outputs that don't match the next phase's inputs

## Section 4: Complexity Signals

### complexity_tier

| Aspect | Guidance |
|--------|----------|
| Good answer | `moderate (5)` — with numeric score |
| Bad answer | `medium` / `it's not too hard` |
| Probe | "On a 1-10 scale, where 1 is 'run one command' and 10 is 'autonomous research agent', where does this fall?" |
| Default rule | Score based on: phase count (+1 per phase), conditional routing (+2), loop-back (+2), state (+2), external deps (+1) |

### has_conditional_routing / has_loop_back / has_state_management

| Aspect | Guidance |
|--------|----------|
| Good answer | `yes — the workflow branches when validation fails` |
| Bad answer | `maybe` / `not sure` |
| Probe for routing | "Are there any 'if X then do Y, else do Z' decisions?" |
| Probe for loop-back | "Can you ever go back to an earlier step?" |
| Probe for state | "Does the skill need to remember anything from the last time it ran?" |
| Default rule | No for all unless evidence suggests otherwise |

## Section 5: Tools & Environment

### tools_needed

| Aspect | Guidance |
|--------|----------|
| Good answer | `["Read", "Write", "Bash", "Glob", "Grep"]` or `["Bash", "WebFetch", "GitHub:create_issue"]` |
| Bad answer | `["all of them"]` |
| Probe | "Which Claude tools does each workflow phase actually use?" |
| Default rule | Read, Write, Bash, Glob, Grep (standard set) |
| Constraints | MCP tools must use fully qualified names: `ServerName:tool_name` |

### runtime_dependencies

| Aspect | Guidance |
|--------|----------|
| Good answer | `["Python 3.10+", "uv", "Docker"]` |
| Bad answer | `["whatever's needed"]` |
| Probe | "What needs to be installed on the machine for the scripts to work?" |
| Default rule | Python 3.8+ stdlib only |

## Section 6: Output Expectations

### scripts_needed

| Aspect | Guidance |
|--------|----------|
| Good answer | Name, purpose, and interface (flags → output format) for each script |
| Bad answer | "A script to do stuff" |
| Probe | "What deterministic operation does this script handle? What flags does it take?" |
| Default rule | One validate script, one for the primary deterministic operation |

### templates_needed

| Aspect | Guidance |
|--------|----------|
| Good answer | Name + what document the agent fills using this template |
| Bad answer | "A template" |
| Probe | "What document does the skill produce that should start from a scaffold?" |
| Default rule | Based on output document types in the workflow |

### references_needed

| Aspect | Guidance |
|--------|----------|
| Good answer | Name + what heavy documentation this holds |
| Bad answer | "Some docs" |
| Probe | "What information is too long for SKILL.md but Claude needs access to?" |
| Default rule | Based on domain complexity; moderate+ skills typically need 1-3 reference files |

## Section 7: Safety & Constraints

### safety_rules

| Aspect | Guidance |
|--------|----------|
| Good answer | `["Never delete production data without backup confirmation", "Never commit secrets to generated code"]` |
| Bad answer | `["Be careful"]` |
| Probe | "What's the worst thing that could happen if this skill malfunctions? Write a rule to prevent it." |
| Default rule | Never fabricate data. Never run destructive commands without confirmation. |
| **IMPORTANT** | Never infer safety rules — always ask explicitly |

### restricted_paths

| Aspect | Guidance |
|--------|----------|
| Good answer | `[".git/", ".env", "secrets/", "node_modules/"]` |
| Bad answer | Not specified |
| Probe | "Are there directories or files this skill should never read or write to?" |
| Default rule | `.git/`, `.env`, `secrets/` |
| **IMPORTANT** | Never infer restricted paths — always ask explicitly |

### data_sensitivity

| Aspect | Guidance |
|--------|----------|
| Good answer | `low` / `medium` / `high` with explanation |
| Bad answer | Not specified |
| Probe | "Does this skill handle credentials, PII, or proprietary data?" |
| Default rule | `low` |

## Section 8: Reference Material

### urls

| Aspect | Guidance |
|--------|----------|
| Good answer | Direct links to official docs, API references, or tool pages |
| Bad answer | "Google it" |
| Probe | "Is there a documentation page or API reference the generator should read?" |
| Default rule | None (TBD) |

### existing_skills

| Aspect | Guidance |
|--------|----------|
| Good answer | Names of .kb_ref/ skills that share domain or structure |
| Bad answer | "Similar skills exist" |
| Probe | "Are there existing skills in this project that solve a related problem?" |
| Default rule | Auto-detected from domain matching against .kb_ref/ |

### prior_art

| Aspect | Guidance |
|--------|----------|
| Good answer | Paths to existing scripts, workflows, or internal tools |
| Bad answer | "We have some scripts" |
| Probe | "Are there existing scripts or workflows that do part of what this skill should do?" |
| Default rule | None |
