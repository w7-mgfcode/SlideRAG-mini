# Versioning

SlideRAG Mini ships **one SemVer train** for the whole repo, tagged by hand. There is no release automation.

## Train

| Train | Tag | Source of truth | Changelog |
|-------|-----|-----------------|-----------|
| SlideRAG Mini | `vX.Y.Z` | `version` in `pyproject.toml` | `CHANGELOG.md` (root, hand-maintained) |

## Cutting a release

1. Confirm the plan's definition of done on EC2: upload the demo deck, ask a question, inspect slide references, recreate the container, query again.
2. Bump `version` in `pyproject.toml` and add a dated section to `CHANGELOG.md` in one `release(repo): cut X.Y.Z (#N)` commit on `main`.
3. Tag and push: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.

`v0.1.0` is cut the first time the definition of done passes end to end.

## SemVer mapping

| Commit | Bump |
|--------|------|
| `feat!:`, `fix!:`, or `BREAKING CHANGE:` in the body | MINOR while in `v0.x`; MAJOR after `v1.0.0` |
| `feat(...)` | MINOR |
| `fix(...)` | PATCH |
| `docs`, `chore`, `refactor`, `test` | No bump; listed under "Other" in the changelog. CI work uses `chore(ci)` under the existing commit grammar. |

While in `v0.x`, MINOR may include breaking changes — call them out under a `### Breaking` heading.
