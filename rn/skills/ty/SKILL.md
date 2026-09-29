---
name: ty
description: Approve the sign-off an rn session is waiting for — the plan, the design, or the deliverable — record it, and stop. It commits, pushes, and at the Deliverable sign-off marks the pull request ready, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

## Purpose

The user's approval becomes the ground all the work after it stands on, so the session goes on from it
without asking again. It is recorded and the session stops, so they can clear the conversation.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line is
   not waiting for a sign-off → say what the session is doing, and stop.
2. Mark the sign-off `[x]`. At the Deliverable sign-off, set `status` to `finished` and mark the pull
   request ready with `gh pr ready`.
3. Commit and push with the decision line
   `● {sign-off name} ── approved → {work out the design | plan the tasks | finished}`, and say in the
   user's language:

   ```
   ● Approved the {plan | design}. Next: say "go on", or /clear and /rn:up.
   ```

   At the Deliverable sign-off, say instead that the session is finished and the merge is theirs.
4. When the user says to go on, go on as `/rn:up` does.
