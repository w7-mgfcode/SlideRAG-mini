# [PROJECT_NAME] — Claude Code Operating Index

<!-- CLAUDE.md template. Thin Claude-specific layer. Hard limit: 150 lines. -->
<!-- All shared content (stack, commands, conventions, safety, git flow) lives in -->
<!-- AGENTS.md — see templates/AGENTS.md. CLAUDE.md @imports it; never duplicate it here. -->

> **Read `@AGENTS.md` first.** It is the shared cross-tool brief — stack, setup, build/test
> commands, validation gates, architecture, conventions, safety, and git flow. This file adds
> only Claude-specific operating context on top; it does not repeat AGENTS.md content.

@AGENTS.md

## Deep-Dive References

<!-- Claude @import feature. List only docs that exist. K8s/CI-CD lines are conditional. -->
Claude pulls these in on demand — load only what the task touches.

- Developer guide & tech stack:  @docs/_base/DEV_GUIDE.md
- Architecture & boundaries:     @docs/_base/ARCHITECTURE.md
- API contracts & interfaces:    @docs/_base/API_CONTRACTS.md
- Operational runbooks:          @docs/_base/RUNBOOKS.md
- Security & compliance:         @docs/_base/SECURITY.md
- Rules & constraints:           @docs/_base/RULES.md
- Domain model & glossary:       @docs/_base/DOMAIN_MODEL.md
- Service & dependency map:      @docs/_base/REPO_MAP_INDEX.md
# K8s repos only (remove if not applicable):
# - Workload policy:             @docs/_base/WORKLOAD_POLICY.md
# - Platform SLOs:               @docs/_base/PLATFORM_SLO.md
# CI/CD repos only (remove if not applicable):
# - Pipeline contract:           @docs/_base/PIPELINE_CONTRACT.md

## Safety

<!-- A pointer, NOT a copy. The hard rules live in AGENTS.md § Safety. -->
Full constraint matrix: `docs/_base/RULES.md`. Hard rules and stop-and-ask gates: `@AGENTS.md`
§ Safety. When a change is ambiguous or hard to reverse, surface the concern before acting.

## Verification

<!-- 5 lines max. CLAUDE.md-specific checks; gate commands themselves live in AGENTS.md. -->
```bash
{the project's validation-gate one-liner}
wc -l CLAUDE.md          # must stay ≤ 150 lines
```

## Workflow

<!-- 8 lines max. Ordered steps for the canonical dev loop. -->
1. {Pick an issue / branch off the integration branch}
2. {Implement in the right module}
3. {Run the validation gates — see @AGENTS.md}
4. {Open PR; CI must be green; merge}

## Learnings

<!-- 3 lines max. Session-specific discoveries Claude should remember. -->
<!-- Update this section when you discover repo-specific gotchas. -->
