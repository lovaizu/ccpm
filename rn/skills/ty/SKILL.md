---
name: ty
description: Approve the decision an rn session stopped for — the plan, a design choice, or the finished work — record it, and stop. It commits, pushes, and at the last sign-off marks the pull request ready, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

## Purpose

The user's approval becomes the ground all the work after it stands on, so the session goes on from it
without asking again, in this conversation or a later one.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. `Next` not at a sign-off →
   say what the session is doing, and stop.
2. Check the sign-off and set `Next` past it.
3. At a Design sign-off, record the approved choice as a Fact in `Assumptions`.
4. At the Evaluation sign-off the session ends: remove `evaluations/` and mark the pull request ready
   with `gh pr ready`.
5. Commit, push, and say in the user's language:

   ```
   ● Approved: {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```

   At the Evaluation sign-off, say instead that the session is finished, that the merge is theirs, and
   what `Notes` says waits on it.
6. When the user says to go on, go on as `/rn:up` does.
