# Create PRD

## Objective

Create a Product Requirements Document for a new feature or significant change.

## Input

- **Feature idea**: Description of the feature, problem, or opportunity

## Tools

- Project architecture/design documents (as referenced in AGENTS.md)
- Project roadmap (as referenced in AGENTS.md)
- User personas documentation (if available)

## Process

1. **Gather Context**
   - Review project architecture/design documents for relevant context
   - Check project roadmap for related or conflicting work
   - Review user personas documentation for user context
   - Identify similar features in the codebase

2. **Define Problem**
   - Who is affected? (reference personas)
   - What is the current pain point?
   - What happens if we don't solve this?

3. **Specify Goals**
   - Primary goal (main outcome)
   - Secondary goals (additional benefits)
   - Non-goals (explicitly out of scope)

4. **Design Solution**
   - High-level approach
   - Key design decisions with rationale
   - Alternatives considered and why rejected

5. **Detail User Experience**
   - API changes (endpoints, parameters, responses)
   - CLI changes (commands, flags)
   - Configuration changes
   - Migration path for existing users

6. **Plan Technical Implementation**
   - Architecture (components, data flow)
   - Dependencies (services, libraries)
   - Updates needed to project design documents

7. **Define Success Metrics**
   - Quantitative measures
   - Qualitative signals
   - Verification criteria

8. **Identify Risks**
   - What could go wrong?
   - Likelihood and impact
   - Mitigations

## Output Format

```markdown
# [Feature Name] PRD

**Author:** [Name]
**Status:** Draft
**Date:** [Date]

## Problem Statement
[Who is affected and what pain point we're solving]

## Goals
- **Primary:** [Main outcome]
- **Secondary:** [Additional benefits]
- **Non-goals:** [Out of scope]

## Proposed Solution
[High-level approach and key decisions]

## User Experience
### API Changes
[New/modified endpoints]

### CLI Changes
[New/modified commands]

### Configuration
[New config options]

## Technical Design
[Architecture, components, data flow]

## Success Metrics
[How we measure success]

## Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk] | Low/Med/High | Low/Med/High | [Mitigation] |

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]
```

## When to Write a PRD

**Write PRD:**
- Adding significant new functionality
- Making breaking changes to APIs
- Changing architectural patterns
- Work spans multiple milestones
- Multiple people need to coordinate

**Skip PRD:**
- Bug fixes with clear scope
- Small improvements within existing patterns
- Implementation details already in design doc

## Constraints

- **Aligned**: Must align with existing project architecture and design documents
- **Scoped**: Clear boundaries on what's included and excluded
- **Actionable**: Leads directly to implementable tasks
- **Concise**: PRDs that nobody reads don't help

## Error Handling

- If feature conflicts with existing design, propose design amendments first
- If requirements are unclear, list questions before completing PRD
- If scope is too large, recommend phasing the work
