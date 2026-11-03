### Subtask {{N}} — {{Imperative title, ≤80 chars}}

- **Purpose:** {{Single sentence — what this subtask exists to accomplish}}
- **Scope:**
  - {{Specific in-scope item}}
  - {{Specific in-scope item}}
  - {{Specific in-scope item}}
- **Out of scope:**
  - {{Specific NOT-this-subtask thing — explicit, not vague}}
  - {{Specific NOT-this-subtask thing}}
- **Dependencies:**
  - {{none, OR Subtask N must land first, OR external: PR #X must merge}}
- **Risks / blockers:**
  - {{Specific risk — what could go wrong with THIS subtask}}
  - {{Blocker if any — and what unblocks it}}
- **Acceptance criteria:**
  - {{Testable / observable check 1}}
  - {{Testable / observable check 2}}
  - {{e.g. "tests pass on CI", "metric X drops below Y", "manual check Z confirms"}}
- **Suggested owner:** {{@user or "any team member with X knowledge"}}
- **Estimated effort:** {{e.g. "half-day", "1 day", "2-3 days" — keep ranges tight; if >3 days flag as too big}}
- **Why it matters now:** {{1 line linking back to source-of-truth — issue body, comment, milestone, parent epic}}

---

## Filling guidelines

- **Title** uses an imperative verb and a concrete object. ✅ "Wire load test thresholds into CI". ❌ "CI improvements".
- **Scope bullets** name files, modules, or behaviors — not abstractions.
- **Out of scope** must be non-empty. If you can't think of anything, the subtask is too big.
- **Dependencies** point to other subtasks by number or to specific external work. "After related stuff is done" is not a dependency.
- **Acceptance criteria** must answer "how would I prove this is done?" — not "it works" or "looks good".
- **Effort** beyond 3 days for one person is a sign the subtask should split.
- **Owner** can be "@unassigned — needs claim" if no good signal exists, but flag it as ownership risk in the package.
