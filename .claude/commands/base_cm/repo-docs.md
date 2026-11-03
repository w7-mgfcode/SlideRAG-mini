---
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
description: Deep-analyze the entire repository and generate 6 LLM-optimized documentation artifacts under docs/_base/: index map, relationship graph, concept guide, DevOps onboarding doc, AI Engineer onboarding doc, and a living CLAUDE.md memory file.
---

# ROLE & PERSONA
You are a **Senior Documentation Architect** with deep expertise in DevOps, platform engineering, and knowledge management for AI-assisted workflows. You produce documentation that is equally useful for human engineers AND LLM agents navigating codebases.

---

# PHASE 0 — PLAN MODE (MANDATORY, DO NOT SKIP)
Before writing a single file, switch into read-only exploration. Follow this exact sequence:

```
STEP 0 — Ensure output directory exists
  bash: mkdir -p docs/_base

STEP 1 — Map the filesystem
  bash: find . -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.terraform/*' -not -path '*/vendor/*' | sort

STEP 2 — Identify all documentation files
  glob: **/*.md, **/*.txt, **/*.rst, **/*.adoc

STEP 3 — Identify all infrastructure and config files
  glob: **/*.yaml, **/*.yml, **/*.tf, **/*.hcl, **/*.json, **/Dockerfile*, **/Makefile, **/Jenkinsfile, **/*.sh

STEP 4 — Identify source code
  glob: **/*.py, **/*.go, **/*.ts, **/*.js (skip node_modules, vendor)

STEP 5 — Read key entry-point files
  Read: README.md, CLAUDE.md, .claude/CLAUDE.md (if present), Makefile, docker-compose.yml, Chart.yaml (Helm)

STEP 6 — Identify CI/CD pipelines
  glob: .github/workflows/*.yml, .gitlab-ci.yml, Jenkinsfile, .circleci/config.yml

STEP 7 — Scan for service boundaries and API contracts
  grep: "kind:", "apiVersion:", "def ", "func ", "class ", "export default", "router.", "@app.route"

STEP 8 — Inventory all findings in a mental map before proceeding
```

**DO NOT create any files until Phase 0 is fully complete.**

---

# PHASE 1 — GENERATE DOCUMENT: `docs/_base/00-INDEX.md`
> **Purpose**: Master navigation map. Designed so an LLM agent can locate ANY topic in ONE lookup.

## Content Requirements
- First section: **Repository at a Glance** (5-10 sentences: what this repo is, its primary purpose, and the technology stack)
- Second section: **Document Registry** — a table with columns:
  | File Path | Type | Topics Covered | When to Read |
  Where "Type" is one of: `Architecture`, `Runbook`, `Config Reference`, `API Contract`, `Test`, `CI/CD`, `Security`, `Onboarding`
- Third section: **Topic-to-File Lookup** — a two-column table:
  | If you need to know about... | Read this file |
  Cover at minimum: deployment, rollback, secrets, networking, storage, auth, monitoring, testing, CI/CD triggers, environment config
- Fourth section: **Quick Command Reference** — the 10 most common commands an engineer will run (build, test, deploy, lint, connect to cluster, etc.), extracted from Makefile/README/CI pipelines
- Footer: `<!-- LLM-AGENT-INDEX: v1 | repo: {repo_name} | generated: {date} -->`

## Formatting Rules
- Use relative Markdown links for all cross-references
- Max 400 lines
- Every section header must include a short machine-readable anchor (e.g., `## Document Registry {#doc-registry}`)

---

# PHASE 2 — GENERATE DOCUMENT: `docs/_base/01-RELATIONSHIPS.md`
> **Purpose**: Visualize how every component, service, and config connects. Mandatory Mermaid diagrams.

## Content Requirements

### Section A: Component Relationship Diagram
Produce a `graph TD` Mermaid diagram that shows:
- All services / applications (boxes)
- All infrastructure dependencies: databases, queues, storage, secrets managers (cylinders/diamonds)
- All external integrations: cloud providers, registries, SaaS tools
- Directional arrows labeled with the interaction type: `-->|HTTP/gRPC|`, `-->|reads|`, `-->|publishes|`, `-->|mounts|`

### Section B: Data Flow Diagram
Produce a `sequenceDiagram` Mermaid block for the **primary happy-path flow** (e.g., a deploy trigger → final running pod, or an API request → database response).

### Section C: CI/CD Pipeline Flow
Produce a `graph LR` Mermaid showing the full pipeline: trigger → stages → artifacts → deploy targets. Include branch conditions if found.

### Section D: Dependency Matrix
Prose table:
| Component | Depends On | Depended On By | Critical Path? |

### Section E: Environment Topology
If multiple environments exist (dev/staging/prod), show how they differ using a comparison table.

## Formatting Rules
- All Mermaid blocks must be wrapped in triple-backtick `mermaid` fences
- Include a "How to read this document" intro paragraph
- Cross-link to `docs/_base/00-INDEX.md` for each named component

---

# PHASE 3 — GENERATE DOCUMENT: `docs/_base/02-CONCEPT-GUIDE.md`
> **Purpose**: Teach any engineer (including an LLM) what this repo IS and HOW it works conceptually, from zero.

## Content Requirements
Structure as a progressive narrative — each section builds on the previous:

1. **The Problem This Repo Solves** — What pain point does it address? What would break without it?
2. **Mental Model** — One analogy or metaphor that captures the system's purpose
3. **Key Concepts Glossary** — Table of domain-specific terms:
   | Term | Plain-English Definition | Where it Appears in Code |
4. **Architecture Decisions** — For each major tech choice found (e.g., "Why Helm?", "Why ArgoCD?", "Why this folder structure?"), provide a 2-3 sentence rationale. Infer from code if no ADR docs exist.
5. **The Request/Event Lifecycle** — Walk through what happens step-by-step when the primary action occurs (e.g., "when a developer pushes code..."). Use numbered steps.
6. **Configuration Model** — How is the system configured? Environment variables? ConfigMaps? Helm values? Show the hierarchy.
7. **Failure Modes** — What are the known or likely failure scenarios? How does the system respond?

## Formatting Rules
- Target audience: a competent engineer who has NEVER seen this repo before
- Max reading time: 15 minutes
- No code blocks longer than 20 lines; use snippets with `// ...` for brevity

---

# PHASE 4 — GENERATE DOCUMENT: `docs/_base/03-DEVOPS-ONBOARDING.md`
> **Purpose**: Day-1 reference card for a new DevOps/platform engineer joining the team. Immediately actionable.

## Content Requirements

### Part 1: Environment Setup Checklist
A numbered checklist of everything needed to work with this repo:
- [ ] Required CLI tools and their minimum versions (kubectl, helm, terraform, etc.) — infer from scripts/CI
- [ ] Authentication setup (cloud provider credentials, kubeconfig, registry login)
- [ ] Required environment variables (scan for `os.getenv`, `process.env`, `${VAR}` patterns)
- [ ] Repository clone and local setup steps

### Part 2: Day-1 Verification Commands
5-10 commands the engineer should run to confirm their environment is working. Include expected successful output (one line each).

### Part 3: Deployment Runbook (Standard Path)
Step-by-step guide for the standard deployment procedure. Include:
- Pre-flight checks
- Deployment command(s)
- How to verify success
- How to verify health post-deploy

### Part 4: Rollback Procedure
Exact commands to roll back to the previous state. Label clearly: IMMEDIATE ROLLBACK vs FULL ROLLBACK.

### Part 5: Secrets & Credentials Map
Table:
| Secret Name | Where it Lives | How to Rotate | Who Owns It |
(Scan for Vault references, K8s secrets, SSM parameters, `.env.example`)

### Part 6: Monitoring & Alerting
- Where to find dashboards (Grafana, Datadog, etc.)
- Key metrics to watch
- Alert channels (Slack, PagerDuty, etc.) — infer from config files

### Part 7: Common Troubleshooting Scenarios
At least 5 scenarios in format:
**Symptom**: `<what the engineer sees>`
**Likely Cause**: `<root cause>`
**Fix**: `<exact command or action>`

### Part 8: Who to Contact
Infer from git log, CODEOWNERS, or README:
| Area | Contact / Team | Channel |

## Formatting Rules
- Use checkboxes `- [ ]` for all action items
- Every command block must be copy-pasteable (no placeholders without explanation)
- Add `> ⚠️ WARNING:` callouts for any destructive operations

---

# PHASE 5 — GENERATE DOCUMENT: `docs/_base/04-AI-ENGINEER-ONBOARDING.md`
> **Purpose**: Day-1 reference for an AI/ML engineer or someone integrating LLMs into or alongside this repo. Covers prompt engineering surface, agentic touchpoints, model context, and safe AI-assisted workflows.

## Content Requirements

### Part 1: AI Integration Surface Map
Identify and list every place where AI/LLM tooling touches this repo:
- Claude Code CLAUDE.md files and their current contents
- Slash commands in `.claude/commands/` and what each does
- Subagent definitions in `.claude/agents/`
- Any `.env` or config keys referencing model names, API endpoints, or AI providers
- Prompt templates or system prompt files (scan for `system_prompt`, `SYSTEM`, `<instructions>` patterns)
- Any Python/TS SDK usage of `anthropic`, `openai`, `langchain`, `litellm`

Produce a table:
| AI Touchpoint | File Path | Type | Description |
Where "Type" is one of: `Memory`, `SlashCommand`, `Subagent`, `Prompt`, `SDK Call`, `Config`

### Part 2: CLAUDE.md Anatomy
If a `CLAUDE.md` exists in the repo, provide:
- A section-by-section breakdown of what it currently instructs Claude to do
- An assessment: what is well-defined vs what is missing or vague
- Recommended additions (use `<!-- TODO: add -->` markers)

If no `CLAUDE.md` exists, note this as a gap and reference the one created in Phase 6.

### Part 3: Prompt Engineering Guide for This Repo
Based on the codebase's domain, provide actionable prompting guidance:

**Effective task patterns for this codebase:**
- How to ask Claude Code to navigate this repo's structure (e.g., "grep for X in the Y directory")
- How to frame infrastructure change requests (e.g., "using Plan Mode first, then...")
- How to ask for safe, idempotent operations vs destructive ones

**Repo-specific context to always provide:**
List the 5-7 pieces of context that make Claude responses significantly better for THIS repo (infer from tech stack):
| Context to Include | Why It Matters | Example Phrasing |

**Anti-patterns to avoid:**
At least 3 prompting mistakes specific to this repo's domain (e.g., "never ask Claude to apply Helm charts without --dry-run first")

### Part 4: Agentic Workflow Safety Rules
Rules for running Claude Code autonomously against this repo:

```
SAFE FOR AUTO-ACCEPT MODE:
- [ ] {infer from repo: e.g., reading files, generating docs, running tests}
- [ ] {e.g., linting, formatting}

REQUIRE PLAN MODE FIRST:
- [ ] {e.g., any change to Kubernetes manifests}
- [ ] {e.g., any Terraform modifications}
- [ ] {e.g., database schema changes}

NEVER AUTOMATE (human approval required):
- [ ] {e.g., production deployments}
- [ ] {e.g., secret rotation}
- [ ] {e.g., destructive kubectl/terraform operations}
```

### Part 5: Context Window Management for This Repo
Practical guidance on feeding this repo to an LLM efficiently:
- Which files to `@mention` for common task types (deploy task → mention these files; debug task → mention those)
- Files to NEVER include in context (too large, auto-generated, irrelevant): scan for `*.lock`, `*-generated.*`, large JSON fixtures
- Recommended `/memory` additions after first week of working with Claude Code on this repo

Produce a quick-reference table:
| Task Type | Files to Include in Context | Files to Exclude |

### Part 6: AI-Assisted Development Workflows
Step-by-step recipes for common AI-assisted tasks specific to this repo:

**Recipe 1: AI-assisted code review**
```
1. Stage your changes: git add -p
2. Run: claude --permission-mode plan -p "Review staged changes for security and correctness. Focus on {repo-specific concern}."
3. Review the plan output
4. If approved, proceed with standard review process
```

**Recipe 2: AI-assisted debugging**
(Tailor to the repo's primary language/framework found in Phase 0)

**Recipe 3: AI-assisted documentation update**
```
1. After any significant change, run: /repo-docs
2. Review diffs in docs/_base/
3. Commit updated docs alongside the code change
```

### Part 7: Model & Token Considerations
- Estimated token count of key files (bash: `wc -c` on large files, divide by 4)
- Which tasks benefit from Opus vs Sonnet vs Haiku for this codebase
- Recommended `max_tokens` for common operations

| Operation | Recommended Model | Why |
|---|---|---|
| Full repo analysis | Opus | Needs deep reasoning across many files |
| Single-file edits | Sonnet | Balanced speed/quality |
| Search & grep tasks | Haiku | Fast, read-only, low cost |

### Part 8: MCP & Tool Integration Opportunities
Based on the repo's tech stack, suggest relevant MCP servers or tool integrations:
- If Kubernetes detected → suggest `kubectl` MCP or bash tool patterns
- If Terraform detected → suggest state inspection patterns
- If CI/CD detected → suggest pipeline introspection commands
- List any existing tool permissions in `.claude/settings.json`

## Formatting Rules
- Use checkboxes `- [ ]` for all safety rules and checklists
- Every code/command block must be copy-pasteable
- Add `> 💡 TIP:` callouts for non-obvious AI workflow optimizations
- Add `> ⚠️ WARNING:` for any operation that could cause Claude to make irreversible changes

---

# PHASE 6 — UPDATE OR CREATE: `CLAUDE.md`
> **Purpose**: Keep the Claude Code project memory file current and LLM-optimized.

## Rules
- If `CLAUDE.md` already exists: **append** a new section `## Learnings from Documentation Pass` — do NOT overwrite existing content
- If it does not exist: create it from scratch following the structure below

## CLAUDE.md Structure (if creating new)
```markdown
# {Repo Name} — Claude Code Memory

## Quick Context
{2-3 sentences: what this repo does, primary tech stack, environment count}

## Critical Commands
```bash
# Build
{command}
# Test  
{command}
# Deploy
{command}
```

## Architecture Summary
{3-5 bullet points: key components and their roles}

## Conventions
- {Naming convention 1}
- {Config convention 2}
- {Branch/PR convention 3}

## Docs Map
- @docs/_base/00-INDEX.md — Master navigation index
- @docs/_base/01-RELATIONSHIPS.md — Component graph + Mermaid diagrams
- @docs/_base/02-CONCEPT-GUIDE.md — Conceptual deep-dive
- @docs/_base/03-DEVOPS-ONBOARDING.md — DevOps day-1 runbook
- @docs/_base/04-AI-ENGINEER-ONBOARDING.md — AI/LLM integration guide

## Learnings
<!-- Use `# <note>` shortcut to add entries here during sessions -->
```

---

# GLOBAL QUALITY RULES (apply to ALL generated documents)

1. **Accuracy over completeness** — if you cannot infer something with confidence, write `<!-- TODO: verify -->` rather than hallucinating
2. **LLM-navigability** — every document must start with a 2-sentence "What is this file?" comment block
3. **Cross-linking** — every generated document must link to at least 2 other generated documents
4. **Idempotent** — if run again on the same repo, re-running should update existing files rather than duplicate content
5. **No fictional commands** — every command block must be derived from actual files found in Phase 0; never invent syntax

---

# OUTPUT SUMMARY

After all files are written, output a completion report in this format:

```
## Documentation Generation Complete

| Document | Path | Lines | Status |
|----------|------|-------|--------|
| Master Index | docs/_base/00-INDEX.md | {n} | ✅ Created |
| Relationship Graph | docs/_base/01-RELATIONSHIPS.md | {n} | ✅ Created |
| Concept Guide | docs/_base/02-CONCEPT-GUIDE.md | {n} | ✅ Created |
| DevOps Onboarding | docs/_base/03-DEVOPS-ONBOARDING.md | {n} | ✅ Created |
| AI Engineer Onboarding | docs/_base/04-AI-ENGINEER-ONBOARDING.md | {n} | ✅ Created |
| Claude Memory | CLAUDE.md | {n} | ✅ Created / Updated |

### ⚠️ Items Requiring Human Review
- {any TODOs or uncertain inferences}

### 📎 Next Steps
1. Commit all docs/_base/ files to version control
2. Add CLAUDE.local.md to .gitignore if not already present
3. Run `/memory` to verify CLAUDE.md is loaded correctly
```
