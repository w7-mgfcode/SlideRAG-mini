# Repo Map Index
> LLM: Read this index first. Load individual docs ONLY when the current task touches
> that domain. Do NOT pre-load all docs. This index is auto-generated — do not edit
> manually; re-run the generating-claudemd skill to update it.
>
> Last updated: {DATE} | Generator: generating-claudemd skill | Docs: {N}

## System at a Glance

{2–4 sentence plain-language summary of what this system does, written for an
engineer joining the team.}

> Example: This system is a B2B e-commerce platform serving ~200 merchants. It consists
> of 14 services across 8 repos, owned by 3 platform teams. The core transactional path
> is: API Gateway → Orders → Payments → Inventory → Fulfillment. All services run on
> EKS, deployed via ArgoCD.

## Document Index

<!-- AUTO-GENERATED — do not edit manually -->
| File | What it answers | Load when... |
|------|-----------------|-------------|
| [00_README.md](../_kB/repo-map/00_README.md) | KB overview and completeness status | Checking KB quality or starting fresh |
| [01_WORKSPACE_MAP.md](../_kB/repo-map/01_WORKSPACE_MAP.md) | Repo boundaries, monorepo topology | Understanding overall repo structure |
| [02_REPO_TREE.md](../_kB/repo-map/02_REPO_TREE.md) | Top-level directory layout annotated | Navigating the codebase |
| [03_COMPONENT_INVENTORY.md](../_kB/repo-map/03_COMPONENT_INVENTORY.md) | Master component table (language, type, CI, K8s) | Tech stack questions, new component decisions |
| [04_BUILD_AND_CICD.md](../_kB/repo-map/04_BUILD_AND_CICD.md) | Pipeline stages, gates, build tooling | CI/CD changes, build system questions |
| [05_DEPLOYMENT_AND_ENVIRONMENTS.md](../_kB/repo-map/05_DEPLOYMENT_AND_ENVIRONMENTS.md) | Env layout, Helm/Kustomize, ArgoCD | Deployment questions, env-specific config |
| [06_RUNTIME_ARCHITECTURE.md](../_kB/repo-map/06_RUNTIME_ARCHITECTURE.md) | Communication patterns, auth, data, observability | Architecture changes, service boundaries |
| [07_OBSERVABILITY.md](../_kB/repo-map/07_OBSERVABILITY.md) | Metrics, traces, logs, dashboards | Alerting, monitoring, debugging questions |
| [08_DEPENDENCIES_AND_BLAST_RADIUS.md](../_kB/repo-map/08_DEPENDENCIES_AND_BLAST_RADIUS.md) | Dependency graph + Mermaid diagrams | Impact analysis, blast radius assessment |
| [09_END_TO_END_FLOWS.md](../_kB/repo-map/09_END_TO_END_FLOWS.md) | ≥5 flows with sequence diagrams | Understanding request lifecycle, debugging flows |
| [10_RISKS_GAPS_RECOMMENDATIONS.md](../_kB/repo-map/10_RISKS_GAPS_RECOMMENDATIONS.md) | Discovered risks and open items | Risk assessment, prioritization decisions |
| [11_GLOSSARY_OPEN_QUESTIONS.md](../_kB/repo-map/11_GLOSSARY_OPEN_QUESTIONS.md) | Domain terms and UNKNOWNs | Naming, domain model, open questions |
| [knowledge-graph.yaml](../_kB/repo-map/knowledge-graph.yaml) | Entity nodes, aggregate boundaries, edge types | Domain model reasoning, entity relationships |
| [interfaces/01_API_ROUTES_CATALOG.md](../_kB/repo-map/interfaces/01_API_ROUTES_CATALOG.md) | HTTP/gRPC endpoints | API changes, contract questions |
| [interfaces/02_EVENTS_JOBS_QUEUES_CATALOG.md](../_kB/repo-map/interfaces/02_EVENTS_JOBS_QUEUES_CATALOG.md) | Async events, jobs, queues | Async architecture, event-driven changes |
| [interfaces/03_EXTERNAL_INTEGRATIONS_CATALOG.md](../_kB/repo-map/interfaces/03_EXTERNAL_INTEGRATIONS_CATALOG.md) | Third-party integrations | External dependency questions, security review |
<!-- /AUTO-GENERATED -->

## Dependency Hotspots (LLM: high blast-radius targets — extra caution required)

| Service | Incoming Dependencies | Risk Level |
|---------|----------------------|-----------|
| {service} | {N} | CRITICAL |
| {service} | {N} | HIGH |
| {service} | {N} | MEDIUM |

## Tech Stack Snapshot

| Category | Technology | Status |
|----------|-----------|--------|
| Backend language | {e.g. Go 1.22} | Approved |
| Orchestration | {e.g. Kubernetes 1.29} | Approved |
| Message broker | {e.g. Kafka 3.6} | Approved |
| Primary DB | {e.g. PostgreSQL 15} | Approved |
| IaC | {e.g. Terraform 1.7} | Approved |
| CI/CD | {e.g. GitHub Actions + ArgoCD} | Approved |

## Index Update History (last 5 generations)

| Date | Change | Who |
|------|--------|-----|
| {DATE} | Initial generation | generating-claudemd skill |
