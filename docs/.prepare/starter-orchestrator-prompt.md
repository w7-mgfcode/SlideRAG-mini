Mission: Documentation-First Architecture and Orchestration for SlideRAG Mini

Act as the Principal Software Architect and Documentation Orchestrator for this repository. Your responsibility is to establish an evidence-grounded, revision-controlled documentation foundation before implementation begins.

You must:
1. Study and adapt the referenced AI-native SDLC playbook to this repository.
2. Establish the initial core context and documentation governance.
3. Perform a deep, critical review of the existing brainstorm plan.
4. Generate actionable recommendations.
5. Score, rank, and re-rank those recommendations using the transparent rubric below.
6. Use the Herdr skill to delegate substantial document writing to agent sessions.
7. Review, reconcile, and integrate their outputs into a coherent documentation baseline.
8. Stop at an explicit human approval gate before implementation.

You are the architect and orchestrator, not the primary author of every downstream document.

Do not write application code or begin implementation during this assignment.

0. Project-specific parameters (decided by the repository owner on 2026-11-02)

- Repository: the SlideRAG-mini repository root. It contains no application code yet. It holds .claude/ tooling (7 rules, 3 agents, 16 skills, 27 commands, one commit-format hook), three empty .agents/ history directories, docs/.prepare/brainstorm-plan.md, and HANDOFF.md.
- The project is an 8-hour AI Engineer portfolio build. This documentation phase does NOT count against those 8 hours; the 8 hours start at Milestone 1 of the plan. Score recommendations on build-time proportionality only.
- Existing governance lives in .claude/rules/ (product-vision, commit-format, branch-naming, versioning, security-patterns, test-requirements, output-formatting). product-vision.md currently states that docs/.prepare/brainstorm-plan.md is the source of truth and wins over the rules on conflict. Treat that as the current governance fact. Your revised plan is a proposal until the owner approves it; do not edit the rules to point at it. Propose any rule change separately in the readiness report.
- Human approver: the repository owner, the only developer. Approval is recorded ONLY when the owner personally writes a dated "Approved by owner" line into docs/.prepare/decision-log.md for the relevant decision, or tells you so in this conversation and asks you to record it. You never write that line on your own initiative.
- Git: there is no git repository. You MAY run exactly `git init -b main` once, so that revisions can be tracked. You may NOT commit, tag, push, or create branches. Until the owner commits, no SHA exists; use the revision scheme below.
- Revision scheme: every document carries a `revision` field (r1, r2, ...) in its metadata block. The preparation README records a baseline label `docs-baseline-r1` listing each document and its revision. Bump the baseline label only when a core document changes. State plainly in the source register that these are manual revisions, not immutable SHAs, and that a retrieval date is not a revision.
- Herdr: available in this environment (HERDR_ENV=1, binary at ~/.local/bin/herdr, skill at ~/.claude/skills/herdr/SKILL.md, verified 2026-11-02). You must still read that SKILL.md in full before invoking anything, and use only the commands and capabilities it documents.
- Delegation budget: at most 3 Herdr agent sessions, at most 2 running concurrently. Planned roles: (S1) requirements and architecture writer, (S2) security and verification writer, (S3) independent critic and rubric reviewer. S1 and S2 may run concurrently; S3 runs after both complete and must not be the sole reviewer of anything it authored.
- Package size: consolidated. Produce these files under docs/.prepare/ and no others unless justified in the readiness report:
  README.md (index, reading order, ownership, status, dependencies, approval workflow, next gate, baseline label)
  core-context.md
  source-register.md
  decision-log.md
  open-questions.md
  methodology-adaptation.md
  plan-review.md (deep review, findings register, recommendations with criterion-level scores, independent review and re-ranking table, strengths to preserve)
  brainstorm-plan-revised.md (the revised plan, separate from the original)
  delegation-manifest.md (delegation packets, session records, completion reports, actual outcomes)
  readiness-report.md (readiness checks, verdict, human approval checklist, proposed rule changes)
  This map covers all ten minimum deliverables. Do not split or add files to look more thorough.
- Plan preservation: docs/.prepare/brainstorm-plan.md is version 1.0 dated 2026-11-02 and was editorially amended the same day in two places only: the section 3 diagram was re-rendered from pasted SVG styling into a Mermaid block, and a real operator's name was replaced by neutral wording in section 9. The pre-amendment copy is at /tmp/claude-1000/-home-w7-loqker-w7-workspace-selfbase-w7-mgfcode-portfolio-SlideRAG-mini/18be5421-a5e7-4d43-8d05-93f59d89a098/scratchpad/brainstorm-plan.md.bak. Before anything else, copy it to docs/.prepare/archive/brainstorm-plan.v1.0-original.md and record both files in the source register. Never modify either copy again.
- Do not update CLAUDE.md, AGENTS.md, .claude/rules/, or any skill automatically. Do not modify HANDOFF.md. Do not create or modify files outside docs/.prepare/ and the git initialization, except the memory directory if you need to record session facts.

1. Inputs and sources

External methodology. Read and understand https://github.com/yibie/ai-native-sdlc-playbook/blob/main/book.md. Extract the principles relevant to this project, including intent-driven planning; requirements and design before implementation; explicit implementation planning; version-controlled artifacts and traceable decisions; shared repository context; skills as reusable institutional knowledge; scoped delegation and isolated agent sessions; verification and feedback loops; human accountability and approval gates. Adapt these principles to the repository rather than copying the playbook mechanically. Record which principles you adopt, how each changes the project workflow, which you defer or consider inapplicable, why, and the source revision or retrieval date available to you. Treat the playbook as a methodology source, not as evidence about the project itself. If the URL cannot be fetched, say so, record the attempt, and proceed on the principle list above marked as unverified against the source.

Primary review target. Read docs/.prepare/brainstorm-plan.md in full. Treat it as input to evaluate, not as an already approved specification.

Repository evidence. Inspect the .claude/rules/ files, the commit hook, the agent and skill definitions, HANDOFF.md, and the memory directory. There are no source files, dependency manifests, tests, deployment configuration, or decision records yet; say so rather than inferring them. Inspect only to understand and verify. Do not modify implementation files (none exist; do not create any).

Delegation mechanism. Locate and read the actual Herdr skill instructions before using it. Do not assume what Herdr means, invent commands, arguments, or capabilities, or claim to have delegated work unless agent sessions actually ran. If Herdr turns out to be unusable despite the verified availability above, report the exact blocker, complete only work that does not require that capability, and do not silently substitute another orchestration mechanism such as the Agent tool or a Workflow.

2. Operating rules

Evidence discipline. Separate every material statement into one of: verified fact, user-stated requirement, proposed decision, working assumption, open question, unresolved conflict. Support repository-specific findings with file paths and line ranges or section references. Support methodology claims with source sections. Never invent requirements, existing functionality, repository structure, performance measurements, security guarantees, stakeholder approval, agent execution results, or document completion status. When evidence is unavailable, mark the claim unverified and explain what would verify it.

Scope discipline. Do not expand the product scope merely to create a more impressive design. Distinguish required baseline, conditional work, optional improvement, and explicitly out of scope. Prefer the smallest sufficient documentation set. Respect the plan's scope lock and the product-vision rule's negative guardrails when judging recommendations; a recommendation that violates them must say so and justify itself as a correctness, security, or demonstration-blocking fix.

Change discipline. Preserve the original brainstorm plan. Produce the critique separately. Write the revised plan as a separate proposed artifact. Do not overwrite existing documents without checking their purpose and status. Do not commit, push, merge, or mark documents human-approved without authorization. Creating planning documents under docs/.prepare/ is permitted. Implementation remains prohibited.

Approval discipline. An agent can report that a document passed its review. An agent cannot manufacture human approval. Use exactly these states: draft, in-review, ready-for-human-review, approved. Only the recorded owner decision described in section 0 may move a document to approved.

3. Phase A, discovery and methodology adaptation

Before delegating: read the methodology; read the brainstorm plan; inspect the repository instructions and evidence; read the Herdr skill; identify existing documentation conventions and sources of truth; identify missing inputs and consequential uncertainties; define a proportional documentation scope.

Produce methodology-adaptation.md with, per principle: adopted principle, source reference, project-specific application, required artifact or workflow, verification method, limitations or prerequisites. Do not claim the methodology requires this exact document structure, rubric, or agent topology; those are project-specific choices made in section 0.

4. Phase B, establish the core documentation first

Before spawning writing sessions, author the core package yourself: README.md, core-context.md, source-register.md, decision-log.md, open-questions.md, methodology-adaptation.md. This is the one explicit exception to delegated authorship, because every delegated session depends on a consistent foundation.

README.md defines: purpose of the preparation workspace, canonical document index, reading order, artifact ownership, status of each artifact, dependencies between artifacts, approval workflow, next gate, and the baseline label.

core-context.md includes only high-value, project-relevant context: problem statement, intended outcomes, known users and stakeholders, scope and non-goals, verified current-state summary, confirmed constraints, architectural boundaries, important terminology, sources of truth, existing decisions and their status, working assumptions, major unresolved questions, acceptance and readiness principles, links to supporting evidence and specialist documents. Keep it concise enough to be the shared entry point for agents. Link to detail instead of duplicating it.

source-register.md records, per source: source ID, path or URL, source type, authority and intended use, revision or retrieval date (state which), relevant sections, known limitations. Include both copies of the brainstorm plan, the rules files, the hook, HANDOFF.md, the playbook, and any library documentation you consult.

decision-log.md records, per decision: decision ID, question, options considered, proposed or accepted choice, rationale, evidence, consequences, decision owner, status, superseded decision where applicable. Create separate ADRs only when complexity or importance justifies them; default to no ADRs.

open-questions.md records, per question: question ID, why it matters, affected documents or decisions, whether it blocks further work, required evidence or responsible owner, current status. Do not turn unanswered questions into implicit decisions. Carry forward the open questions in HANDOFF.md that remain unresolved.

Revision metadata on every core and downstream document: document ID, title, revision, status, owner, last updated, evidence baseline, core-context revision used, dependencies, supersedes if applicable, approval record if any, change summary. Use repository history for the full audit trail once it exists; do not copy history into every document.

Core baseline checkpoint. Before delegation verify that the core context reflects available evidence, that assumptions and uncertainties are visible, that no unresolved contradiction is disguised as a settled fact, that agents can identify the authoritative sources, and that the baseline has the label docs-baseline-r1. The baseline may remain draft. Do not label it approved because it is ready for agent use.

5. Phase C, deep critical review of the brainstorm plan

Evaluate docs/.prepare/brainstorm-plan.md against repository reality and the adapted methodology across these dimensions where applicable: problem clarity and intended outcomes; scope and non-goals; functional requirements; non-functional requirements; architectural consistency; data model and data lifecycle; interfaces and integrations; security, privacy, and trust boundaries; failure handling and resilience; testing and verifiability; deployment and rollback; operations and observability; dependencies and sequencing; feasibility and maintainability; decision traceability; agent handoffs and context sufficiency; unnecessary complexity; missing approvals or ownership. Mark irrelevant dimensions not applicable with a reason.

For each finding record: finding ID, title, severity, exact evidence reference (file and line range or section), what is missing, inconsistent, unsupported, or risky, why it matters, likely consequence, recommended correction, confidence and evidence limitations, linked recommendation IDs.

Severity: Critical is an evidenced issue that makes the approach unsafe, fundamentally invalid, or unable to achieve its core purpose. High is substantial risk, missing requirement, or major feasibility problem. Medium is meaningful ambiguity or weakness likely to cause rework. Low is a localized improvement with limited consequence. Separate issue severity from recommendation priority. Include strengths worth preserving. Do not produce criticism merely to increase the finding count.

6. Phase D, recommendations and defensible ranking

Create concrete, non-duplicative recommendations. For each record: recommendation ID, linked findings, proposed action, expected outcome, evidence, dependencies, effort estimate and its basis, proposed owner role, acceptance criteria, uncertainty, initial rank, final rank, explanation of any rank change.

Weighted rubric, each criterion scored 0 to 5:

| Criterion | Weight |
|---|---:|
| Alignment with confirmed intent and requirements | 25 |
| Reduction of evidenced risk or architectural failure | 25 |
| Ability to unblock dependent work | 20 |
| Contribution to verifiable implementation readiness | 20 |
| Proportionality of benefit to estimated build-time effort | 10 |

Priority score = sum over criteria of (weight x criterion score / 5), range 0 to 100. This is a structured decision aid, not a validated prediction.

Scoring anchors: 0 no demonstrated contribution or counterproductive; 1 small, indirect; 2 limited but relevant; 3 material, clearly explained; 4 strong, evidence-supported; 5 essential or exceptionally strong, supported by evidence. Every criterion score must have a short justification. Do not present precise-looking totals without the underlying reasoning.

Missing evidence: if a criterion cannot be responsibly scored, mark it unknown, explain what evidence is missing, do not silently score it zero, do not renormalize the remaining weights, report a possible score interval, and label the ordering provisional.

Confidence, reported separately from priority: High when direct evidence supports the recommendation and most estimates; Medium when partial evidence with stated assumptions; Low when substantial uncertainty or unverified premises. Do not bury confidence inside a multiplier.

Separate mandatory blockers, ranked improvements, and optional enhancements. An evidenced mandatory security, legal, or feasibility blocker cannot be deprioritized because its benefit-to-effort score is lower. Explain why each mandatory blocker is mandatory.

Initial ranking order: mandatory blocker status; weighted priority score within category; confidence and unresolved uncertainty; dependencies and practical sequencing. Keep priority rank distinct from execution order.

Independent review and re-ranking: the S3 critic session challenges findings and scores; checks for double-counted benefits, unsupported high scores, overlapping recommendations to merge, dependencies and sequencing, and whether reasonable scoring changes would alter the top choices. Then re-rank using corrected evidence. Produce a re-ranking table with recommendation ID, initial score and rank, revised score and rank, the evidence or assumption that changed, and an explanation. Do not force rank changes; if the review confirms the initial ordering, say so.

7. Phase E, delegate writing through Herdr

Use the verified Herdr workflow and the budget in section 0. Every session receives a delegation packet containing: task ID; role and objective; required core-context revision; exact source documents and revisions; scope and exclusions; assigned output paths; allowed write paths; required document structure; required evidence references; acceptance criteria; dependencies; questions to escalate; definition of done; required completion report. Require every agent to distinguish facts, assumptions, proposals, and open questions.

Shared-context rules: all sessions begin from docs-baseline-r1; agents do not independently redefine product intent; agents propose changes to core context rather than editing it; only you integrate changes into the core baseline; a material baseline change triggers an impact review of dependent outputs.

Concurrency rules: run S1 and S2 in parallel; run S3 after both complete; never allow concurrent writes to the same authoritative file; use isolated sessions or worktrees when the Herdr skill documents support for them; limit concurrency to what you can meaningfully review.

Agent completion report must include: session or task identifier; baseline revision used; documents created or changed; evidence consulted; decisions proposed; assumptions introduced; unresolved questions; validation performed; known limitations; completion or blocker status. If delegation fails, report the failure in delegation-manifest.md. Do not present a planned task as completed.

8. Phase F, integrate and validate the documentation

Review every delegated output before accepting it. Validate consistency with the core context and with repository evidence; agreement on terminology and system boundaries; no contradictory requirements or decisions; no invented functionality or guarantees; clear ownership and status; traceability from intent to requirements and from requirements to proposed verification; correct document dependencies; valid internal links; explicit handling of blockers; no unnecessary duplication.

Where agents disagree: identify the exact disagreement; compare evidence and assumptions; resolve it when supported by evidence and within your authority; otherwise record the alternatives and escalate; update all affected artifacts consistently. Do not resolve conflicts by silently selecting the most detailed response.

9. Deliverables

Exactly the ten files mapped in section 0, plus docs/.prepare/archive/brainstorm-plan.v1.0-original.md. A full implementation plan belongs inside brainstorm-plan-revised.md only if requirements and architecture are sufficiently stable; otherwise provide a conditional outline there and state the blockers. Do not update CLAUDE.md or shared policy skills; propose such changes in readiness-report.md.

10. Readiness and approval gate

Classify each readiness check as Pass, Fail, Unknown, or Not applicable with rationale: intent and scope are clear; requirements are sufficiently complete and testable; architecture is grounded in repository reality; major alternatives and trade-offs are documented; mandatory blockers are resolved or explicitly awaiting an authorized decision; recommendations have transparent scores and rationale; agent outputs have been reviewed and reconciled; dependencies and execution order are clear; verification and acceptance criteria exist; remaining questions have owners; the documentation baseline is revisioned and internally consistent.

Finish with exactly one of: NOT READY (documentation or decision blockers remain); READY FOR HUMAN REVIEW (the package is coherent but not approved); APPROVED FOR IMPLEMENTATION (only if the owner approval described in section 0 has actually been recorded). Do not begin implementation even if you assess the package as ready.

11. Final response format

Provide, concisely, with links to the artifacts rather than reproducing them: executive summary; sources inspected and access limitations; adapted methodology; core baseline and revision; most important findings; ranked recommendations and scoring rationale; re-ranking results; delegated sessions and actual outcomes; documents created, revised, or proposed; remaining blockers and decisions; readiness verdict; the exact human approval required next.

Execution order: discover; understand the methodology and repository; archive the original plan and initialize git; establish the revisioned core context; review the brainstorm plan; create and score recommendations; delegate S1 and S2, then S3, through Herdr; reconcile evidence and re-rank; integrate and validate documents; present the package for owner approval; stop before implementation.