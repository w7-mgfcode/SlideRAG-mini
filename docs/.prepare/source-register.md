# Source Register

| Field | Value |
|---|---|
| Document ID | PREP-03 |
| Title | Source Register |
| Revision | r3 |
| Status | Dated historical register with Option C evidence/approval additions |
| Owner | Orchestrator (Principal Architect session); approver: repository owner |
| Last updated | 2026-11-03 |
| Evidence baseline | Historical 2026-11-02 register plus dated 2026-11-03 Option C addendum; no commits |
| Core-context revision used | r1 for original register; r3 for current addendum |
| Dependencies | none (root evidence document) |
| Supersedes | — |
| Approval record | [decision-log.md § 4](decision-log.md#4-owner-approval-record); direction approval, not blanket validation of sources |
| Change summary | r1: initial register. r2: SR-30…SR-36. r3: SR-37…SR-40, current authority and dated official-documentation checks |

## Revision honesty statement

- **Revisions in this package are manual labels (r1, r2, …), not immutable identifiers.** The repository was initialised with `git init -b main` on 2026-11-02 and has **no commits**, so no commit SHA exists for any repository file. A revision label changes only when an author edits the document and bumps it; nothing enforces that.
- **A retrieval date is not a revision.** Where a source is external, the "Revision / retrieval" column states which of the two it is. Only SR-20 (playbook) has an upstream commit SHA; the rest are dated retrievals or local file hashes.
- Where a local file hash is given, it is the first 12 hex characters of `sha256sum` at the evidence baseline. Hashes are evidence of byte identity on that date, not a version-control record.

## Register

The original rows describe their dated baseline, including authority at that time. Current authority is EXEC-01/SR-39, approved through SR-38; SR-01 is preserved historical input. Original hashes remain unchanged. Current rule edits and later observations are not represented by old line counts.

Authority scale: **A** = governing (wins on conflict) · **B** = binding policy · **C** = evidence of state · **D** = methodology/reference (not evidence about this project) · **E** = unverified external claim.

| ID | Path / URL | Type | Authority & intended use | Revision / retrieval | Relevant sections | Known limitations |
|---|---|---|---|---|---|---|
| SR-01 | `docs/.prepare/brainstorm-plan.md` | Product/architecture plan v1.0 (amended) | **A** — named source of truth by `product-vision.md:3`. Review target of [plan-review.md](plan-review.md). Treated as *input to evaluate*, not an approved spec. | File, sha256 `8a5e41cc903a`; v1.0 dated 2026-11-02 with two editorial amendments | §1–§12; key lines: DoD L26, scope L28–49, ingestion L80–87, stack L102–137, tree L140–189, graph L190–248, AWS L249–318, roadmap L319–369, dataset L371–396, QGs L398–420 | Plain-text paste of a rendered page: no markdown headings, table cells tab-separated, stray citation residue ("OpenAI API +1", "GitHub +1", "DoiT Compute +2"). Prices and model availability are author claims (see SR-22). § 3 Mermaid edges are a reconstruction (HANDOFF.md "Decisions Made"). |
| SR-02 | `docs/.prepare/archive/brainstorm-plan.v1.0-original.md` | Pre-amendment copy of SR-01 | **C** — byte-exact preservation of the original. Never modify. | File, sha256 `2c576598359a`; verified byte-identical to the session scratchpad `.bak` on 2026-11-02 | Whole file; differs from SR-01 in 35 diff lines (§ 3 diagram, § 9 operator name) | Contains a pasted 9 KB SVG stylesheet line and a real operator name; not for reuse in public docs. |
| SR-03 | `.claude/rules/product-vision.md` | Policy rule | **B** — scope lock, guardrails, litmus test. Declares SR-01 the source of truth. | File, 94 lines, retrieved 2026-11-02 | L3 (source of truth), L11–20 (principles), L22–45 (scope lock + freeze), L47–57 (guardrails), L59–67 (hard no), L69–80 (litmus test) | Mirrors SR-01 v1.0; will drift if a revised plan is approved without updating it. |
| SR-04 | `.claude/rules/security-patterns.md` | Policy rule | **B** — security requirements for all code. | File, 87 lines, retrieved 2026-11-02 | L7–19 (forbidden), L23–33 (secrets/config keys, L31), L35–43 (upload validation), L45–50 (storage, `/data` containment L49), L52–56 (untrusted text), L58–61 (HTML), L63–67 (external calls), L69–73 (deployment) | "Fixed ceiling" for uncompressed size has no number. L49's "MUST be under `/data`" collides with local dev and temp-dir tests (finding F-11). |
| SR-05 | `.claude/rules/test-requirements.md` | Policy rule | **B** — test layers, gates, QG→test mapping, eval set. | File, 80 lines, retrieved 2026-11-02 | L15–27 (gates), L29–43 (QG map), L45–55 (eval set), L57–59 (load-bearing tests), L61–66 (when tests required), L68–73 (conventions) | Integration tests with a live LLM are inherently non-deterministic; pass criteria for synthesis questions are not defined. |
| SR-06 | `.claude/rules/commit-format.md` | Policy rule | **B** — commit grammar and scope list; forbids AI co-author trailers. | File, 80 lines, retrieved 2026-11-02 | L9–14 (rules, types L11), L16–33 (scopes), L35–45 (no AI trailer), L65–67 (scope exception), L69–80 (before committing) | Type list has no `ci`, though `versioning.md:26` treats `ci` as a commit type. |
| SR-07 | `.claude/rules/branch-naming.md` | Policy rule | **B** — branch naming; one issue per branch. | File, 46 lines, retrieved 2026-11-02 | L5–13 (format), L32–37 (rules), L39–44 (before creating) | Presupposes a GitHub remote and issues; none exist yet. |
| SR-08 | `.claude/rules/versioning.md` | Policy rule | **B** — single SemVer train, manual tagging. | File, 28 lines, retrieved 2026-11-02 | L5–9 (train), L11–17 (release procedure), L19–28 (bump map, `ci` at L26) | References `pyproject.toml` and `CHANGELOG.md`, which do not exist yet. |
| SR-09 | `.claude/rules/output-formatting.md` | Policy rule | **B** — report formatting for skill output. | File, 109 lines, retrieved 2026-11-02 | whole | Applies to skill/report output, not to the planning documents themselves. |
| SR-10 | `.claude/hooks/check-commit-format.sh` + `.claude/settings.json` | Deterministic hook | **B** — PreToolUse gate on `git commit`. | Files, 127 lines / 15 lines, retrieved 2026-11-02 | hook L81 (subject regex), L89–99 (AI trailer checks), L106–125 (deny JSON; literal `\\n` built at L109) | Regex makes scope optional for every type (rule allows omission only for `docs`/`release`); deny message ends with a literal `\n` (HANDOFF open question). Fires only on `git commit`, so it is inert until the owner commits. |
| SR-11 | `.claude/agents/*.md` (3), `.claude/skills/*/SKILL.md` (15), `.claude/commands/**` (27) | Agent tooling | **C** — inventory of available automation. | Directory listing, retrieved 2026-11-02 | `repo-visibility-manager.md`, `audit-rules-drift`, `commit-format-check`, `library-claim-verify`, `managing-agent-memory` are project-specific | Mission § 0 says "16 skills"; 15 exist since the dangling `shadcn` symlink was removed (HANDOFF.md). Most commands are generic, not tuned to this repo. |
| SR-12 | `.claude/settings.local.json` | Local settings | **C** | File, retrieved 2026-11-02 | `permissions.allow`, `enableAllProjectMcpServers`, `enabledPlugins` | Local, not team policy. |
| SR-13 | `HANDOFF.md` | Session handoff | **C** — state and open questions of the previous session. Not to be modified. | File, 10,319 bytes, mtime 2026-11-02 18:36 | "Open Questions", "Context for Next Session" | Written by an agent; its claims were spot-checked (archive hashes, toolchain versions, symlink removal) on 2026-11-02 and held. |
| SR-14 | `.handoffs/2026-11-02-tooling-adaptation.md` | Archived handoff | **C** | File, 86 lines, retrieved 2026-11-02 | L64–70 (open questions) | Superseded by SR-13 except for carried open questions. |
| SR-15 | `~/.claude/projects/<this-project>/memory/` | Agent memory | **C** — auto-mode constraints. | `MEMORY.md` + `auto-mode-destructive-ops.md`, retrieved 2026-11-02 | whole | Outside the repository; describes harness behaviour, not the product. |
| SR-16 | `docs/.prepare/starter-orchestrator-prompt.md` | Mission prompt | **A for this documentation phase** — owner-stated parameters in § 0. | File, 153 lines, saved by owner 2026-11-02 18:32 | § 0 (parameters), § 2 (operating rules), § 6 (rubric), § 10 (readiness) | § 0 inventory counts are slightly stale (16 skills vs 15). § 0 still names the scratchpad `.bak` as the archive source; verified still present and identical. |
| SR-17 | Repository tree | Filesystem evidence | **C** | `tree`/`find` on 2026-11-02 | — | **No** application source, dependency manifest, tests, Dockerfile, CI, CLAUDE.md, AGENTS.md, README.md, or GitHub remote exist. No `.env*` file exists. |
| SR-18 | Host toolchain | Environment evidence | **C** | Observed 2026-11-02: Python 3.14.4, uv 0.12.7, git 2.53.0, Claude Code 2.1.316, Herdr 0.9.5 (protocol 22) | — | Docker/gh/aws versions taken from HANDOFF.md, not re-observed this session. |
| SR-19 | `~/.claude/skills/herdr/SKILL.md` + `herdr --help`, `herdr agent`, `herdr tab`, `herdr pane`, `herdr worktree` | Delegation tool docs | **D** — the only permitted delegation mechanism. | Read in full 2026-11-02; CLI v0.9.5 | "Start and coordinate an agent", "Safety and coordination rules"; `worktree create` requires `--branch` | The skill defaults to sibling panes; tabs used here because the owner explicitly asked for named tabs. |
| SR-20 | https://github.com/yibie/ai-native-sdlc-playbook/blob/main/book.md | Methodology | **D** — methodology source only; never evidence about this project. | **Upstream commit `4a48004`** (2026-09-03T07:54:44Z, last commit touching `book.md`); raw file retrieved 2026-11-02, 1,374 lines, sha256 `37dbc5d6c40d` | Intro L30–143; Stage 1 L144–240; Stage 2 L241–320; plan mode L321–434 (source of truth L381–428); CLAUDE.md L435–519; skills & build hooks L520–622; parallel sessions L623–710; feedback loop L711–796; evals L797–891; PR review L892–978; approval hooks L979–1132; CI/CD L1133–1215; metrics L1216–1315 | **Secondary transcription**: header (L3–6) states it is a community compilation of the Anthropic Claude Academy course "The AI-Native SDLC Playbook" (academy.claude.com). Fidelity to the official course is not verified. Line numbers refer to the raw file at the commit above. |
| SR-21 | `git init -b main` | Repository event | **C** | Executed once, 2026-11-02 | — | No commits, branches beyond unborn `main`, tags, or remotes. |
| SR-22 | Plan-cited external facts (OpenAI model names and prices, AWS prices, LangGraph `StateGraph`, `langchain-chroma` `persist_directory`, AWS SSH guidance) | Claims inside SR-01 | **E** — unverified for 2026-11-02. | Not retrieved this session | SR-01 L111–122, L194–196, L268–270, L286, L295–313 | Not independently checked in this phase. Verification is recommendation R-12 (scaffold time, `library-claim-verify` skill, provider model list). |

## Library documentation and delegated artifacts (added in r2)

The orchestrator consulted no library documentation itself. These entries come from the S2 and S3 completion reports, integrated by the orchestrator.

| ID | Path / URL | Type | Authority & intended use | Revision / retrieval | Relevant sections | Known limitations |
|---|---|---|---|---|---|---|
| SR-30 | python-pptx **1.0.2**, host copy at `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/pptx/` | Library source | **C** for the claims in PREP-08 § 8.B.3 (XML parser `resolve_entities=False`; all members read into memory on open) | Version from `python_pptx-1.0.2.dist-info`; read 2026-11-02 by S2, re-read by S3 | `oxml/__init__.py` L21, L34–36; `opc/serialized.py` L191–195; `opc/package.py` L277, L399, L482 | **Weak provenance:** another tool's runtime cache, not the project's environment (none exists). It is not the version that will be pinned. Re-verify against `uv.lock` at M1 (R-12). |
| SR-31 | lxml **6.1.1**, same host copy (`etree.cpython-312-x86_64-linux-gnu.so`) | Library binary | **C** for the `XMLParser` default signature | dist-info 6.1.1; read 2026-11-02 | embedded signature string | Same provenance caveat as SR-30 |
| SR-32 | CPython **3.14.4** `/usr/lib/python3.14/zipfile/__init__.py` | Stdlib source | **C** for the claim that `zipfile` bounds reads by the declared `file_size` | Host Python 3.14.4; read 2026-11-02 | L969, L1183–1185 | The plan targets 3.12, so 3.12 behaviour is [ASSUME] until checked in the pinned image |
| SR-33 | Context7 `/chroma-core/chroma`: `docs/mintlify/docs/overview/migration.mdx`, `reference/python/client.mdx` | Library docs | **D** for `Settings(anonymized_telemetry=False)` and `PersistentClient` | Retrieved 2026-11-02; docs version not stated | — | Default telemetry value and langchain-chroma parameter name unverified (R-12) |
| SR-34 | `docs/.prepare/delegation/S1-brainstorm-plan-revised.raw.md` | Delegated draft (raw) | **C** — provenance of S1's output before integration | sha256 `00f395311b2d`; created 2026-11-02 19:01 | whole | Superseded by PREP-08 r2 |
| SR-35 | `docs/.prepare/delegation/S2-security-verification.md` | Delegated draft (raw) | **C** — provenance of S2's output; merged into PREP-08 §§ 8, 9, 10.2 | sha256 `48fab0b65f67`; created 2026-11-02 19:02 | whole | Superseded by PREP-08 r2 |
| SR-36 | `docs/.prepare/delegation/S3-critic-review.md` | Independent review | **C** — basis for plan-review §§ 6–7 and the PREP-08 reconciliations | sha256 `de3bcc67137a`; created 2026-11-02 19:14 | whole | Reviewed pre-integration content |

## Option C review and approval (added in r3)

| ID | Source | Authority / use | Date and limitations |
|---|---|---|---|
| SR-37 | Current conversation: architectural review of preparation documents, rules, archived handoffs, and GitHub mission | Evidence-based recommendation; distinct from historical S3 review | 2026-11-03. No application/runtime tests existed; external account/cloud state not established. |
| SR-38 | Owner message: “APPROVE YOUR SUPERVIZED VISION” | Approval of the immediately preceding Option C recommendation; recorded verbatim in decision-log § 4 | 2026-11-03. No blanket approval of earlier proposals or proof of execution. |
| SR-39 | `docs/.prepare/execution-plan.md` r1 | **A** — governing execution direction, D-16…D-21 | 2026-11-03. Assistant transcription; implementation unverified. |
| SR-40 | Local Git/tree inspection in review/approval turns | **C** — unborn main, no commits/remote/application, configured Git identity; ignored provenance remains local | 2026-11-03. GitHub API connectivity failed during review; remote existence cannot be inferred. |

Official documentation consulted during the preceding review on 2026-11-03:

- [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini) and [text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small): documented offerings; no project-account access test.
- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs) and [ChatOpenAI](https://docs.langchain.com/oss/python/integrations/chat/openai): native schema support; schema validity does not establish factual correctness.
- [Chroma configuration](https://docs.trychroma.com/docs/collections/configure), [deletion](https://docs.trychroma.com/docs/collections/delete-data), and [persistence integration](https://docs.langchain.com/oss/python/integrations/vectorstores/chroma): explicit metric, metadata deletion, persistent local storage.
- [FastAPI concurrency](https://fastapi.tiangolo.com/async/) and [uploads](https://fastapi.tiangolo.com/tutorial/request-files/): concurrent threadpooled sync handlers and spooled files; exact parser APIs require pinned-version checks.
- [systemd RequiresMountsFor](https://www.freedesktop.org/software/systemd/man/257/systemd.unit.html), [AWS EBS initialization](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-using-volumes.html), and [Docker stats](https://docs.docker.com/reference/cli/docker/container/stats/): mount dependencies, safe initialization, single-sample limitation.

These dated references do not prove dependency compatibility, deployed behavior, resource usage, current regional AWS prices, or the eight-hour forecast. Preserve prior provenance locally; ignored/uncommitted artifacts are not Git history.
