# Herdr Coordination Reference

Read this when preparing a delegation packet or handling an ambiguous result,
restart, or cleanup. The [project rule](../rules/herdr-orchestration.md) owns the
contract. The installed Herdr skill and matching CLI help own command syntax.
This reference is outside `rules/` to avoid loading detailed examples into every
Claude session. It does not authorize a mission, integrations or external writes.

## Assignment and report shapes

Use these fields in an English terminal prompt; fill only fields relevant to
the task. The orchestrator supplies the packet rather than asking a worker to
guess its scope. Do not require workers to create report files by default.

```text
Task: <unique ID and bounded outcome>
Report to: <assigning orchestrator's current identity>
Working directory and baseline: <absolute cwd, commit, relevant local inputs>
Read: <AGENTS.md, governing sections, task-specific rules and accepted inputs>
Procedure: <command/skill file or none; native alias or explicit file-read mode>
Bindings and adaptations: <named inputs, allowed plan sections, output, gates>
Ownership: <write paths; any ports, containers, temporary data roots>
Allowed actions and exclusions: <specific authority, integration owner>
Dependencies: <accepted artifact/version or agreed interface>
Acceptance: <observable result and applicable verification>
Checkpoint: <when to report progress or a blocker>
Return a terminal completion report matching this task and baseline.
```

```text
Task / worker / cwd / baseline:
Status: DONE or BLOCKED
Result location: final commit, or exact changed paths/diff/artifact
Procedure used: source, invocation mode and any deviations from the packet
Changed files and runtime resources still in use:
Checks: command, actual outcome, evidence location and revision tested
Unverified claims, assumptions and remaining limitations:
Blocker or decision needed, if any:
Recommended next action:
```

The lead records acceptance only after checking the result. An internal task
split does not change the repository's outcome-sized issue/branch/PR convention.
Keep progress in an existing session/work artifact; a new manifest is optional,
not a gate. Budget concurrency for what the lead can inspect and the host can
run, rather than filling every available pane.

## Repository command routing

Static inspection: 2026-11-15. These are candidate procedures, not a mandatory
pipeline or proof of runtime availability. Paths in the table are relative to
`.claude/commands/`. The lead reads the selected file, checks prerequisites and
binds its scope before assigning it. Use the smallest suitable subset; the
installed Herdr skill controls delegation, while these files guide the work.

| Assignment | Procedure and expected Claude alias | Required bounds or adaptation |
|---|---|---|
| Understand the repository | [core_piv_loop/prime.md](../commands/core_piv_loop/prime.md), `/core_piv_loop:prime` | Use current instructions/EXEC-01; tolerate absent application files. Its injected Git reads use the session cwd. Read-only alternatives can replace an unavailable `tree`; do not install it implicitly. |
| Implement an approved task | [core_piv_loop/execute.md](../commands/core_piv_loop/execute.md), `/core_piv_loop:execute` | Bind the plan path plus exact milestone/task sections. For M1, reading all of EXEC-01 does not authorize M2–M4. Map the generic step-list assumption to the assigned acceptance criteria; do not invent a new plan. Treat its `/commit` mention as readiness only, not an available or authorized commit action. |
| Review a specific PR/diff | [do/review.md](../commands/do/review.md), `/do:review` | Supply the exact PR/diff and baseline. Findings are technical review, not owner approval. Apply actual repository checks; no invented type-check gate or automatic GitHub posting. |
| Review local changes with an artifact | [validation/code-review.md](../commands/validation/code-review.md), `/validation:code-review` | Restrict to assigned changes, including relevant untracked files; `/core` is a generic assumption. Authorize the exact `.agents/code-reviews/` output. Judge severity from evidence rather than labeling every security finding critical. |
| Record implementation evidence | [validation/execution-report.md](../commands/validation/execution-report.md), `/validation:execution-report` | Supply the plan, actual result and exact `.agents/execution-reports/` output. Distinguish PASS/FAIL/SKIP/not-applicable; type checking is not a project gate and unrun integration tests are not passing. Use only when a durable report is part of the task. |
| Plan genuinely unresolved work | [core_piv_loop/plan-feature.md](../commands/core_piv_loop/plan-feature.md), `/core_piv_loop:plan-feature` | Optional. Do not repeat approved M1 planning, invent an 80% coverage gate or let its generic subagent advice bypass the Herdr lead. Use current scope and test requirements. |

GitHub administration belongs to the
[github-steward role](../agents/github-steward.md) and the scoped packet; there
is no requirement to force it through an application implementation command.
These existing routes need repair or an explicit, reviewed adaptation before use:

- `end-to-end-feature.md` points at absent `core_commands/*` files and a different
  plan directory. Do not use it as an automatic plan-to-commit pipeline.
- `do/implementation.md` references a missing repository `github-pm` skill and
  closes an issue after local checks, conflicting with merge-based closure.
- `validation/code-review-fix.md` points at missing `commands/validate.md`.
  Bind the findings/scope explicitly and use the actual repository gates rather
  than claiming the missing command ran.
- `validation/system-review.md` names absent flat planner/executor paths and an
  inconsistent third argument. Actual procedures are under `core_piv_loop/`;
  a process review is optional and does not authorize rewriting policy.
- PRP creators depend on absent `PRPs/templates/prp_base.md`; do not bootstrap
  another planning framework just to satisfy a command template.

For direct invocation, verify discovery in the worker session. The documented
nested-file alias uses colon separators. Current Claude positional arguments
are zero-based (`$0` is first); some repository templates instead start at `$1`.
Do not guess bindings. Explicit file-read mode uses named packet inputs and
does not perform native placeholder substitution or dynamic shell injection.
Inspect shell snippets separately and run only applicable, authorized commands.
[Claude command and argument documentation](https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name).

## Recovery decisions

These are project decisions inferred from the documented mechanisms; choose
commands from the installed skill rather than treating this table as a script.

| Observation | Required interpretation and next action |
|---|---|
| Submission acknowledged, no observed activity | Task start is unconfirmed. Inspect the worker before another submission. |
| A settled state returns but the report names another task | Keep the new assignment unresolved; collect its matching report. |
| Unexpected idle, unknown state or approval UI | Inspect current output. Do not submit approval keystrokes from the badge alone. |
| Report is clipped or unavailable | Try the skill's history-read mechanism; use its temporary-file fallback only if necessary. |
| Worker becomes unreachable while writing | Keep ownership reserved until the previous writer is known to have stopped. |
| Input changes during dependent work | Tell the worker which input changed; review or rerun only affected work. |
| Reconnected or restored session | Reconcile live identity, cwd, baseline, artifacts and commands with the task record. |
| Worker checks pass but integration changes files/contracts | Verify the combined result; preserve which revision earlier evidence covered. |

Ports, container names and temporary data roots are additional ownership fields
for this project's local-container and Chroma checks. A second checkout does
not isolate those resources or provide an OS sandbox. Preserve actual durable
data and secrets; serialize resource use when separate instances are unsuitable.

Before closing owned panes or removing worktrees, confirm no task still needs
them, preserve results and dirty files, and identify owned running processes.
An interface cleanup must not silently become checkout deletion or service
termination. If a cleanup target's ownership is uncertain, leave it intact.

## Source review and authority

Checked 2026-11-15. The lifecycle and ownership expansion was reviewed by three
research/review agents against documentation and repository instructions. The
command-routing addition was checked separately through static inspection of
the command files and Claude documentation; native invocation remains untested.
No live Herdr agents were started or controlled, and no hooks, integrations or
server settings were changed as part of that verification.

Use the [official documentation index](https://herdr.dev/tui/docs/) to find the
matching feature/version. The following pages support the operational cautions:

| Primary source | Documented behavior informing the rule |
|---|---|
| [Agent skill file](https://herdr.dev/tui/docs/agent-skill/) | Read the operating skill; `herdr --skill` prints the installed release's bundled copy. The separate `agent-guide.md` is for human onboarding and troubleshooting. |
| [Agent automation](https://herdr.dev/tui/docs/agent-automation/) | Agent-aware control differs from raw terminal input; submission/waits are not task-specific acceptance. |
| [Agents](https://herdr.dev/tui/docs/agents/#blocked-state) | Lifecycle detection can miss unfamiliar blocking screens; a status label needs contextual interpretation. |
| [Session state and restore](https://herdr.dev/tui/docs/session-state/) | Detach, restart, screen replay and native conversation restoration preserve different state. |
| [Integrations](https://herdr.dev/tui/docs/integrations/#how-herdr-uses-integrations) | Integration capabilities vary. Claude/Codex integrations supply session identity for resume; lifecycle detection still uses screen state in the documented versions. |
| [CLI reference](https://herdr.dev/tui/docs/cli-reference/) | Targeting and worktree/workspace operations have distinct semantics; installed client/server capabilities must be checked when relevant. |

The user-supplied [Deep Dive](https://acchapm1.github.io/tutorials/Herdr/herdr-deep-dive)
and [Beginner Guide](https://acchapm1.github.io/tutorials/Herdr/herdr-beginner-guide)
are secondary explanatory material. Their examples are not a command contract:

- Deep Dive §4.8 and its orchestration example contain targeting/status forms
  that differ from the inspected installed skill; do not select IDs by list
  position or paste raw key sequences to orchestrate recognized agents.
- Both tutorials generalize integration-provided status. The current official
  integration page distinguishes session identity from lifecycle reporting.
- Both troubleshooting sections suggest broad socket deletion. Do not copy
  that recovery into a live mission; diagnose the exact session and preserve
  running work instead.
- Installation, configuration tuning, raw socket automation and experimental
  restore/handoff features are outside routine project coordination.

The lead/worker roles, English prompts, default three-session/two-active limit,
resource ownership, acceptance record and integrated checks are project policy,
not Herdr guarantees. The explicit Herdr request/environment boundary comes
from the installed skill. Historical preparation packets are examples only;
[EXEC-01](../../docs/.prepare/execution-plan.md) and the
[current delivery override](../../docs/.prepare/methodology-adaptation.md)
continue to govern scope and sequencing.
