# Example Output — fully worked

> This is a sample run of the skill against a realistic issue, drawn from a real-world product proposal (SIE M3, Req 4 Proj 2). It shows what the final 9-section package looks like when the pipeline runs end-to-end.

---

# Issue 488 — Execution Package

> Repository: `superlinked/sie-internal` · Issue: [#488](https://github.com/superlinked/sie-internal/pull/488) · Generated: 2026-04-28

---

## 1. Brief

- **What this issue is really about:** LightOnOCR adapter shipped in PR #488, but L4 throughput is ~14s/page while the vendor claims 5.71 pages/sec on H100 — roughly a 100× gap. Without closing or explaining this gap, "SIE has OCR" is undermined by "but it's 100× slower than alternatives."
- **Type:** performance investigation + remediation
- **Why it matters now:** OCR is a marquee Req 4 commitment in M3 — competitive throughput is the thing that makes OCR a reason to pick SIE rather than just a checkbox feature.

## 2. Source of Truth

Authoritative:

- `product/milestone3-proposal.md` — Req 4 Proj 2 ("Close the LightOnOCR perf gap")
- `product/design.md` — Section 3.3 (cost-based batching), Section 4.2 (decoder model batching gap)
- PR [#488](https://github.com/superlinked/sie-internal/pull/488) discussion — vLLM as perf target source raised
- Issue [#33](https://github.com/superlinked/sie-internal/issues/33) — decoder model OOM batching issue (open)

Supporting context:

- LightOnOCR vendor model card (claimed 5.71 pages/sec on H100)
- `packages/sie_bench/configs/eval-matrix-m2.yaml` — current perf eval matrix

Not source-of-truth (mentioned but not actionable here):

- Future M4 generative-worker rewrite ideas

## 3. Issue Context

| Field | Value |
|---|---|
| State | open |
| Milestone | M3 |
| Assignees | @ShaiShmuel |
| Labels | `perf`, `ocr`, `m3`, `req4` |
| Project / Board | M3 Delivery |
| Parent / Epic | M3 Req 4 (OCR is a reason to pick SIE) |
| Linked PRs | #488 (merged, adapter landed), #519 (open, olmOCR-bench) |
| Referenced issues | #33 (decoder OOM), #541 (shared cluster cache — adjacent) |
| Created / Updated | 2026-04-09 / 2026-04-13 |

**Sibling open issues from same assignees:**

- Req 4 Proj 1 — Add GLM-OCR adapter (#— TBD, planning)
- Req 4 Proj 3 — Evaluate PaddleOCR-VL-0.9B
- Req 4 Proj 5 — Add OCR quality benchmarks (OmniDocBench harness)

## 4. Risks / Blockers / Dependencies

**Risks:**

- Architectural cause (H100 vs L4 compute/memory) may mean L4 will never approach H100 throughput; outcome would be "document the gap" rather than "close the gap"
- Investigation could uncover that LightOnOCR specifically needs vLLM-backed worker — opens M4-sized work
- Decoder model batching bug (#33) likely contributes; fixing batching alone may not fully close the gap

**Blockers:**

- ⚠️ Soft: #33 (decoder OOM batching) needs to be either fixed or proven irrelevant before throughput numbers are trustworthy

**Dependencies:**

- **Upstream:** none hard — investigation can start
- **Downstream:** Req 4 Proj 9 (OCR showcase) needs trustworthy throughput numbers to demo realistically
- **Sequencing:** must precede Req 4 Proj 5 (benchmarks) so benchmarks measure a tuned configuration, not the unknown baseline

## 5. Role-Relevant Scope

> Framed for: **engineering lead** (assignee will implement, but the framing is sequencing + decision-quality, not file paths)

**In scope:**

- Profile LightOnOCR forward pass on L4 to identify bottleneck (compute, memory, scheduler, decode loop)
- Test batching-fix hypothesis from #33 — does decoder-aware cost estimation help?
- Decide whether vLLM-backed worker path is needed, and document the decision
- Publish a tracked perf measurement on L4 before and after any changes
- Update PR #488 thread or post a follow-up issue with the investigation outcome

**Out of scope (explicit):**

- Implementing a vLLM-backed worker (that's M4 if recommended)
- Adding new OCR models (Req 4 Proj 1, 3, 5)
- Building the OCR showcase (Req 4 Proj 9)
- Fixing #33 fully — only the part that affects this measurement

**Minimum MVP:**

- A profiling report saying "the gap is X% architectural / Y% scheduling / Z% runtime" with evidence
- A tuned L4 configuration with measured throughput improvement OR a written decision that no L4 fix is achievable
- Required proof: tracked measurement file under `benchmarks/{TASK}/lighton-ocr/performance_L4_b1_c16/` matching the new number

**Pipeline:**

```
profile L4 baseline → identify bottleneck → test batching hypothesis (#33) →
test runtime hypothesis (vLLM target) → write decision → publish measurement →
post follow-up
```

**Not yet decided:**

- Whether SIE adds vLLM as a perf target source in `sie-bench` for this investigation only or as a long-term integration

**Intentionally deferred:**

- Productionizing a vLLM-backed worker (M4 candidate, see Appendix D)

## 6. Research / Recommendation / Rerank

**Candidate directions considered:**

| ID | Description | Origin |
|---|---|---|
| A | Profile-first: instrument the L4 forward pass, identify bottleneck before changing anything | issue body, eng best practice |
| B | Batching-fix-first: assume #33 is the cause, fix decoder cost estimation, re-measure | PR #488 discussion, design.md §4.2 |
| C | vLLM-runtime-first: stand up a vLLM perf target in sie-bench and compare directly | PR #488 discussion |
| D | Document-and-defer: declare H100 vs L4 architectural, defer to M4 | conservative fallback |

**Rerank** (using `score_directions.py`):

| Rank | ID | Name | Score | Value | Risk | Ready | DepLoad | Validate | Rollback | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | Profile-first | 4.43 | 5 | 2 | 5 | 1 | 4 | 5 | 5 |
| 2 | B | Batching-fix-first | 3.71 | 4 | 3 | 4 | 2 | 4 | 4 | 4 |
| 3 | C | vLLM-runtime-first | 3.43 | 4 | 4 | 3 | 3 | 3 | 3 | 3 |
| 4 | D | Document-and-defer | 2.86 | 2 | 1 | 5 | 1 | 5 | 5 | 2 |

**Recommended path:** **A — profile first**, with a strong feed-in to either B or C depending on what profiling reveals.

**Why:** Highest evidence strength and lowest dependency load. B and C both jump to a fix without knowing whether it's the right fix; D forfeits the M3 commitment without justification. A also produces a profiling report which is itself a deliverable other Req 4 work can use.

## 7. Critic Findings

- [Section 2] ✅ Pass — every claim traces to issue body, PR #488 discussion, or design.md
- [Section 3] ⚠️ Subtask 3 in original draft included "evaluate vLLM worker rewrite" — that's M4. Reduced to "evaluate vLLM as a perf-target source only."
- [Section 5] ✅ Pass — out-of-scope is specific and non-empty
- [Section 7] ⚠️ Original draft had 4 weeks of work; tightened to 1.5 weeks once profile-first sequencing locked in

**Revisions applied:** Subtask 3 scope tightened (vLLM target ≠ vLLM worker). Total estimated effort reduced from "3-4 weeks" to "1.5-2 weeks" by sequencing on profiling outcome.

## 8. Proposed 5 Subtasks

### Subtask 1 — Profile LightOnOCR forward pass on L4 and locate the bottleneck

- **Purpose:** Establish whether the gap is compute, memory, scheduling, or runtime so subsequent work targets the right thing.
- **Scope:**
  - Run `nvprof` / `nsys` on a representative LightOnOCR inference on L4
  - Capture: time-per-page breakdown (preprocess / forward / decode / postprocess)
  - Capture: GPU utilization, memory pressure, batch-size behavior
  - Compare against the same trace pattern on H100 if available
- **Out of scope:** any code change to fix the gap; new model adapters
- **Dependencies:** none — can start immediately
- **Risks / blockers:** H100 access for comparison — if unavailable, reason from L4 metrics alone (acceptable, just less conclusive)
- **Acceptance criteria:**
  - Profiling report committed under `benchmarks/lighton-ocr/profile-l4.md`
  - Report ranks the top 3 contributors to the 100× gap
  - Numbers are reproducible (script committed)
- **Suggested owner:** @ShaiShmuel
- **Estimated effort:** 2 days
- **Why it matters now:** All other subtasks depend on knowing where the gap is.

### Subtask 2 — Validate or rule out decoder-batching hypothesis (#33)

- **Purpose:** Test whether SIE's static cost-based batcher (which costs decoder models at 1 per image) is starving the GPU on LightOnOCR specifically.
- **Scope:**
  - Implement minimal pessimistic cost estimation using `max_output_tokens` (per #33)
  - Run perf eval against LightOnOCR with old vs new batcher
  - Capture before/after throughput on L4 with batch sizes [1, 4, 8, 16]
- **Out of scope:** full #33 fix for all decoder models; refactoring the batcher
- **Dependencies:** Subtask 1 (informs whether this is the right thing to test)
- **Risks / blockers:** if profiling rules out scheduling as the bottleneck, drop this subtask and keep effort for Subtask 3
- **Acceptance criteria:**
  - Measurement file at `benchmarks/lighton-ocr/performance_L4_b1_c16/` updated
  - Written conclusion: batching is/isn't a contributor, with %
- **Suggested owner:** @ShaiShmuel
- **Estimated effort:** 1.5 days
- **Why it matters now:** Cheapest possible fix — must be tried before considering runtime changes.

### Subtask 3 — Add vLLM as a perf-target source in `sie-bench` and benchmark LightOnOCR on it

- **Purpose:** Establish a runtime baseline — does vLLM-backed inference recover the H100 numbers (or the proportional L4 equivalent)?
- **Scope:**
  - Wire a vLLM source into `packages/sie_bench/src/sie_bench/sources/`
  - Run LightOnOCR on vLLM with the same prompts / images / batch sizes used in Subtask 1
  - Document delta: SIE-on-PyTorch vs vLLM, on L4
- **Out of scope:** building a vLLM-backed SIE worker; promoting vLLM to a default source; multi-model vLLM evaluation
- **Dependencies:** Subtask 1
- **Risks / blockers:** vLLM dependency conflicts with current bundles — may need the new `transformers5` bundle or a vLLM-specific bundle
- **Acceptance criteria:**
  - vLLM source merged into sie-bench
  - Comparative measurement file committed
  - Recommendation written: "M4 should / should not pursue vLLM-backed worker"
- **Suggested owner:** @ShaiShmuel
- **Estimated effort:** 2 days
- **Why it matters now:** Second-cheapest hypothesis; if true, informs M4 direction at low cost.

### Subtask 4 — Write the decision document and post follow-up to PR #488

- **Purpose:** Close the loop on the investigation: what's the gap, what fixed it, what didn't, what's the M4 recommendation.
- **Scope:**
  - Write `docs/perf/lighton-ocr-l4-investigation.md` summarizing Subtasks 1-3
  - Post a comment on PR #488 with a link to the decision doc
  - Update Req 4 Proj 2 status in the M3 proposal
- **Out of scope:** implementing whatever the M4 recommendation is
- **Dependencies:** Subtasks 1, 2, 3
- **Risks / blockers:** none — pure write-up
- **Acceptance criteria:**
  - Decision doc merged
  - PR #488 has a follow-up comment with the link
  - M3 proposal updated
- **Suggested owner:** @ShaiShmuel
- **Estimated effort:** half-day
- **Why it matters now:** Without this, the investigation produces no durable artifact and M4 planning has nothing to consume.

### Subtask 5 — Update OCR documentation in sie-web with realistic perf expectations

- **Purpose:** Customers evaluating SIE for OCR see honest numbers, not vendor-claim aspirations.
- **Scope:**
  - Update `apps/site/src/content/docs/docs/extract/vision.mdx` LightOnOCR section
  - Add measured pages-per-second on L4 (post-Subtask 2 numbers)
  - Add a sentence on H100 expectations and how to scale up if needed
- **Out of scope:** other OCR model docs (Req 4 Proj 8 covers those)
- **Dependencies:** Subtask 4 (numbers must be settled before publishing)
- **Risks / blockers:** none
- **Acceptance criteria:**
  - Docs PR merged in sie-web
  - Numbers match the committed measurement file
- **Suggested owner:** @ShaiShmuel or @fm1320 (DevRel)
- **Estimated effort:** half-day
- **Why it matters now:** Closes the customer-facing half of "OCR is a reason to pick SIE."

**Sequencing summary:**

```
Subtask 1 (profile) ─┬─► Subtask 2 (batching) ─┐
                     │                          ├─► Subtask 4 (decision) ──► Subtask 5 (docs)
                     └─► Subtask 3 (vLLM)  ─────┘
```

## 9. Final Recommendation

- **What should happen next:** Start Subtask 1 immediately. Block on profiling output before launching 2 or 3.
- **What should be reviewed first:** The profiling report from Subtask 1 — it gates the whole investigation.
- **What must NOT be overbuilt:** Don't let this slip into a vLLM-worker rewrite. That's M4. Stay inside investigation + lightweight fixes + documentation.

---

**Ready for your review.** I can edit, reorder, drop, or merge any subtask. Once you approve, I can:

- Create them as GitHub sub-issues linked to PR #488 / Req 4 Proj 2
- Post a summary comment on PR #488
- Hand them to the M3 Delivery board

Your call. **No GitHub write actions taken yet.**
