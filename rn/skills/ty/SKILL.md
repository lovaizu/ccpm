---
name: ty
description: Approve the sign-off an rn session is waiting for, record it, and stop. It commits and pushes, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

1. Find the session and its current task as `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` steps 1 and 2
   say. When its CCS's `next` is not `waiting for #{id} {sign-off name}`, say there is nothing to
   approve, and stop.
2. Mark the task `[x]` in `steering.md`. Write the next task's CCS, `ccs/{next id}.yaml`, in the form
   of `ccs/1.yaml`, with `next` its first move, and commit and push.
3. Say, in the `conversation-language`:

    ```
    ● #{id} {sign-off name} ── approved → #{next id} {next task name}

      Say "go on", or /clear and then /rn:up.
    ```

   and stop.
