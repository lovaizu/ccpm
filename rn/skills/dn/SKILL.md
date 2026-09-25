---
name: dn
description: Suspend the current rn session — record where it stands in steering.md, commit and push everything, and hand off to /clear then /rn:up. Use when stopping: context nearly full, a break, end of day. Has side effects (commits, pushes) — run only on explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Suspend

Writes down where the session stands so a fresh conversation picks it up without being told.

## Steps

1. **Enter the session** as in Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. **Hand off** as in Handing off to a fresh conversation in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, `Feedback` none.
