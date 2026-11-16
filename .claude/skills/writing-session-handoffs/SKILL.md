---
name: writing-session-handoffs
description: >
  Generates a structured session handoff document so the next session can resume
  without context loss. Gathers git state, extracts decisions with rationale,
  surfaces dead ends, and enforces that Next Step #1 is immediately actionable.
  Triggers on: "write a handoff", "session handoff", "end of session", "hand off
  to next session", "save session context". Do NOT use for: git commit messages,
  changelogs, PR descriptions, meeting notes, retrospectives.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Writing Session Handoffs — Claude Code entry point

Read the [shared handoff procedure](../../../.agents/skills/writing-session-handoffs/SKILL.md)
in full, then follow it for this request. Resolve this link relative to this
wrapper file, not the current working directory.

The shared procedure owns the workflow, output contract and resource paths.
Resolve its template relative to the shared skill directory; honor its target
repository-root and output-path rules. Do not maintain a second procedure here.
