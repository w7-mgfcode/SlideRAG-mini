# AGENTS.md — Template

> Universal agent brief for **{PROJECT}** — the shared, cross-tool source of truth read by any
> AI coding agent (Claude Code, Cursor, GitHub Copilot, Gemini CLI, Aider, Zed, …). Plain
> Markdown, no frontmatter. Keep it focused: every token loads on every request.

## Project Overview

{One short paragraph: what the project is, who it serves, its defining constraint.}

## Tech Stack

- **Backend** — {language + framework + key libs}
- **Frontend** — {framework + build tool}
- **Database** — {engine + extensions}
- **Package managers** — {python / js managers}
- **CI/CD** — {platform + release tooling}

## Setup

```bash
{exact clone-to-running commands}
```

## Build & Test Commands

Use these exact strings.

```bash
{unit test command}
{integration test command}
{frontend check command}
{e2e / demo command}
```

## Validation Gates

Run before every commit. {N} gate(s) gate merge in CI.

```bash
{lint / format / typecheck / test commands}
```

## Architecture & Conventions

- **{Module layout}** — {how code is organized; import boundaries}
- **Errors** — {error envelope convention}
- **Validation** — {boundary validation convention}
- **{Domain invariant}** — {load-bearing rule and its spec test}
- **Migrations** — {schema-change policy}

## Testing Requirements

- {When a new test is required.}
- {Unit vs integration split.}

## Safety

**Hard rules — never violate:**

- {secret handling}
- {injection / unsafe-call prohibitions}
- {validation-gate prohibitions}
- {migration / push prohibitions}

**Stop and ask before:**

- {irreversible or release-boundary actions}

## Git & PR Conventions

- **Branches** — {naming}
- **Commits** — {message format + issue-reference rule}
- **Flow** — {branch → PR → merge → release}

## Deep-Dive Docs

Load only what the current task touches.

- {Doc} — `{path}`
