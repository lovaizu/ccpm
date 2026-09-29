---
name: up
description: Resume an rn session in a fresh conversation — bring a session started under an older rn to the current form, or take up where the last one stopped, and carry the work to the next sign-off. It writes files, commits, and pushes, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

## Purpose

The session goes on from where the user left it, by what its record says, as if it had never
stopped, until the next sign-off.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. When an older `rn` started
   it, bring it to the current form as there instead of the steps below.
2. Say where it resumes, naming the first task not `[x]`, or the next move of the last decision line
   when none is left:

   ```
   ● Resuming {slug} at #{id}: {task name}
   ```

3. When the last decision line is `waiting for #{id} {sign-off name}`, give the review request again
   from that commit's message, and stop. Otherwise take up the session as in
   `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`.
