#!/usr/bin/env bash
# resolve_issue.sh
# Given an issue number, scan accessible repositories (current user + every org
# the user belongs to) and report which repos contain that issue number.
#
# Usage:
#   bash resolve_issue.sh <issue_number> [--limit N]
#
# Output: Markdown table — one row per matching repo with title + state + age.
# Exit codes: 0 = at least one match, 1 = no matches, 2 = bad usage / auth.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <issue_number> [--limit N]" >&2
  exit 2
fi

ISSUE_NUM="$1"
LIMIT=200
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit) LIMIT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Sanity-check gh auth
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh CLI is not authenticated. Run \`gh auth login\` first." >&2
  exit 2
fi

# Validate issue number
if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
  echo "ERROR: issue number must be a positive integer (got: $ISSUE_NUM)" >&2
  exit 2
fi

echo "Searching for issue #$ISSUE_NUM across accessible repositories..." >&2

# Collect all accessible repos: user's own + every org they're a member of.
REPOS_FILE="$(mktemp)"
trap 'rm -f "$REPOS_FILE"' EXIT

# User's own repos
gh repo list --limit "$LIMIT" --json nameWithOwner -q '.[].nameWithOwner' >> "$REPOS_FILE" 2>/dev/null || true

# Each org the user belongs to
ORGS=$(gh api user/orgs -q '.[].login' 2>/dev/null || true)
for ORG in $ORGS; do
  gh repo list "$ORG" --limit "$LIMIT" --json nameWithOwner -q '.[].nameWithOwner' >> "$REPOS_FILE" 2>/dev/null || true
done

# Dedupe
sort -u -o "$REPOS_FILE" "$REPOS_FILE"

TOTAL_REPOS=$(wc -l < "$REPOS_FILE" | tr -d ' ')
echo "Scanning $TOTAL_REPOS repositories..." >&2

MATCHES=0
echo ""
echo "| # | Repository | Issue Title | State | Updated |"
echo "|---|---|---|---|---|"

while IFS= read -r REPO; do
  [[ -z "$REPO" ]] && continue
  RESULT=$(gh issue view "$ISSUE_NUM" --repo "$REPO" --json title,state,updatedAt 2>/dev/null || true)
  if [[ -n "$RESULT" ]]; then
    MATCHES=$((MATCHES + 1))
    TITLE=$(echo "$RESULT" | jq -r '.title' | sed 's/|/\\|/g')
    STATE=$(echo "$RESULT" | jq -r '.state')
    UPDATED=$(echo "$RESULT" | jq -r '.updatedAt')
    echo "| $MATCHES | $REPO | $TITLE | $STATE | $UPDATED |"
  fi
done < "$REPOS_FILE"

echo ""
if [[ $MATCHES -eq 0 ]]; then
  echo "No repositories contain issue #$ISSUE_NUM." >&2
  echo "Possible reasons: typo, repo not accessible, issue is in a private repo not in your gh auth scope." >&2
  exit 1
elif [[ $MATCHES -eq 1 ]]; then
  echo "One match found. Proceed with that repository." >&2
else
  echo "Multiple matches found ($MATCHES). Ask the user to pick one before proceeding." >&2
fi

exit 0
