# Writing Session Handoffs — Diagrams

## Logic: Phase Flow with Validation Gates

```mermaid
flowchart TD
    A[Start: User requests handoff] --> B[Phase 1: Gather State]
    B --> B1{Git repo?}
    B1 -->|Yes| B2[Run 6 git commands in parallel]
    B1 -->|No| B3[Fallback: ls -la file listing]
    B2 --> B4[Scan conversation context]
    B3 --> B4
    B4 --> C[Phase 2: Extract Decisions & Dead Ends]
    C --> C1{Every decision has WHY?}
    C1 -->|No| C2[Re-read conversation]
    C2 --> C3{Still missing?}
    C3 -->|Yes| C4[Ask user]
    C3 -->|No| D
    C4 --> D[Phase 3: Compose Next Steps]
    C1 -->|Yes| D
    D --> D1{Next Step #1 passes actionable gate?}
    D1 -->|No: can rewrite| D2[Rewrite with specific file/command]
    D2 --> D1
    D1 -->|No: genuinely open-ended| D3[Ask user: What should next session do first?]
    D3 --> D
    D1 -->|Yes| E[Phase 4: Render & Save]
    E --> E1[Fill template]
    E1 --> E2{Post-render checklist passes?}
    E2 -->|No| E3[Fix and re-render]
    E3 --> E2
    E2 -->|Yes| E4{Existing HANDOFF.md?}
    E4 -->|No| E5[Write to workspace root]
    E4 -->|Yes| E6{User choice}
    E6 -->|Overwrite| E5
    E6 -->|Archive| E7[Move old to .handoffs/DATE.md]
    E7 --> E5
    E5 --> F[Report: Handoff written]
```

## Flow: Data Sources → Template Sections

```mermaid
flowchart LR
    subgraph Git State
        GS[git status --short]
        GD[git diff --stat]
        GN[git diff --name-only]
        GL[git log --oneline -5]
        GB[git branch --show-current]
        GR[git remote -v]
    end

    subgraph Conversation
        CC[Decisions + rationale]
        DE[Failed approaches]
        OQ[Unresolved items]
        GO[User-stated goals]
    end

    subgraph Template Sections
        WD[What Was Done]
        FC[Files Changed]
        DM[Decisions Made]
        DD[Dead Ends]
        OQS[Open Questions]
        NS[Next Steps]
        CTX[Context for Next Session]
        ST[Status]
    end

    GS --> WD
    GS --> FC
    GD --> FC
    GN --> FC
    GL --> CTX
    GB --> CTX
    GR --> CTX
    CC --> DM
    DE --> DD
    OQ --> OQS
    GO --> ST
    GO --> NS
```

## Relationships: Validation Gate Detail (Next Step #1)

```mermaid
flowchart TD
    NS1[Next Step #1 candidate]
    NS1 --> T1{Names a specific file, command, or test?}
    T1 -->|No| FAIL[FAIL — rewrite]
    T1 -->|Yes| T2{Describes expected outcome?}
    T2 -->|No| WARN[WEAK — add outcome]
    T2 -->|Yes| T3{Executable without reading other sections?}
    T3 -->|No| FAIL
    T3 -->|Yes| PASS[PASS — actionable]

    FAIL --> NS1
    WARN --> NS1

    style PASS fill:#c8e6c9,stroke:#2e7d32
    style FAIL fill:#ffcdd2,stroke:#c62828
    style WARN fill:#fff9c4,stroke:#f9a825
```

## Structure: Output File Layout

```mermaid
graph TD
    ROOT[writing-session-handoffs/] --> SKILL[SKILL.md]
    ROOT --> ASSETS[assets/]
    ROOT --> REF[references/]
    ROOT --> DIAG[writing-session-handoffs-diagrams.md]
    ASSETS --> TEMPLATES[templates/]
    TEMPLATES --> HANDOFF[HANDOFF.md — skeleton template]

    style SKILL fill:#e1f5fe,stroke:#0277bd
    style HANDOFF fill:#fff3e0,stroke:#ef6c00
    style DIAG fill:#f3e5f5,stroke:#7b1fa2
```
