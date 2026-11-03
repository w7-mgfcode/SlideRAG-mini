# Question Pool — Phase 2 Logic

## Auto-Answered from KB (skip if mapping-repo-context KB present)

| # | Question | KB Source File | Detection Method |
|---|----------|---------------|-----------------|
| A1 | IaC tool? (Terraform / Pulumi / CloudFormation) | `03_COMPONENT_INVENTORY.md` | `*.tf` rows or `type: terraform` |
| A2 | Cloud provider? (AWS / GCP / Azure / multi) | `06_RUNTIME_ARCHITECTURE.md` | Provider detection in runtime doc |
| A3 | Container orchestration? (K8s / ECS / none) | `03_COMPONENT_INVENTORY.md` | `Dockerfile`, `Chart.yaml` rows |
| A4 | CI/CD platform? (GitHub Actions / Jenkins / GitLab) | `04_BUILD_AND_CICD.md` | Pipeline entrypoints |
| A5 | Environment topology? (dev/staging/prod / more) | `05_DEPLOYMENT_AND_ENVIRONMENTS.md` | Env sections |
| A6 | Key domain entity names? | `11_GLOSSARY_OPEN_QUESTIONS.md` | Glossary section |
| A7 | Manual approval gates in pipeline? | `04_BUILD_AND_CICD.md` | Stage gates with `manual` flag |

## Residual Questions (Always Ask — KB Cannot Answer These)

### R1 — Primary Audience
**Question:** Who is the primary audience for this CLAUDE.md?
- `platform` — Platform / infrastructure team
- `app` — Application developers consuming platform
- `both` — Both equally
- `external` — Open source contributors / external collaborators

**Why it matters:** Determines depth of Safety section and formality of Workflow section.
**Default:** `both` (balanced depth)

---

### R2 — Compliance Frameworks
**Question:** Which compliance frameworks are in scope?
- `pci` — PCI-DSS (payment card data)
- `soc2` — SOC 2 Type II
- `iso27001` — ISO 27001
- `hipaa` — HIPAA (health data)
- `none` — No formal compliance requirement

**Why it matters:** Shapes SECURITY.md scanning requirements and RULES.md hard constraints.
**Default:** `none` (no special compliance constraints added)

---

### R3 — System Boundary Ownership
**Question:** What does this repo OWN vs. CONSUME?

Format: "This repo owns: [list]. It consumes (but does not own): [list]."

Examples of "owns": VPC, EKS cluster, IAM roles, platform services, specific databases
Examples of "consumes": DNS zones managed by Networking team, shared VPCs, container registry

**Why it matters:** Drives ARCHITECTURE.md System Boundaries — cannot be inferred from code alone.
**Default:** Mark as `[UNVERIFIED - boundary not confirmed by owner]`

---

### R4 — Change Management Process
**Question:** How are production changes approved and applied?
- `atlantis` — Atlantis for Terraform, ArgoCD for K8s
- `github-environments` — GitHub Environments with required reviewers
- `manual` — Manual `terraform apply` by authorized engineers only
- `custom` — Custom process (describe it)

**Why it matters:** Populates RULES.md Change Authority Matrix and PIPELINE_CONTRACT.md gates.
**Default:** `github-environments` (safest common default)

---

### R5 — SLO Targets (K8s repos only)
**Question:** Are SLO targets agreed with stakeholders for production services?
- `yes-standard` — Use the standard targets from PLATFORM_SLO.md template (99.9% critical, 99.5% standard)
- `yes-custom` — Provide custom targets (enter values)
- `no-draft` — No agreed targets yet — generate draft based on service classes for stakeholder review

**Why it matters:** PLATFORM_SLO.md requires committed targets, not just technical limits.
**Default:** `yes-standard` (use template defaults, mark as `[PENDING STAKEHOLDER CONFIRMATION]`)

---

## UNKNOWN Surfacing Logic

From `11_GLOSSARY_OPEN_QUESTIONS.md`, extract items tagged as UNKNOWN or OPEN_QUESTION.

Surface the top 3 highest-impact UNKNOWNs as additional questions BEFORE R1–R5.
Rank by: data loss risk > security risk > blast radius > performance impact > other.

Format:
> "The KB flagged this as an open question: {UNKNOWN description}. Can you clarify?
> Default if skipped: {safe default or [UNVERIFIED]}."

## Total Question Cap

- UNKNOWNs from KB: max 3
- Residual questions: max 5 (R1–R5; R5 only for K8s repos)
- Hard cap: **8 questions per session**
- If cap would be exceeded, prioritize UNKNOWNs flagged as data-loss or security risk
