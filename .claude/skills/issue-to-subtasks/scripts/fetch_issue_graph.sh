#!/usr/bin/env bash
# fetch_issue_graph.sh
# Pull the full delivery context for an issue: the issue itself, linked PRs,
# referenced issues, sibling open issues from the same assignees, project board
# state, and key comment timeline.
#
# Usage:
#   bash fetch_issue_graph.sh <owner/repo> <issue_number>
#
# Output: Single JSON object on stdout, structured for easy consumption by Claude.
# Exit codes: 0 = success, 1 = issue not found, 2 = bad usage / auth.

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <owner/repo> <issue_number>" >&2
  exit 2
fi

REPO="$1"
ISSUE_NUM="$2"

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh CLI is not authenticated. Run \`gh auth login\` first." >&2
  exit 2
fi

if ! [[ "$ISSUE_NUM" =~ ^[0-9]+$ ]]; then
  echo "ERROR: issue number must be a positive integer (got: $ISSUE_NUM)" >&2
  exit 2
fi

# 1. Pull the target issue with all the rich metadata gh exposes
ISSUE_JSON=$(gh issue view "$ISSUE_NUM" --repo "$REPO" --json \
  number,title,body,state,url,labels,assignees,milestone,author,createdAt,updatedAt,closedAt,comments,projectItems,projectCards \
  2>/dev/null) || {
    echo "ERROR: could not fetch issue $REPO#$ISSUE_NUM. Check repo path and issue number." >&2
    exit 1
  }

# 2. Linked PRs (via gh's built-in cross-reference search)
LINKED_PRS=$(gh pr list --repo "$REPO" --search "$ISSUE_NUM in:body" \
  --state all --limit 20 --json number,title,state,url,author,updatedAt 2>/dev/null || echo "[]")

# 3. Issues that reference this one in their body or title
REFERENCING_ISSUES=$(gh issue list --repo "$REPO" --search "#$ISSUE_NUM in:body,title" \
  --state all --limit 20 --json number,title,state,url,updatedAt 2>/dev/null || echo "[]")

# 4. Sibling open issues from the same assignees
ASSIGNEES=$(echo "$ISSUE_JSON" | jq -r '.assignees[].login' 2>/dev/null || echo "")
SIBLING_ISSUES="[]"
if [[ -n "$ASSIGNEES" ]]; then
  SIBLINGS_TMP=$(mktemp)
  trap 'rm -f "$SIBLINGS_TMP"' EXIT
  echo "[]" > "$SIBLINGS_TMP"
  for USER in $ASSIGNEES; do
    USER_ISSUES=$(gh issue list --repo "$REPO" --assignee "$USER" --state open \
      --limit 20 --json number,title,labels,milestone,updatedAt 2>/dev/null || echo "[]")
    # Merge with existing siblings file (deduped by number)
    jq -s '.[0] + .[1] | unique_by(.number)' "$SIBLINGS_TMP" <(echo "$USER_ISSUES") > "${SIBLINGS_TMP}.new"
    mv "${SIBLINGS_TMP}.new" "$SIBLINGS_TMP"
  done
  SIBLING_ISSUES=$(cat "$SIBLINGS_TMP")
fi

# 5. Parse referenced issues out of the body and comments (matches #N patterns)
BODY_TEXT=$(echo "$ISSUE_JSON" | jq -r '.body // ""')
COMMENTS_TEXT=$(echo "$ISSUE_JSON" | jq -r '[.comments[].body] | join("\n")')
REFERENCED_NUMBERS=$(echo "$BODY_TEXT $COMMENTS_TEXT" \
  | grep -oE '#[0-9]+' \
  | sort -u \
  | head -30 \
  | jq -R -s -c 'split("\n") | map(select(length > 0))')

# 6. Detect parent / blocked-by hints
PARENT_HINTS=$(echo "$BODY_TEXT" \
  | grep -iE '(parent|epic|blocked by|depends on|relates to|part of|tracking|fixes|closes|resolves)[[:space:]:]+#?[0-9]+' \
  | head -20 \
  | jq -R -s -c 'split("\n") | map(select(length > 0))')

# 7. CODEOWNERS check (best effort)
CODEOWNERS_HINT=""
if gh api "repos/$REPO/contents/CODEOWNERS" >/dev/null 2>&1; then
  CODEOWNERS_HINT="present at /CODEOWNERS"
elif gh api "repos/$REPO/contents/.github/CODEOWNERS" >/dev/null 2>&1; then
  CODEOWNERS_HINT="present at /.github/CODEOWNERS"
elif gh api "repos/$REPO/contents/docs/CODEOWNERS" >/dev/null 2>&1; then
  CODEOWNERS_HINT="present at /docs/CODEOWNERS"
fi

# Assemble the unified output
jq -n \
  --argjson issue "$ISSUE_JSON" \
  --argjson linked_prs "$LINKED_PRS" \
  --argjson referencing_issues "$REFERENCING_ISSUES" \
  --argjson sibling_issues "$SIBLING_ISSUES" \
  --argjson referenced_numbers "$REFERENCED_NUMBERS" \
  --argjson parent_hints "$PARENT_HINTS" \
  --arg repo "$REPO" \
  --arg codeowners "$CODEOWNERS_HINT" \
  '{
    repo: $repo,
    issue: $issue,
    linked_prs: $linked_prs,
    referencing_issues: $referencing_issues,
    sibling_issues_from_assignees: $sibling_issues,
    referenced_issue_numbers: $referenced_numbers,
    parent_or_blocker_hints: $parent_hints,
    codeowners: $codeowners
  }'

exit 0
