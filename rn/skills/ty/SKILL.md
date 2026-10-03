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

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line does
   not end `waiting for #{id} {sign-off name}` → say what the session is doing, and stop.
2. Mark that task `[x]`. At the Deliverable sign-off, set `status` to `finished` and mark the pull
   request ready with `gh pr ready`.
3. Commit and push with the decision line
   `● #{id} {sign-off name} ── approved → {the first task not [x]; planning the tasks, after the Design sign-off; finished, after the Deliverable sign-off}`, and say, in the
   `conversation-language` of `steering.md`:

   ```
   {the decision line}

   Say "go on", or /clear and then /rn:up.
   ```

   At the Deliverable sign-off, say instead, after the decision line, that the pull request is ready,
   with its URL, and that the merge is theirs.
4. When the user says to go on, go on as `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` says, from its
   third step.
