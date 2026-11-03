# Decision Log

| Field | Value |
|---|---|
| Document ID | PREP-04 |
| Title | Decision Log |
| Revision | r3 |
| Status | Current approval recorded; historical entries retain their original status |
| Owner | Orchestrator maintains entries; **the repository owner is the only person who can approve** |
| Last updated | 2026-11-03 |
| Evidence baseline | source-register.md r3 |
| Core-context revision used | core-context.md r3 |
| Dependencies | source-register.md r3, open-questions.md r3, execution-plan.md r1 |
| Supersedes | — |
| Approval record | § 4 below; Option C direction approved in conversation |
| Change summary | r1: initial decisions. r2: D-12 corrected; D-13…D-15 added after review. r3: verbatim owner approval and Option C decisions D-16…D-21 recorded; historical status preserved |

## 1. Status vocabulary

| Status | Meaning |
|---|---|
| `owner-stated` | The owner stated it as a parameter (mission § 0, SR-16). It is binding for this documentation phase but is **not** an "Approved by owner" record. |
| `in-force-by-rule` | A plan v1.0 decision that `product-vision.md:3` makes authoritative. It was never separately approved. |
| `proposed` | Proposed by an agent. It has no effect on the build until the owner approves it. |
| `approved` | Only when § 4 contains a dated "Approved by owner" line that the owner wrote personally, or that the owner explicitly asked to be recorded. |
| `superseded` | Replaced. The replacing ID is named. |

No ADR files are created (D-11). Every decision lives in this log. The 2026-11-03 owner approval below supersedes conflicting earlier proposals; it does not retroactively approve D-08…D-15 or the entire revised plan. The current governing plan is [execution-plan.md](execution-plan.md).

## 2. Process and governance decisions

| ID | Question | Options considered | Choice | Rationale | Evidence | Consequences | Owner | Status | Supersedes |
|---|---|---|---|---|---|---|---|---|---|
| D-01 | Does the documentation phase count against the 8 h build budget? | count / do not count | Does not count. The 8 h start at M1. | Owner decision | SR-16 § 0 | Recommendations are scored on build-time proportionality only | Owner | owner-stated | — |
| D-02 | How is approval recorded? | agent sign-off / owner line / conversation | An owner-written dated "Approved by owner" line in § 4, or the owner asks the orchestrator to record it | Prevents agents manufacturing approval | SR-16 § 0, § 2 | Nothing in this package is `approved` at r1 | Owner | owner-stated | — |
| D-03 | How are revisions tracked without commits? | wait for commits / manual labels | Per-document `revision` (r1, r2, …) plus the `docs-baseline-r1` label in README | No SHA can exist before the owner commits | SR-16 § 0; SR-21 | Revisions are honour-system labels (stated in SR register) | Owner | owner-stated | — |
| D-04 | Delegation topology | single author / Agent tool / Herdr sessions | Herdr: S1 requirements + architecture, S2 security + verification (concurrent), S3 critic after both. Max 3 sessions, max 2 concurrent. | Owner decision | SR-16 § 0, § 7 | Agent tool and Workflow are **not** substitutes | Owner | owner-stated | — |
| D-05 | Package shape | many files / consolidated | Ten files under `docs/.prepare/` + the archived original plan | Smallest sufficient set | SR-16 § 0 | Extra files need justification in readiness-report.md | Owner | owner-stated | — |
| D-06 | Git | none / `git init` only / full workflow | `git init -b main` once. No commit, tag, branch, or push. | Enables later tracking without creating history | SR-16 § 0; executed 2026-11-02 (SR-21) | Herdr worktrees unavailable (D-09) | Owner | owner-stated | — |
| D-07 | Plan v1.0 editorial amendments (Mermaid diagram, operator name neutralised) | keep pasted SVG / re-render; keep name / neutralise | Re-render + neutralise. Original archived byte-exact. | Readability; public repo must not name a real company | SR-13 "Decisions Made"; SR-02 | Mermaid edges are a reconstruction, not the author's wiring | Owner | owner-stated | — |
| D-08 | How to satisfy "S1 and S2 in parallel" and "never concurrent writes to the same authoritative file" when both feed the revised plan | (a) S2 writes into the revised plan after S1 (serial); (b) S2 writes a staging fragment that the orchestrator merges; (c) separate final documents | **(b)** S1 owns `brainstorm-plan-revised.md`. S2 writes `docs/.prepare/delegation/S2-security-verification.md`. S3 writes `docs/.prepare/delegation/S3-critic-review.md`. The orchestrator merges both. | Keeps parallelism and single-writer ownership. Preserves raw delegated output as provenance. | SR-16 § 0, § 7 | Two files beyond the ten-file map, justified in readiness-report.md | Orchestrator | proposed | — |
| D-09 | Use Herdr worktrees for isolation? | worktree per session / shared tree with disjoint write paths | Shared tree, disjoint write paths | `herdr worktree create` takes `--branch` and git needs a commit for a worktree. Branches and commits are forbidden (D-06). | SR-19 (`herdr worktree` usage); SR-21 | Isolation is by instruction plus orchestrator verification, not by filesystem | Orchestrator | proposed | — |
| D-10 | Session placement and permissions | sibling panes / new tabs; manual / acceptEdits / auto | One **new labelled tab per session** in workspace `w1`, agent kind `claude`, `--permission-mode auto`, named `s1-req-arch`, `s2-sec-verify`, `s3-critic` | Owner asked for logically named new tabs (overrides the skill's sibling-pane default). Auto mode avoids unattended permission stalls and keeps the classifier guard. | Owner chat request 2026-11-02; SR-19 | Sessions are attributable by tab label and agent name | Orchestrator | proposed | — |
| D-11 | Use separate ADR files? | ADR per decision / single log | Single log, no ADRs | No decision so far needs more than one table row | SR-16 § 4 | — | Orchestrator | proposed | — |
| D-12 | What counts as a "mandatory blocker"? | severity-based / milestone-gated | A recommendation is a mandatory blocker if, unresolved, it makes a load-bearing gate (**QG-06, QG-07**, per SR-05 L59) untestable or violates a `security-patterns.md` MUST, **before the milestone that implements it**. *r2 correction:* r1 also listed QG-03 and QG-08, which SR-05 L59 does not call load-bearing (S3 § 2.6). R-03 and R-05 remain blockers through the MUST prong. | Ties blocker status to evidence, not to score | SR-05 L57–59; SR-04 L1–5 | Blockers are listed per milestone in plan-review.md | Orchestrator | proposed | r1 wording |
| D-13 | Accept S3's structural review proposals? | accept all / accept score changes only (S3 § 4.3) / reject | **Accept all**: merge R-04 into R-03; split R-14 into R-14 (drift) + R-15 (commit preconditions); reclassify R-09 (M1) and R-10 (M4 / pre-provision) as mandatory under D-12's MUST prong; new category "owner precondition" for R-15; present ranks 8–13 as tiers; the six criterion score changes | Each change is backed by evidence S3 cites (double count R-03↔R-04; SP L49 and L73 MUSTs; python-pptx full-read evidence). The score-only control (S3 § 4.3) shows the top 5 is stable either way. | SR-36 §§ 2–4 | plan-review.md r2 §§ 6–7 carry the final ranks | Orchestrator | proposed | — |
| D-14 | How to resolve the S1↔S2 contradictions | pick by detail / pick by evidence and ownership / escalate all | Resolve C-01, C-03…C-17 on evidence and section ownership (S1 owns contracts and interfaces; S2 owns security spec and tests). **Escalate C-02** (malformed output) as OQ-23 because it changes a load-bearing table. | Mission § 8: resolve within authority when evidence-supported, escalate otherwise | SR-36 § 5.1; PREP-08 § 15.1 | PREP-08 r2 | Orchestrator | proposed | — |
| D-15 | Keep the raw S1 draft as a provenance file? | overwrite in place / keep a raw copy | Keep `delegation/S1-brainstorm-plan-revised.raw.md`, making three provenance files alongside the S2 and S3 raw outputs | S3 reviewed the raw S1 text. Keeping it lets the owner audit what changed at integration. | SR-34 | Three files beyond the ten-file map, justified in readiness-report.md | Orchestrator | proposed | extends D-08 |

## 3. Inherited plan decisions (v1.0)

These describe the inherited r2 baseline from SR-01, preserved for traceability. D-16…D-21 and execution-plan.md now govern where they differ (notably DATA_DIR, index lifecycle, calibration, and schedule).

| ID | Decision | Evidence | Status |
|---|---|---|---|
| P-01 | Python 3.12, FastAPI, Uvicorn, Jinja2, plain CSS | SR-01 L102–118 | in-force-by-rule (host has 3.14.4, see OQ-07) |
| P-02 | python-pptx extraction: text boxes and supported table cells | SR-01 L82 | in-force-by-rule |
| P-03 | Chunk within slide, ~1000 chars, 150 overlap | SR-01 L84 | in-force-by-rule |
| P-04 | OpenAI `text-embedding-3-small` + `gpt-4.1-mini`, configurable base URLs | SR-01 L110–135 | in-force-by-rule; availability unverified (OQ-08) |
| P-05 | langchain-chroma with `persist_directory` under `/data/chroma` | SR-01 L113, L134, L268–270 | in-force-by-rule |
| P-06 | LangGraph state `question, retrieved_docs, evidence_status, answer, sources`; top-5 retrieval | SR-01 L197–238 | in-force-by-rule; gate rule undefined (OQ-12) |
| P-07 | EC2 t3.small eu-central-1, Ubuntu 24.04, EBS gp3 host `/var/lib/sliderag` → `/data`, SSH tunnel, `unless-stopped` | SR-01 L249–293 | in-force-by-rule |
| P-08 | 10 MB upload cap, one worker, one upload at a time | SR-01 L80, L189, L416 | in-force-by-rule |

## 4. Owner approval record

> Only the repository owner writes here, or the orchestrator writes here when the owner explicitly says so in conversation and asks for it to be recorded. Format:
> `YYYY-MM-DD — Approved by owner — <decision or document ID(s)> — <optional note>`

2026-11-03 — Approved by owner — D-16…D-21 / Option C — Owner message: “APPROVE YOUR SUPERVIZED VISION”, approving the immediately preceding architectural review and recommended execution direction. Recorded by the assistant as the requested planning follow-through; the wording is preserved verbatim.

This is approval of the recommendation, not a claim that the owner separately reviewed every sentence subsequently written into EXEC-01. No previous review document or completed historical process is blanket-approved. The approval turn aligns planning/policy only; implementation, GitHub mutations, commits, publication, and deployment are not performed in this turn.

## 5. Approved Option C decisions (2026-11-03)

| ID | Decision | Consequence | Evidence / status |
|---|---|---|---|
| D-16 | Choose Option C: fixed-configuration MVP with explicit recovery; execution-plan.md is the governing plan | Original/revised plans remain historical; retain product, stack, synthetic demo, and QG-01…QG-09 | Current owner approval; approved direction |
| D-17 | Complete configuration identity, coordinated ingestion/retrieval, non-destructive degraded startup, explicit fresh-root rebuild | No automatic stale collection/migration machinery; preserve uncertain data | Approved recommendation; implementation unverified |
| D-18 | C1 citations, native structured output, separate calibration probes, explicit refusal/error distinction | Citation membership is provenance, not semantic proof; acceptance questions do not choose T | Approved recommendation; runtime calibration pending |
| D-19 | Python 3.12, explicit cosine, DATA_DIR-derived storage, plain dependency injection, bounded upload handling, safe deployment and focused verification | Routine implementation details are builder decisions within these contracts; no separate file-layout approval gate | Approved technical direction; compatibility/limits must be verified |
| D-20 | Use the proposed 480-minute timebox, with preparation/bootstrap/AWS provisioning accounted for separately | 60 + 150 + 105 + 75 implementation minutes, 30 workflow, 60 reserve; estimates are not guarantees; report variance rather than weaken gates | Approval of recommended accounting; actual durations unmeasured |
| D-21 | Preserve public GitHub/hierarchy preference; bundle work into outcome-sized issues/PRs; maintain a lean active documentation set | Historical process choices are not M1 blockers; archive originals; fix publication provenance before publishing | Current approval plus prior authorization recorded in github-bootstrap-mission.md; external execution not performed |

Remaining evidence obligations and optional choices are in [open-questions.md](open-questions.md). They must not be reported as completed merely because the direction is approved.
