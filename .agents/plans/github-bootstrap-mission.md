# Mission — GitHub bootstrap for SlideRAG Mini

> **Agent:** `github-steward` (`.claude/agents/github-steward.md`). Read it in full first. It defines the taxonomy, templates, and operating rules this mission uses.
> **Issued:** 2026-11-03 by the owner (`w7-mgfcode`), via the orchestrator session.
> **Owner authorizations already given:** create a **public** repo `w7-mgfcode/SlideRAG-mini`; the git identity is set locally (`Gabor Szabo <shellsnake@icloud.com>`); model the project on cvforge-ai (milestones → umbrella → epic → sub-issues on a Projects v2 board).

> **Planning update, 2026-11-03:** Option C is approved in `docs/.prepare/decision-log.md` § 4–5. `docs/.prepare/execution-plan.md` now governs scope, milestone allocation, and acceptance. Preserve this mission's public-repository/hierarchy preference, but bundle implementation by milestone outcome. This update does not execute the mission or claim any GitHub object exists.

## Current state

- The local repo has `main` with **0 commits** and **no remote**. The untracked content is `.claude/`, `.dockerignore`, `.gitignore`, `docs/`, plus this `.agents/` folder.
- `.gitignore` already excludes `.legacy-assets/` (48 MB zips), `.env*`, `data/`, `HANDOFF.md`, `.handoffs/`, `docs/.prepare/delegation/` and `.claude/settings.local.json`.
- There is no code. Option C direction is approved (D-16…D-21); historical A-1…A-7 are superseded by current readiness/question dispositions. Operational prerequisites remain unverified.
- Repository-name availability and existing project numbers were observed in the earlier mission session; re-check before creating objects. The later architectural review could not connect to GitHub's API.

## Phase 0 — Prime (read-only, ~5 min)

1. Read the rules and plan files listed under "Read before acting" in your agent definition.
2. Study the references:
   - `gh issue view 129 -R w7-mgfcode/cvforge-ai`, then the same for 130 and 135
   - `gh project field-list 2 --owner w7-mgfcode`
   - `gh api repos/w7-mgfcode/ForecastLabAI/contents/.github/ISSUE_TEMPLATE`, then `.github/PULL_REQUEST_TEMPLATE.md`, `.github/dependabot.yml` and `.github/workflows/ci.yml`

## Phase 1 — Repo bootstrap and first commit

1. **Pre-push scan.** Run `git add -A --dry-run`. Over that file list, scan for secret patterns, `.env` files, files over 5 MB, and the `.legacy-assets` zips (see Operating rules). On any hit, **stop** and report.
2. `gh repo create w7-mgfcode/SlideRAG-mini --public` with a one-line description, and **no** `--source`/`--push` yet. Set topics, disable the wiki, allow squash merge only, and turn on auto-delete of head branches.
3. Labels: the full taxonomy from the agent definition, created idempotently.
4. Milestones: `M0 - Preparation`, `M1 - Stack Proof`, `M2 - Complete Local Path`, `M3 - Failure & Evidence Checks`, `M4 - Deployment & Demo`, `v0.1.0 - Release Gate`. Cite EXEC-01 § 8 budgets and observable exits. Do not double-count release checks or workflow allowance.
5. **Issue #1:** `docs: add documentation-first preparation package`. Put it in milestone `M0 - Readiness` with labels `type:sub-issue` and `area:docs`. The body lists what the commit contains and what was deliberately left out: `docs/.prepare/delegation/` is git-ignored, with the owner's decision on it pending.
6. First commit on `main`: `git add -A` (only after the scan passed), then `git commit -m "docs: add documentation-first preparation package (#1)"`. Do **not** add any trailer; the hook checks this. Then `git remote add origin git@github.com:w7-mgfcode/SlideRAG-mini.git` and `git push -u origin main`. If SSH fails, use the HTTPS URL with gh's credential helper. Never embed a token in the URL.
7. Close #1 with a comment giving the commit SHA.

## Phase 2 — Projects v2 board

1. Create `SlideRAG Mini Delivery` (owner `w7-mgfcode`), make it public, and link it to the repo.
2. Create the fields from the agent definition and replace the `Status` options. Write the board README and a short description.

## Phase 3 — Decomposition (the core of this mission)

Source: `docs/.prepare/execution-plan.md` §§ 7–9. The direction is approved; runtime acceptance is pending. Do not decompose the unselected full-lifecycle proposal into mandatory implementation work.

1. **Umbrella U1:** `feat(repo): sliderag mini v0.1.0 — grounded pptx q&a with slide citations on ec2`. Use EXEC-01's definition of done and exclusions. Record that 480 minutes is a timebox, not a validated forecast; preparation is separately accounted for and measured variance must be reported.
2. **Epics** (native sub-issues of U1), each with its milestone:
   - E0 `M0 - Preparation`: bootstrap, credentials/toolchain readiness, safe host preparation, publication provenance. Approval is already recorded; only genuine missing prerequisites justify a blocked label. Default to self-contained public summaries of ignored provenance; preserve local originals.
   - E1 `M1 - Stack Proof`
   - E2 `M2 - Complete Local Path`
   - E3 `M3 - Failure & Evidence Checks`
   - E4 `M4 - Deployment & Demo`
   - E5 `v0.1.0 - Release Gate`: QG-09 on EC2, CHANGELOG, tag.
3. **Sub-issues** under each epic, derived from EXEC-01's observable outcomes, normally one implementation issue/PR per milestone:
   - Each needs a scope from the commit allow-list, its files, `gate:` labels for the QGs it proves, `Estimate (min)`, and acceptance criteria that a command or a named test can verify.
   - One branch and one PR each. Minor steps are checkboxes; do not create minute-sized PRs.
   - Include minimal ruff/pytest CI within E1's outcome after pyproject exists. Use commit type/scope `chore(ci)`, not the unsupported `ci(ci)` type; no separate CI sub-issue is required.
4. Link everything as native sub-issues, add every issue to the board, and set Type, Area, Priority, Gate, Estimate and Status:
   - `Blocked` for anything waiting on an owner decision
   - `Ready` for E0's actionable items
   - `Backlog` for the rest
5. **Budget table:** use EXEC-01 § 8: 60/150/105/75 minutes, 30 workflow, 60 reserve. Report preparation separately. Parent rollups must not duplicate child estimates; report overruns honestly.

## Phase 4 — Repo design PR (opened, not merged)

1. Cut `chore/repo-github-scaffold` from `main`, with an issue under E1 (or E0) first.
2. Add `.github/ISSUE_TEMPLATE/` (umbrella, epic, sub-issue, bug, `config.yml`), `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS` and `dependabot.yml`. **No** CI workflow yet; it belongs to its E1 sub-issue.
3. Commit, push, and open the PR with `Closes #n`. **Do not merge.** Leave it for the owner's review.

## Out of bounds for this mission

- Application code (`app/`, `tests/`, `demo/`, `pyproject.toml`)
- Edits to `.claude/rules/`
- Approval lines in `decision-log.md`
- Branch protection, tags or releases
- Deleting anything
- Merging the PR

## Done when

Your final report (in `output-formatting.md` style) contains:
- the repo URL
- the board URL
- the 🔗 table of every created object with URLs
- the issue tree (U1 → E0…E5 → sub-issues with numbers)
- the budget table
- the PR URL
- `👉 Next steps` for the owner

Then wait in the session for owner feedback.
