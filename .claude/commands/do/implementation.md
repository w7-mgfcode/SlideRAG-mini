# Execute Task

## Objective

Implement a single, atomic task defined in a GitHub issue, ensuring code quality and verification before completion.

## Input

- **Issue number**: The GitHub issue number to execute (e.g., `42`)

## Tools

- Project task runner as defined in AGENTS.md
- `github-pm` skill for issue management
- API client as defined in AGENTS.md

## Process

1. **Claim Task**
   - Read issue details: `gh issue view <number> --comments`
   - Move to In Progress on the project board via `github-pm`

2. **Context Loading**
   - Read the parent Epic or PRD if referenced
   - Review project design documents for relevant sections
   - Explore relevant source code
   - Identify patterns to follow

3. **Implementation**
   - **Write Test**: Create a failing test that validates the requirement
   - **Implement**: Write minimal code to satisfy requirements and pass the test
   - **Refactor**: Clean up while keeping tests passing

4. **Verification**
   - Run quality gates as defined in the project's AGENTS.md (lint, typecheck, test)
   - Manual verification if applicable

5. **Completion**
   - If verification fails, fix issues and repeat Step 4
   - If verification passes:
     - Update issue with summary of changes
     - Close issue: `gh issue close <number> --reason completed --comment "Completed: [summary]"`

## Constraints

- **Scope**: Focus ONLY on the specified ticket. Do not implement extra features.
- **Minimal**: Write the minimum code necessary. Avoid abstractions for single-use cases.
- **Patterns**: Follow existing code patterns. Don't introduce new conventions.
- **Dependencies**: Use the project's package manager as defined in AGENTS.md.
- **API calls**: Follow API client conventions defined in AGENTS.md.
- **Security**: No command injection, XSS, SQL injection, or hardcoded secrets.

## Anti-Patterns

- Adding docstrings/comments to code you didn't change
- Creating helpers or utilities for one-time operations
- "Future-proofing" with unnecessary configuration
- Fixing unrelated code you notice
- Skipping tests because "it's simple"

## Error Handling

- If blocked (missing dependency, unclear requirement):
  - Add comment: `gh issue comment <number> --body "Blocker: [description]"`
  - Add blocked label: `gh issue edit <number> --add-label blocked`
  - Stop and report the blocker

- If task is too large:
  - Stop implementation
  - Recommend splitting into smaller tickets
  - Do not proceed with partial implementation
