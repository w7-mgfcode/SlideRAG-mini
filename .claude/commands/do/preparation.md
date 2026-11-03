# Implementation Preparation

## Objective

Gather context and validate approach before starting implementation to avoid wasted effort.

## Input

- **Issue number**: The GitHub issue number to prepare for (e.g., `42`)

## Tools

- `github-pm` skill for issue details
- Project design and roadmap documents (as referenced in AGENTS.md)

## Process

1. **Load Task Context**
   - Read issue details: `gh issue view <number> --comments`
   - Read parent Epic or PRD if referenced
   - Note acceptance criteria and dependencies

2. **Review Design Documents**
   - Check project design documents for relevant architecture sections
   - Check project roadmap for related tasks
   - Note any design decisions that constrain implementation

3. **Explore Existing Code**
   - Find existing patterns this should follow
   - Identify files that will need modification
   - Check for existing tests covering related functionality
   - Note code conventions and styles used

4. **Identify Dependencies**
   - What existing code/APIs does this depend on?
   - Are there blocking issues? Check issue dependencies via `github-pm`
   - What external dependencies (if any) are needed?

5. **Validate Approach**
   - Does the design doc specify how this should work?
   - Are there multiple valid approaches? Which aligns best?
   - What edge cases need handling?
   - What could go wrong?

6. **Create Implementation Plan**
   - List files to modify (in order)
   - List new files to create (if any - prefer modifying existing)
   - List tests to add/update
   - Suggest quick verification test to validate approach early

## Output Format

```
### Context Summary
[Brief summary of what the task requires]

### Design Alignment
[Relevant sections from design.md, any constraints]

### Files to Modify
1. path/to/file1.py - [what changes]
2. path/to/file2.py - [what changes]

### Patterns to Follow
[Existing code patterns to match]

### Quick Verification
[A simple test to run early to validate the approach]

### Open Questions
[Any ambiguities to resolve before starting]
```

## Constraints

- **No Code Changes**: This phase is research only
- **Design First**: If design doc doesn't cover this, flag it before proceeding
- **Scope Validation**: If task seems too large, recommend splitting

## Error Handling

- If requirements are unclear, list specific questions and stop
- If approach conflicts with project design documents, flag for discussion
- If blocking dependencies exist, note them and check if task should be marked blocked
