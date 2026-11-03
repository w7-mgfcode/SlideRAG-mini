# Code Review

## Objective

Review code changes for correctness, design alignment, security, and code quality before merge.

## Input

- **PR number or diff**: The changes to review
- **Context**: What the change is supposed to accomplish (optional)

## Tools

- `gh pr view <number>` - Get PR details
- `gh pr diff <number>` - Get PR diff
- `git diff main..HEAD` - Local branch changes

## Process

1. **Understand Context**
   - Read the PR description or ticket
   - Understand what problem is being solved
   - Check related project design documents

2. **Review Correctness**
   - Does the code do what it's supposed to do?
   - Are there edge cases not handled?
   - Any logic errors or off-by-one errors?
   - Could this introduce race conditions?

3. **Check Design Alignment**
   - Does this align with project design documents?
   - Does it follow existing patterns in the codebase?
   - Is this the right location for this code?
   - Are there unnecessary abstractions?

4. **Security Audit**
   - Command injection (especially with user input)
   - SQL injection
   - XSS (if applicable)
   - Hardcoded secrets or credentials
   - Insufficient input validation at boundaries

5. **Verify Testing**
   - Are there tests for new functionality?
   - Are edge cases tested?
   - Is coverage appropriate (not excessive, not missing critical paths)?

6. **Assess Code Quality**
   - Is the code readable and self-explanatory?
   - Are names clear?
   - Is there unnecessary complexity?
   - Does it match surrounding code style?

7. **Project-Specific Checks**
   - Follows API client conventions defined in AGENTS.md?
   - Uses project task runner where applicable?
   - Uses project package manager for dependencies?
   - Follows project architectural patterns?

## Output Format

```
### Must Fix (Blocking)
[Issues that must be addressed before merge]

### Should Fix (Non-blocking)
[Improvements that should be made but don't block merge]

### Suggestions (Optional)
[Nice-to-have improvements]

### Questions
[Clarifications needed]

### Approved
[What was done well - brief]
```

## Review Checklist

- [ ] Code does what it claims
- [ ] No security vulnerabilities
- [ ] Tests added/updated
- [ ] Follows existing patterns
- [ ] No scope creep
- [ ] Lint and type checks pass

## Common Issues

**Over-engineering:**
- Configuration for things that don't need it
- Abstractions for single-use code
- "Future-proofing" without clear benefit

**Under-testing:**
- Missing error path tests
- Only happy path tested
- No integration tests for API changes

**Scope Creep:**
- Fixing unrelated issues
- Refactoring working code
- Adding unrequested features

## Constraints

- **Objective**: Focus on correctness and alignment, not style preferences
- **Constructive**: Provide actionable feedback with examples
- **Scoped**: Review only the changes, not the entire file history
