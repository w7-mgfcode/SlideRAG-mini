# Preparing Skill Briefs — Diagrams

## Logic: Interview Phase Decision Gates

```mermaid
flowchart TD
    Start([User provides input]) --> InputType{Input type?}
    InputType -->|Pre-filled brief| Parse[Parse brief & validate]
    InputType -->|URL| Fetch[Fetch URL & extract signals]
    InputType -->|Text/keyword| Classify
    Parse --> BriefCheck{Complete?}
    BriefCheck -->|Yes| Review
    BriefCheck -->|Gaps found| GapInterview[Interview only missing sections]
    GapInterview --> Synthesize
    Fetch --> Classify[Classify domain & estimate tier]
    Classify --> TierCheck{Complexity tier?}

    TierCheck -->|Simple 1-3| Simple[Ask Sections 1-2 only]
    TierCheck -->|Moderate 4-6| Moderate[Ask Sections 1-4]
    TierCheck -->|Complex 7-10| Complex[Ask Sections 1-6]

    Simple --> Interview
    Moderate --> Interview
    Complex --> Interview

    Interview[Interview with role switching] --> TierUpgrade{Tier upgrade detected?}
    TierUpgrade -->|Yes| NotifyUser[Explain upgrade & ask confirmation]
    TierUpgrade -->|No| Continue[Continue interview]
    NotifyUser -->|Confirmed| ExpandScope[Add newly required sections]
    NotifyUser -->|Rejected| Continue
    ExpandScope --> Continue
    Continue --> Synthesize

    Synthesize[Assemble draft brief] --> Validate{Completeness check}
    Validate -->|Pass| Review[Present to user]
    Validate -->|Fail| FillGaps[Infer defaults or ask follow-ups]
    FillGaps --> Synthesize

    Review --> UserDecision{User response}
    UserDecision -->|Approve| Handoff[Format & hand off]
    UserDecision -->|Change| Refine[Integrate feedback]
    UserDecision -->|Max 3 rounds| Handoff
    Refine --> Review
```

## Flows: Full Pipeline Phase Transitions

```mermaid
stateDiagram-v2
    [*] --> Seed: User input received
    Seed --> FastPath: Input is pre-filled brief
    Seed --> URLFetch: Input contains URL
    Seed --> Interview: Text/keyword, domain classified
    FastPath --> Review: Brief is complete
    FastPath --> Interview: Brief has gaps (skip filled sections)
    URLFetch --> Interview: Extracted signals, pre-filled candidates
    Interview --> Interview: More sections to cover
    Interview --> TierUpgrade: Complexity signals exceed estimate
    TierUpgrade --> Interview: Tier adjusted, scope expanded
    Interview --> Synthesize: All required sections answered
    Synthesize --> Review: Draft assembled, completeness passed
    Synthesize --> Interview: Missing required fields
    Review --> Review: User requests changes (max 3 rounds)
    Review --> Handoff: User approves
    Handoff --> [*]: Brief delivered

    note right of Interview
        Role switches between:
        - Domain Analyst (S1, S2, S8)
        - Workflow Architect (S3-S6)
        - Safety Auditor (S7)
    end note

    note right of TierUpgrade
        Triggers: conditional routing,
        loop-back, state management,
        5+ phases, external APIs
    end note
```

## Relationships: Role-to-Section Mapping

```mermaid
flowchart LR
    subgraph Roles
        DA[Domain Analyst]
        WA[Workflow Architect]
        SA[Safety Auditor]
    end

    subgraph Sections
        S1[S1: Identity]
        S2[S2: Triggers]
        S3[S3: Workflow]
        S4[S4: Complexity]
        S5[S5: Tools]
        S6[S6: Outputs]
        S7[S7: Safety]
        S8[S8: References]
    end

    DA --> S1
    DA --> S2
    DA --> S8
    WA --> S3
    WA --> S4
    WA --> S5
    WA --> S6
    SA --> S7

    subgraph Scripts
        VB[validate_brief.py]
        AB[assemble_brief.py]
    end

    S1 & S2 & S3 & S4 & S5 & S6 & S7 & S8 --> AB
    AB --> VB
```

## Structure: Skill Directory Tree

```mermaid
flowchart TD
    Root[preparing-skill-briefs/] --> SKILL[SKILL.md]
    Root --> Scripts[scripts/]
    Root --> Refs[references/]
    Root --> Assets[assets/]

    Scripts --> VB[validate_brief.py]
    Scripts --> AB[assemble_brief.py]

    Refs --> IR[interviewer-roles.md]
    Refs --> FE[field-elicitation-guide.md]
    Refs --> CT[complexity-tier-rules.md]

    Assets --> Templates[templates/]
    Templates --> BB[blank_brief.txt]
    Templates --> EB[example_brief.txt]

    style SKILL fill:#e1f5fe
    style VB fill:#f3e5f5
    style AB fill:#f3e5f5
    style IR fill:#fff3e0
    style FE fill:#fff3e0
    style CT fill:#fff3e0
    style BB fill:#e8f5e9
    style EB fill:#e8f5e9
```
