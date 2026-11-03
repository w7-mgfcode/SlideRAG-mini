#!/usr/bin/env bash
# list_repos.sh
# Enumerate every repository accessible via gh CLI (user's own + every org
# the user is a member of). Output is a Markdown table sorted by org/owner.
#
# Usage:
#   bash list_repos.sh [--limit N] [--filter <substring>]
#
# Exit codes: 0 = success, 2 = bad usage / auth.

set -euo pipefail

LIMIT=200
FILTER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    --filter) FILTER="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh CLI is not authenticated. Run \`gh auth login\` first." >&2
  exit 2
fi

REPOS_FILE="$(mktemp)"
trap 'rm -f "$REPOS_FILE"' EXIT

# Gather user's own repos
gh repo list --limit "$LIMIT" --json nameWithOwner,description,isPrivate,updatedAt \
  -q '.[] | [.nameWithOwner, .description, .isPrivate, .updatedAt] | @tsv' \
  >> "$REPOS_FILE" 2>/dev/null || true

# Gather repos for each org
ORGS=$(gh api user/orgs -q '.[].login' 2>/dev/null || true)
for ORG in $ORGS; do
  gh repo list "$ORG" --limit "$LIMIT" --json nameWithOwner,description,isPrivate,updatedAt \
    -q '.[] | [.nameWithOwner, .description, .isPrivate, .updatedAt] | @tsv' \
    >> "$REPOS_FILE" 2>/dev/null || true
done

# Dedupe and sort
sort -u -o "$REPOS_FILE" "$REPOS_FILE"

TOTAL=$(wc -l < "$REPOS_FILE" | tr -d ' ')
echo ""
echo "| Repository | Description | Visibility | Updated |"
echo "|---|---|---|---|"

while IFS=$'\t' read -r REPO DESC PRIVATE UPDATED; do
  [[ -z "$REPO" ]] && continue
  if [[ -n "$FILTER" ]] && [[ "$REPO" != *"$FILTER"* ]]; then
    continue
  fi
  VIS="public"
  [[ "$PRIVATE" == "true" ]] && VIS="private"
  DESC_CLEAN=$(echo "${DESC:-}" | sed 's/|/\\|/g' | head -c 100)
  echo "| $REPO | ${DESC_CLEAN:--} | $VIS | $UPDATED |"
done < "$REPOS_FILE"

echo ""
echo "Total accessible repositories: $TOTAL" >&2
[[ -n "$FILTER" ]] && echo "(filtered by substring: '$FILTER')" >&2

exit 0
