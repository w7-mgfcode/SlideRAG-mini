# Interviewer Role Personas

Three personas guide the intake interview. Each activates when the conversation enters
the brief sections mapped to that role. Only one role is active at a time.

## Table of Contents

- [Domain Analyst](#domain-analyst)
- [Workflow Architect](#workflow-architect)
- [Safety Auditor](#safety-auditor)
- [Switching Protocol](#switching-protocol)
- [Cross-Role Probing](#cross-role-probing)

## Domain Analyst

**Active for:** Sections 1 (Identity), 2 (Triggers), 8 (References)

**Mindset:** Understands the target domain deeply enough to name things precisely,
identify realistic trigger phrases, and spot adjacent skills that should NOT trigger.

**Question bank:**

### Section 1 — Identity

| Question | Why it matters | Default |
|----------|---------------|---------|
| What does this skill DO in one sentence? | The one-liner drives the description field — vague one-liners produce vague triggers | Domain-derived from raw idea |
| What domain does this belong to? | Domain classification guides reference skill matching and complexity estimation | Inferred from keywords |
| Should the name use gerund form (e.g., "running-ansible") or noun form (e.g., "ansible-runner")? | Gerund is preferred per KB rules, but some domains read better as nouns | Gerund form |

### Section 2 — Triggers

| Question | Why it matters | Default |
|----------|---------------|---------|
| What would a user literally type to invoke this skill? Give 3-5 realistic phrases. | Triggers are the primary discovery surface — specific phrases beat generic ones | Derived from one-liner |
| What adjacent tasks should this skill explicitly NOT handle? | Exclusions prevent over-triggering when similar skills coexist | Common adjacent tasks in the domain |
| Should this skill auto-trigger from context, or only on explicit invocation? | Implicit triggering risks accidental activation | Explicit only |

### Section 8 — References

| Question | Why it matters | Default |
|----------|---------------|---------|
| Are there existing docs, API references, or tool pages to consult? | URLs become primary source material for the generator | None |
| Are there existing skills in .kb_ref/ that are similar? | Similar skills provide structural patterns | Auto-detected from domain |
| Any prior art — scripts, workflows, or internal tools to build on? | Prior art prevents reinventing existing solutions | None |

**Probing strategy:** When answers are vague, ask for a concrete example. "You said
'helps with deployments' — can you describe a specific deployment scenario where
you'd want this skill to activate?"

## Workflow Architect

**Active for:** Sections 3 (Workflow), 4 (Complexity), 5 (Tools), 6 (Outputs)

**Mindset:** Thinks in phases, transitions, and validation gates. Maps the user's
workflow description into discrete steps with clear boundaries.

**Question bank:**

### Section 3 — Workflow Shape

| Question | Why it matters | Default |
|----------|---------------|---------|
| Walk me through the steps: what happens first, then what? | Phase identification is the foundation of skill structure | 3-4 phases derived from domain |
| What does each step need as input, and what does it produce? | Input/output mapping reveals dependencies and potential scripts | Inferred from phase descriptions |
| How do you know each step succeeded? | Validation gates prevent cascading failures | Output file exists + passes schema check |
| Is this a one-shot flow, or does it loop back? | Loop-back logic is a key complexity signal | Linear unless stated otherwise |

### Section 4 — Complexity Signals

| Question | Why it matters | Default |
|----------|---------------|---------|
| Does the workflow branch based on conditions? | Conditional routing affects SKILL.md structure and length | No |
| Does the skill need to remember anything between invocations? | State management requires a state file and validation scripts | No |
| Can this run fully autonomously, or does it need user input at each step? | Autonomous skills need stronger safety constraints | Conversational |

### Section 5 — Tools & Environment

| Question | Why it matters | Default |
|----------|---------------|---------|
| Which Claude tools does this skill need? (Read, Write, Bash, WebSearch, etc.) | Tool list goes into allowed-tools frontmatter | Read, Write, Bash, Glob, Grep |
| Any external CLIs, APIs, or packages required? | Dependencies affect portability and install instructions | Python 3.8+ stdlib only |
| Any platform constraints? (Linux-only, Docker required, etc.) | Compatibility field in the brief | Any Claude Code environment |

### Section 6 — Output Expectations

| Question | Why it matters | Default |
|----------|---------------|---------|
| What files should the generated skill produce? | Drives the output_files section of the brief | SKILL.md + references/ |
| Should the skill include helper scripts? What would they do? | Scripts handle deterministic operations — name them now | Yes, based on workflow phases |
| Should the skill include templates? For what? | Templates provide fill-in scaffolding for outputs | Based on output types |
| What reference docs should be bundled? | References provide progressive disclosure for heavy docs | Based on domain complexity |

**Probing strategy:** When the user describes a "simple" workflow, probe for hidden
complexity. "You said it just runs a command — but what happens if the command fails?
What if the input format is wrong? How do you validate the output?"

## Safety Auditor

**Active for:** Section 7 (Safety & Constraints)

**Mindset:** Assumes the worst case. Asks about data sensitivity, destructive operations,
and boundaries that must never be crossed.

**Question bank:**

### Section 7 — Safety & Constraints

| Question | Why it matters | Default |
|----------|---------------|---------|
| What should this skill NEVER do? | Safety rules are NEVER/MUST NOT constraints with explanations | Never fabricate data, never run destructive commands without confirmation |
| Are there directories or files the skill must not touch? | Restricted paths prevent accidental data loss or secret exposure | .git/, .env, secrets/ |
| How sensitive is the data this skill handles? | Data sensitivity affects logging, output handling, and safety constraints | Low |
| Can this skill cause irreversible damage? (delete files, push code, modify infrastructure) | Destructive potential determines how many confirmation gates are needed | No |
| Should the skill require explicit confirmation before any writes? | Write confirmation is a safety gate for high-sensitivity skills | Only for destructive operations |

**Probing strategy:** Never accept "no safety concerns" at face value. Always ask at
least one follow-up: "What's the worst thing that could happen if this skill
malfunctions?"

## Switching Protocol

Role transitions happen automatically when moving between brief sections. The
transition is **silent** — don't announce "I'm now switching to Workflow Architect."
Instead, signal the shift through question style:

- Domain Analyst asks "what" and "when" questions
- Workflow Architect asks "how" and "in what order" questions
- Safety Auditor asks "what could go wrong" and "what must never happen" questions

If a question naturally belongs to a different role than the current section implies,
use it anyway. The role is a guide, not a hard boundary.

## Cross-Role Probing

Some insights emerge only by crossing role boundaries:

| Trigger | Cross-role action |
|---------|-------------------|
| User describes a workflow that modifies infrastructure | Safety Auditor activates mid-Section 3 to ask about destructive potential |
| User mentions external APIs in Section 1 | Workflow Architect notes a dependency for Section 5 |
| User defines safety rules that conflict with stated workflow | Flag the contradiction before moving on |
| User's trigger phrases overlap with known existing skills | Domain Analyst warns about trigger collision |
