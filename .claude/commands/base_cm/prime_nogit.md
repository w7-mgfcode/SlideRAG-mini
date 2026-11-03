---
description: "Prime agent with codebase understanding (no git required)"
---

# Prime: Load Project Context (No Git)

## Objective

Build comprehensive understanding of the codebase by analyzing filesystem structure, documentation, configuration, and cross-service relationships. Works without git — uses filesystem tools exclusively.

## Process

### 1. Analyze Project Structure

Show directory structure (no git required):
On Linux, run: `tree -L 3 -I 'node_modules|__pycache__|.git|dist|build|vendor|storage'`

Discover all services by scanning for key markers:
- Use Glob to find: `**/composer.json`, `**/requirements.txt`, `**/package.json`
- Use Glob to find: `**/Dockerfile`, `**/docker-compose.yml`
- Use Glob to find: `**/.gitlab-ci.yml`
- Use Glob to find: `**/helm/*/Chart.yaml`, `**/helm/*/values.yaml`

### 2. Read Core Documentation

Priority order:
1. Root `CLAUDE.md` — project-wide rules and conventions
2. `docs/architecture.md` — service topology and patterns
3. `docs/api-contracts.md` — interfaces between services
4. `docs/runbooks.md` — operational procedures
5. `docs/security.md` — auth, secrets, compliance
6. Per-service `CLAUDE.md` files (scan with Glob: `*/CLAUDE.md`)
7. README files at project root and major directories

### 3. Identify Key Files

Based on the structure, identify and read:
- Main entry points per service (`*/app/`, `*/routes/`, `*/src/`)
- Core configuration files (`composer.json`, `pyproject.toml`, `package.json`)
- CI pipeline definitions (`.gitlab-ci.yml` per service)
- Helm charts and environment values (`helm/*/values*.yaml`)
- Docker configurations (`Dockerfile`, `docker-compose.yml`)
- Key model/schema definitions
- Shared CI templates (`gitlab-ci-templates/`)

### 4. Service Inventory & Dependency Map

**For each discovered service, extract:**
- Stack (PHP/Python/Node/Java) and version
- Framework (Laravel/Symfony/FastAPI/etc.)
- Database type and connection patterns
- Redis usage (cache/session/queue)
- Inter-service communication (HTTP calls, queue messages)
- External API dependencies

**Build the map by scanning:**
- `docker-compose.yml` files for service dependencies and networks
- `.env.example` files for connection strings and service URLs
- Helm `values*.yaml` for K8s service references
- PHP/Python source for HTTP client calls to other services

### 5. CI/CD Pipeline Analysis

**Scan pipeline configurations:**
- Which shared CI template each service includes
- Template version pins (check for `ref:` in include statements)
- Custom job overrides per service
- Environment promotion gates (dev/sit/uat/pet/prod)
- Build arguments and registry references

### 6. Cross-Service Consistency Audit

**Compare across all services:**
- Dockerfile patterns (multi-stage? base images? targets?)
- Helm chart structure (common chart dependency? values schema?)
- PHP/Python version alignment
- Shared package versions (check `composer.lock` / `requirements.txt`)
- Health check endpoints (grep for `/up`, `/health`, `/ping`)
- Missing documentation (services without CLAUDE.md or README)

### 7. Environment Configuration Landscape

**Scan all Helm values files:**
- Use Glob: `**/helm/*/values-*.yaml`
- Compare resource allocations across environments
- Identify services with missing environment values files
- Check for hardcoded values that should be secrets

### 8. Understand Current State

Since git is unavailable, assess state through:
- File modification timestamps: `find . -name '*.php' -o -name '*.py' -newer ./CLAUDE.md -not -path '*/vendor/*' | head -30`
- Look for TODO/FIXME markers: Grep for `TODO|FIXME|HACK|XXX` in source files
- Check for uncommitted artifacts: look for `.env` files (should not exist), temp files, debug configs
- Read any `CHANGELOG.md`, `ToDo.md`, or `BACKLOG.md` files

## Output Report

Provide a concise summary covering:

### Project Overview
- Purpose and type of platform
- Primary technologies and frameworks
- Number of services discovered and their team groupings

### Architecture
- Overall monorepo structure and organization
- Key architectural patterns (shared CI, common Helm chart, multi-target Docker)
- Service communication patterns (sync/async, gateway, direct)
- Data layer topology (per-service DB, shared Redis)

### Service Inventory

| Service | Stack | Framework | Team | CI Template | Has Helm | Has Dockerfile |
|---------|-------|-----------|------|-------------|----------|----------------|
| ... | ... | ... | ... | ... | ... | ... |

### Tech Stack
- Languages and versions (per service group)
- Frameworks and major libraries
- Build tools and package managers
- Testing frameworks
- Infrastructure tooling (Ansible, Helm, K8s)

### Cross-Cutting Concerns
- CI/CD pipeline template versions (aligned or drifted?)
- Base image versions across services
- Shared packages and their versions
- Health check endpoint consistency
- Documentation coverage (which services have/lack docs)

### Blast Radius Map
- Which changes affect single services (safe)
- Which changes affect all services (CI templates, common Helm chart)
- Which changes affect the cluster (Ansible, K8s platform)

### Core Principles
- Code style and conventions observed
- Documentation standards
- Testing approach
- Deployment and promotion model

### Gaps & Observations
- Services missing CI pipelines
- Services missing Helm charts or Dockerfiles
- Inconsistent patterns across services
- Missing or outdated documentation
- Potential security concerns (exposed .env, hardcoded secrets)

**Make this summary easy to scan - use bullet points, tables, and clear headers.**
