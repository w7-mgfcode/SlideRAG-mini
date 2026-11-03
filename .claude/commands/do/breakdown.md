# Task Breakdown

## Objective

Break down a feature, epic, or large initiative into smaller, atomic tasks suitable for individual implementation sessions.

## Input

- **Feature description**: What needs to be built or changed
- **Context**: Any relevant PRD, design doc section, or user requirements

## Tools

- `github-pm` skill for issue management
- Project design and roadmap documents (as referenced in AGENTS.md)

## Process

1. **Read Existing Design**
   - Check project design documents for relevant architecture decisions
   - Check project roadmap for existing related tasks
   - Review existing code patterns in relevant packages

2. **Identify Components**
   - List all distinct pieces of work required
   - Identify infrastructure/setup work vs feature work
   - Identify testing requirements

3. **Create Dependency Graph**
   - Determine which tasks block others
   - Order: infrastructure → core logic → integration → tests
   - Minimize parallel dependencies (avoid tasks needing multiple predecessors)

4. **Define Each Task**
   - **Title**: Short, action-oriented (e.g., "Add token batching to worker")
   - **Type**: feature | bug | task | chore
   - **Priority**: 0-4 (0=critical, 4=backlog)
   - **Acceptance criteria**: How we know it's done
   - **Dependencies**: What must complete first

5. **Output Tasks**
   - Provide dependency graph visualization
   - Create issues via `github-pm` skill
   - Set up dependencies via `github-pm` skill

## Output Format

```
### Dependency Graph

Epic: [Name]
├── T1: [Task name] (no deps)
├── T2: [Task name] (depends: T1)
├── T3: [Task name] (depends: T1, T2)
└── T4: [Task name] (depends: T3)

### Commands

gh issue create --title "[T1 name]" --label task
gh issue create --title "[T2 name]" --label task
# Set up dependencies and sub-issues via github-pm skill
...
```

## Constraints

- **Session-sized**: Each task should be completable in one session (a few hours max)
- **Atomic**: Each task has a single, clear deliverable
- **Testable**: Each task has verifiable completion criteria
- **Aligned**: Tasks must fit existing project design documents

## Guidelines

- If breakdown exceeds 10 tasks, consider splitting into multiple epics
- Include test tasks alongside implementation, not as afterthoughts
- Infrastructure and scaffolding tasks come first
- Don't create tasks for work already specified in the project roadmap

## Error Handling

- If requirements are ambiguous, list specific questions before creating tasks
- If the feature conflicts with project design documents, flag for design discussion first
