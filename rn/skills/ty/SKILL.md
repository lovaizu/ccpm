---
name: ty
description: Approve the decision an rn session stopped for — the plan, a design choice, or the finished work — record it, and stop. It commits, pushes, and at the last sign-off marks the pull request ready, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

## Purpose

The user's approval becomes the ground all the work after it stands on, so the session goes on from it
without asking again. It is recorded and the session stops, so they can clear their conversation.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The first task not `[x]` is
   not a sign-off → say what the session is doing, and stop.
2. Mark the sign-off `[x]` and set `Feedback` to none. At a Design sign-off, record the recommended
   choice as a Fact in `Assumptions`. At the Finished work sign-off, set `status` to `finished`, remove
   `evaluations/`, and mark the pull request ready with `gh pr ready`.
3. Commit, push, and say in the user's language:

   ```
   ● Approved: {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```

   At the Finished work sign-off, say instead that the session is finished and the merge is theirs.
4. When the user says to go on, go on as `/rn:up` does.
