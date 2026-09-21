---
name: ty
description: Approve what rn last presented for a decision — the plan, a design, the evaluation, or a reviewed result — and let the session advance. Has side effects (checks off, commits, runs the next task) — run only on explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

Records the user's approval of the pending decision and moves the session on. Changes nothing
about what was approved.

## Steps

1. **Take up the conductor's role and enter the session, so the approval lands on the right
   session in its current shape.** Read `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, then
   run Entering a session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

2. **Name what is being approved, so the verdict cannot land on the wrong thing.** It is the most
   recent gate or reviewed item presented for a decision — in this conversation, or in `State`'s
   `Pending` after a resume. Say it back in one line. If more than one is plausible, ask which,
   with a recommendation, opening with the session-status block. Nothing pending → say so with the
   block and stop.

3. **Advance from the approved point, so the approval has an effect the record shows.**
   - Plan gate → run task #1 per `${CLAUDE_PLUGIN_ROOT}/references/task.md`.
   - "Design sign-off" task → check it off per Checking a task off in
     `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, push, then continue the task loop at the next
     unchecked task.
   - "Evaluation sign-off" task → check it off the same way with `Status: closed` in the same
     commit, push, mark the PR ready for review, and close the session with a report that opens
     with the session-status block and names the merge as the user's next move.
   - A reviewed item → it stands as final; continue whatever was waiting on it.
