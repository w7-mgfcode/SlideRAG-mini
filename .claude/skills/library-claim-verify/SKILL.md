---
name: library-claim-verify
description: Verify third-party library API claims (attribute existence, method signature, default-value behaviour) against the actual installed library before they land in a PRP or plan. Triggers on "verify this LangGraph API", "does langchain-chroma have parameter Y", "check the cited library claims", or whenever a PRP draft cites a specific attribute of LangChain, LangGraph, langchain-chroma, python-pptx, or the OpenAI SDK. Do NOT use for general programming questions or for verifying first-party (in-repo) APIs.
---

# library-claim-verify

## Why this skill exists

The brainstorm plan and any PRP built from it cite specific library surfaces from documentation: LangGraph `StateGraph` with named nodes, conditional edges, and a required `compile()`; `langchain-chroma` `Chroma(persist_directory=...)` surviving process restarts; LangChain text splitters with chunk size and overlap; `python-pptx` exposing text frames and table cells per slide. A citation that is wrong for the installed version costs real time out of an 8-hour budget and is cheapest to catch before implementation starts. This skill runs the claim against the installed package instead of trusting memory.

## When to use

- During PRP or plan authoring, before submitting to `prp-quality-agent`
- Whenever a PRP cites a third-party library attribute, method signature, or default-value behaviour
- During execution if an author realizes a citation may be wrong

## When NOT to use

- General programming questions (use the codebase + WebFetch directly)
- First-party APIs (use `Grep` + `Read` on the repo)
- Already-verified claims (one verification per library version in `uv.lock`)

## Inputs

A YAML block of claims:

```yaml
claims:
  - library: langgraph.graph
    object: StateGraph
    claim: "add_conditional_edges accepts a mapping from router return values to node names, and the graph must be compiled before invoke"
    verify: |
      from typing import TypedDict
      from langgraph.graph import StateGraph, START, END
      class S(TypedDict):
          evidence_status: str
      g = StateGraph(S)
      g.add_node("retrieve", lambda s: {"evidence_status": "insufficient"})
      g.add_node("no_evidence", lambda s: s)
      g.add_edge(START, "retrieve")
      g.add_conditional_edges("retrieve", lambda s: s["evidence_status"], {"sufficient": END, "insufficient": "no_evidence"})
      g.add_edge("no_evidence", END)
      app = g.compile()
      print(app.invoke({"evidence_status": ""}))
  - library: langchain_chroma
    object: Chroma
    claim: "accepts persist_directory and reopening the same directory returns the stored documents"
    verify: |
      import tempfile
      from langchain_chroma import Chroma
      from langchain_core.embeddings import FakeEmbeddings
      d = tempfile.mkdtemp()
      emb = FakeEmbeddings(size=8)
      Chroma(collection_name="t", embedding_function=emb, persist_directory=d).add_texts(["a"], ids=["id-1"])
      print(Chroma(collection_name="t", embedding_function=emb, persist_directory=d).get()["ids"])
  - library: pptx
    object: Presentation
    claim: "each slide exposes shapes with has_text_frame and has_table so text boxes and table cells can be extracted"
    verify: |
      from pptx import Presentation
      from pptx.util import Inches
      p = Presentation()
      s = p.slides.add_slide(p.slide_layouts[5])
      t = s.shapes.add_table(1, 1, Inches(1), Inches(1), Inches(2), Inches(1)).table
      t.cell(0, 0).text = "PRB 92%"
      print([(sh.has_text_frame, sh.has_table) for sh in s.shapes])
```

## Outputs

A Markdown table:

| Library | Object | Claim | Verification command | Result | Verdict |
|---------|--------|-------|----------------------|--------|---------|
| langgraph.graph | StateGraph | conditional edges + compile | `uv run python <tmp>` | `{'evidence_status': 'insufficient'}` | ✅ PASS |
| langchain_chroma | Chroma | persist_directory survives reopen | `uv run python <tmp>` | `['id-1']` | ✅ PASS |
| pptx | Presentation | has_text_frame / has_table on shapes | `uv run python <tmp>` | `[(True, False), (False, True)]` | ✅ PASS |

Plus a suggested PRP "Known Gotchas" block entry per failed row.

## Implementation outline

1. Parse the input YAML block.
2. For each claim:
   - Write the `verify` block to a temp file
   - Run `uv run python <temp>`
   - Capture stdout + return code
   - Compare result to the `claim` (or a parallel `expected_output` field)
3. Render the result table.
4. For failed rows, emit a "Known Gotchas" snippet the PRP author can paste verbatim.

## Cross-links

- Plan: `docs/.prepare/execution-plan.md` §§ 3–5 (storage, ingestion, QA), § 7 (verification). Capability snippets above do not replace the required fresh-process persistence check.
- Sibling: `prp-quality-agent` (this skill runs upstream of its Phase 4.5 library-claim check)
