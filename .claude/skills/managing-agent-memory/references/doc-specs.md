# Reference Doc Specifications

Full section structure for each `docs/_base/` document.
Use these specs during Phase 4 generation.

---

## ARCHITECTURE.md

**Load trigger:** Architecture changes, service boundaries, blast radius assessment,
dependency reasoning, deployment sequencing.

### Section Structure

```markdown
# [PROJECT] Architecture
> Source: KB 05_, 06_, 08_ + services/ + stakeholder input
> Last generated: {date}

## System Boundaries

### What This Repo Owns
- {List of owned resources: VPC, cluster, IAM roles, platform services, etc.}

### What This Repo Depends On
| Dependency | Interface | Owner Team | Change Process |
|------------|-----------|-----------|---------------|
| {Dep} | {SSM param / Terraform remote state / API} | {Team} | {Process} |

### What Depends On This Repo
| Consumer | Depends On | Break Risk |
|----------|-----------|-----------|
| {Repo/service} | {What they consume} | CRITICAL/HIGH/MEDIUM/LOW |

## Resource Hierarchy
(Ascii tree: Org → Account → VPC → Cluster → Namespace → Workload)

## Component Overview
| Component | Language | Type | Repo/Path | Owner |
|-----------|---------|------|-----------|-------|
| {name} | {lang} | {API/Worker/DB/etc} | {location} | {team} |

## Communication Patterns
| Pattern | Used By | Protocol | Auth |
|---------|---------|---------|------|
| Sync HTTP | {services} | REST/gRPC | {mTLS/JWT/API key} |
| Async events | {services} | Kafka/SQS | {IAM/SASL} |

## Deployment Flow (Causal Chain)
(Step-by-step: PR → CI gate → artifact → staging → approval → prod → rollback trigger)

## Observability Stack
| Signal | Tool | Retention | Dashboard |
|--------|------|---------|----------|
| Metrics | {Prometheus} | {30d} | {Grafana link} |
| Traces | {Tempo} | {7d} | {Grafana link} |
| Logs | {Loki/CloudWatch} | {30d} | {link} |
```

---

## API_CONTRACTS.md

**Load trigger:** API changes, interface questions, contract review, new service integration.

### Section Structure

```markdown
# [PROJECT] API Contracts
> Source: interfaces/01_API_ROUTES_CATALOG.md + 02_EVENTS_JOBS_QUEUES_CATALOG.md

## HTTP / gRPC Endpoints
| Service | Method | Path | Auth | Request Schema | Response Schema |
|---------|--------|------|------|---------------|----------------|

## Async Events
| Topic/Queue | Producer | Consumers | Schema | Version | Delivery |
|-------------|---------|----------|--------|---------|---------|

## External Integrations
| Integration | Direction | Auth | Rate Limit | Fallback |
|------------|----------|------|-----------|---------|

## Schema Change Policy
- Breaking changes require version bump and migration period
- Consumers must be updated before producer changes deploy to prod
- Event schema registry: {location}
```

---

## RUNBOOKS.md

**Load trigger:** Incident response, operational procedures, on-call questions, debugging.

### Section Structure

```markdown
# [PROJECT] Runbooks
> Source: KB 09_END_TO_END_FLOWS.md + operational experience

## Common Incidents

### {Incident Type}
**Symptoms:** {what the alert/error looks like}
**Likely Causes:** {list}
**Diagnosis Steps:**
1. {command to run}
2. {what to look for}
**Resolution:**
1. {fix step}
2. {verify step}
**Escalation:** {if this doesn't work, contact...}

## Break-Glass Procedures

### Emergency Prod Access
1. {Step 1: open incident ticket}
2. {Step 2: authenticate with break-glass credentials}
...

## Secret Rotation
1. {Step 1}
...

## Rollback
1. {Step 1}
...
```

---

## SECURITY.md

**Load trigger:** Security review, IAM changes, external integrations, compliance questions.

### Section Structure

```markdown
# [PROJECT] Security
> Source: KB 10_RISKS_GAPS_RECOMMENDATIONS.md + interfaces/03_EXTERNAL_INTEGRATIONS_CATALOG.md

## IAM Model
| Role/SA | Permissions | Scope | Rotation |
|---------|------------|-------|---------|

## Secret Management
- Store: {AWS Secrets Manager / Vault / GCP Secret Manager}
- Injection: {ExternalSecrets Operator / Vault Agent / direct SDK}
- Naming: `{project}/{environment}/{service}/{key}`
- Rotation: {automated/manual} — {frequency}

## Network Security
- Ingress: {load balancer type, WAF, DDoS protection}
- Egress: {controlled / unrestricted}
- Service-to-service: {mTLS / network policy / open}

## External Integrations Security
| Integration | Auth Method | Data Sent | Compliance Note |
|------------|------------|----------|----------------|

## Scanning & Compliance
| Check | Tool | Frequency | Blocks Deploy? |
|-------|------|---------|--------------|
| Container CVE scan | Trivy | Every build | Yes (CRITICAL) |
| IaC scan | Checkov | Every PR | Yes (CRITICAL) |
| Dependency audit | {npm audit / go vuln} | Every PR | Yes (CRITICAL) |
| Secrets detection | {gitleaks} | Every commit | Yes |
```

---

## DEV_GUIDE.md (stub — human-maintained)

**Never overwrite if content exists beyond stub markers.**

```markdown
# [PROJECT] Developer Guide
> HUMAN-MAINTAINED — do not overwrite via generator.
> Fill in all {FILL IN} sections.

## What This Project Is
{FILL IN: 2 sentences}

## Tech Stack
{FILL IN: Languages, frameworks, infra, DB, CI/CD}

## Local Development Setup
{FILL IN: prerequisites + first-time setup commands}

## Running Tests
{FILL IN: test commands}

## Project Conventions
{FILL IN: naming, git workflow, code style}

## Why We Chose These Technologies
{FILL IN: key decisions with ADR links}

## Common Troubleshooting
{FILL IN: frequent issues and fixes}

## Contacts & Resources
{FILL IN: team Slack, on-call, key links}
```
