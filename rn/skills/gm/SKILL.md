---
name: gm
description: Ask rn to revise what it last presented — /rn:gm <feedback> takes the feedback as written, plain /rn:gm takes it from the session PR's unresolved review threads — record it in steering.md, and stop so /rn:up revises in a fresh conversation. Has side effects (commits, pushes) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Records the user's request for a revision where a fresh conversation will find it, so the revision
starts from the feedback and not from a summary of it.

## Steps

1. **Enter the session** as in Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. **Take the feedback.** `$ARGUMENTS`, trimmed, not empty → that text, word for word. Empty → the
   session PR's unresolved review threads; with no PR, ask for the feedback as `/rn:gm <feedback>`
   and stop.
3. **Hand off** as in Handing off to a fresh conversation in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, with that feedback as `Feedback`.
