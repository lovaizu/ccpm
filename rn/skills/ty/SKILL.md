---
name: ty
description: Approve what rn last presented for sign-off — the plan, an approach, or the finished work — record it in steering.md, and stop so the session resumes after /clear with /rn:up. Has side effects (checks off, commits, pushes) — run only on explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

Records the user's approval where a fresh conversation will find it. Changes nothing about what
was approved.

## Steps

1. **Enter the session** as in Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. **Name what is approved.** It is the sign-off task last presented — the first task not yet
   complete. Say it back in one line. When that task is not a sign-off, nothing is awaiting
   approval: say so and stop.
3. **Record the approval.** Mark its step `[x]`, commit `docs: complete task #N — {task name}` —
   the marker only a check-off carries — and push. At "Evaluation sign-off", remove the session's
   `evaluations/` in the same commit: the session then leaves `steering.md` and the deliverable,
   and every verdict stays in the pull request's history.
4. **Close or hand off.** "Evaluation sign-off" → mark the PR ready for review and report the
   session closed, opening with the map in Stopping for the user in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`: the merge is the user's next move, followed by
   any work `Notes` has waiting on it. Otherwise → Handing off to a fresh conversation there,
   `Feedback` none.
