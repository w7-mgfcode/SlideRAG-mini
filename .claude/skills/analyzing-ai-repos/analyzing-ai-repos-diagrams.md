# Analyzing AI Repos — Diagrams

## Logic: Four-Phase Pipeline

```mermaid
flowchart TD
    A[Input: Path or URL] --> B{URL?}
    B -->|Yes| C[git clone --depth 1]
    B -->|No| D[Read local path]
    C --> E[classify_repo.py]
    D --> E
    E --> F{Confidence OK?}
    F -->|Low| G[Ask user to confirm type]
    F -->|OK| H[build_tree.py]
    G --> H
    H --> I[Deep analysis loop]
    I --> J[Build pattern catalog]
    J --> K{--research flag?}
    K -->|skip| N[DOCUMENT phase]
    K -->|light| L[2-3 scoped queries]
    K -->|deep| M[5-8 scoped queries]
    L --> N
    M --> N
    N --> O{--incremental?}
    O -->|Yes| P[Copy current to .prev/]
    O -->|No| Q[Fresh generation]
    P --> R[Generate 5 output files]
    Q --> R
    R --> S[diff_analysis.py]
    S --> T[Validate outputs]
    T --> U[.kb/designs/repo-name/]
```

## Flows: ANALYZE Phase Detail

```mermaid
flowchart TD
    KF[key_files list] --> READ[Read each file]
    READ --> EXT{Extract}
    EXT --> IMP[Imports & deps]
    EXT --> SIG[Function signatures]
    EXT --> TOOL[Tool calls & MCP refs]
    EXT --> PROMPT[Prompt templates]
    EXT --> STATE[State patterns]
    EXT --> CFG[Config patterns]
    IMP & SIG & TOOL & PROMPT & STATE & CFG --> CAT[Pattern catalog]
    CAT --> DEP[Dependency graph]
    CAT --> FLOW[Logic flow map]
    DEP --> VALID{Valid Mermaid?}
    FLOW --> VALID
    VALID -->|Yes| DONE[Analysis complete]
    VALID -->|No| FIX[Fix diagram syntax]
    FIX --> VALID
```

## Flows: RESEARCH Phase Detail

```mermaid
sequenceDiagram
    participant S as Skill
    participant WS as WebSearch
    participant WF as WebFetch
    participant PC as Pattern Catalog

    S->>PC: Get detected patterns & frameworks
    PC-->>S: patterns[], frameworks[]
    loop For each pattern
        S->>S: Generate scoped query
        S->>WS: Search(query)
        WS-->>S: results[]
        S->>S: Filter by relevance
        alt Relevant result found
            S->>WF: Fetch(top_url)
            WF-->>S: content
            S->>S: Link finding to PAT_NNN
        else No relevant results
            S->>S: Log gap, continue
        end
    end
    S->>S: Cross-reference all findings
```

## Relationships: Output Document Dependencies

```mermaid
graph TD
    PC[Pattern Catalog] --> LM[logic-map.md]
    PC --> DG[diagrams.md]
    PC --> RN[research-notes.md]

    CL[classify_repo.py] --> OV[overview.md]
    BT[build_tree.py] --> OV

    LM --> CTX[context.md]
    DG --> CTX
    RN --> CTX
    OV --> CTX

    PREV[.prev/] --> DA[diff_analysis.py]
    DA --> |annotations| OV
    DA --> |annotations| LM
    DA --> |annotations| DG
    DA --> |annotations| RN
    DA --> |annotations| CTX
```

## Structure: Skill Directory Layout

```mermaid
graph TD
    ROOT[analyzing-ai-repos/] --> SKILL[SKILL.md]
    ROOT --> SCRIPTS[scripts/]
    ROOT --> REFS[references/]
    ROOT --> ASSETS[assets/]

    SCRIPTS --> CR[classify_repo.py]
    SCRIPTS --> BT[build_tree.py]
    SCRIPTS --> DA[diff_analysis.py]

    REFS --> RTG[repo-type-guide.md]
    REFS --> PCS[pattern-catalog-schema.md]
    REFS --> OFG[output-format-guide.md]

    ASSETS --> TMPL[templates/]
    TMPL --> T1[overview.txt]
    TMPL --> T2[logic_map.txt]
    TMPL --> T3[diagrams.txt]
    TMPL --> T4[research_notes.txt]
    TMPL --> T5[context.txt]
```

## Structure: Output Document Layout

```mermaid
graph TD
    KB[.kb/designs/] --> REPO[repo-name/]
    REPO --> OV[overview.md]
    REPO --> LM[logic-map.md]
    REPO --> DG[diagrams.md]
    REPO --> RN[research-notes.md]
    REPO --> CTX[context.md]
    REPO --> PREV[.prev/]
    PREV --> POV[overview.md]
    PREV --> PLM[logic-map.md]
    PREV --> PDG[diagrams.md]
    PREV --> PRN[research-notes.md]
    PREV --> PCTX[context.md]
```
