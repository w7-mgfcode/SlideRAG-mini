# Trigger Collision Guide

Known trigger phrases from common skills. Use this during Section 2 (Trigger Boundary)
to detect and warn about overlapping triggers before they cause mis-routing.

## Table of Contents

- [Known Trigger Map](#known-trigger-map)
- [High-Risk Collision Zones](#high-risk-collision-zones)
- [Detection Protocol](#detection-protocol)
- [Resolution Strategies](#resolution-strategies)

## Known Trigger Map

| Skill | Trigger phrases | Domain |
|-------|----------------|--------|
| **archon-rag-workflow** | "any technical question", "architecture decision", "implementation planning", "debugging", "code review", "feature design" | meta / always-on |
| **autoresearch** | "research this", "investigate", "run a study on", "literature review", "experiment on", "what does the research say about" | research |
| **excalidraw-diagram** | "visualize workflows", "visualize architectures", "visualize concepts", "create a diagram", "draw this" | visualization |
| **prompt-architect** | "help me write a better prompt", "improve this prompt", "what framework should I use", "make this prompt more effective" | prompt engineering |
| **generating-skills** (skill-generator) | "generate a skill", "create an agent skill", "custom skill", "skill generator" | meta-tooling |
| **preparing-skill-briefs** | "help me design a skill", "prepare a skill brief", "interview me about the skill I need", "fill out the input brief template", "walk me through skill requirements" | meta-tooling |
| **running-adversarial-dev** | "build this with adversarial review", "use a generator evaluator loop", "adversarially review and iterate", "planner generator evaluator harness" | dev workflow |
| **writing-session-handoffs** | "write a handoff", "session handoff", "end of session", "hand off to next session", "save session context" | session management |

## High-Risk Collision Zones

These phrase patterns are most likely to cause cross-triggering:

| Phrase pattern | Collides with | Why it's risky |
|---------------|---------------|----------------|
| "help me design..." | preparing-skill-briefs, generating-skills | "Design a skill" vs "design a system" — ambiguous intent |
| "research..." | autoresearch, archon-rag-workflow | Always-on RAG catches broad "research" triggers |
| "create..." | generating-skills, excalidraw-diagram | "Create a skill" vs "create a diagram" — verb overlap |
| "improve..." | prompt-architect | "Improve this prompt" vs "improve this code" — domain-dependent |
| "review..." | archon-rag-workflow, running-adversarial-dev | "Code review" vs "adversarial review" — different workflows |
| "visualize..." | excalidraw-diagram | Any visualization request may false-trigger |

## Detection Protocol

During Section 2 of the interview, for each trigger phrase the user proposes:

1. **Exact match check** — does this phrase appear verbatim in the table above?
2. **Substring overlap** — does the key verb + noun pair match? (e.g., "create" + "skill")
3. **Domain adjacency** — is the skill's domain close to a domain in the table?

If any check fires:

```
⚠ Trigger collision detected:
  Your phrase: "help me design a workflow"
  Collides with: preparing-skill-briefs ("help me design a skill")
  Risk: moderate — shared verb "help me design" may cause mis-routing

  Suggestions:
  1. Add domain qualifier: "help me design an Ansible workflow"
  2. Add to exclusions: "Do NOT use for: designing skills or briefs"
  3. Keep as-is if the skills are never installed together
```

## Resolution Strategies

| Strategy | When to use | Example |
|----------|------------|---------|
| **Add domain qualifier** | Phrases are generic but domains differ | "research this" → "research this topic using web sources" (avoids RAG overlap) |
| **Strengthen exclusions** | Skills coexist in the same environment | Add explicit exclusion: "Do NOT use for: prompt engineering tasks" |
| **Rename trigger verb** | Verb is the collision point | "create a skill" → "generate a skill from brief" |
| **Accept overlap** | Skills are never co-installed, or one is always-on | archon-rag-workflow is always-on — other skills can't avoid its triggers |
| **Use explicit invocation** | Collision is unresolvable | Add a note: "For disambiguation, invoke with `/skill-name`" |

### Special case: always-on skills

`archon-rag-workflow` triggers on **every** technical interaction. New skills in the
research, architecture, or debugging domains will inevitably overlap. This is expected
and not a problem — always-on skills layer underneath, while domain-specific skills
take priority when their triggers match more specifically.

**Rule:** Don't avoid broad verbs just because an always-on skill uses them. Instead,
make your triggers more specific so Claude's trigger-matching ranks your skill higher
for its domain.
