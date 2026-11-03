## Summary

<!-- State the problem, resulting behavior and relevant EXEC-01 sections. -->

Closes #<!-- existing open issue; one outcome-sized branch and PR -->

## Validation

<!-- Attach commands/results and relevant QG proof. Keep unchecked items unchecked.
For documentation/scaffolding with no Python project, explicitly mark commands not applicable and explain why. -->

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run pytest -m "not integration"`
- [ ] Relevant quality gates and manual checks have evidence.

Live integration checks (only when authorized, synthetic-only): <!-- result or not run + reason -->

## Scope and vision

- [ ] Matches EXEC-01 and the product scope lock; deferred features are excluded.
- [ ] Estimate and actual time are recorded without double-counting parent rollups or release checks.
- [ ] Commit/PR title follows `type(scope): description (#issue)`; no AI attribution trailer.

## Security and data

- [ ] Publication scan is clean: credentials, `.env`, raw local records, runtime data, large files and legacy ZIPs excluded.
- [ ] Applicable upload, escaping, citation, data-preservation and private-deployment boundaries hold (explain N/A).

## Review notes

<!-- Risks, limitations, recovery, and unverified claims. Do not mark an acceptance criterion complete without proof.
Dependabot PRs: link an existing open issue and normalize the squash title before merge.
Merging, branch protection and tag pushes require owner authorization. No EC2 CD or automatic releases. -->
