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
2. Say, naming the first task not `[x]`:

   ```
   ● Resuming {slug} at #{id}: {task name}
   ```

3. Take up the session as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`. When it is waiting for a
   sign-off, give the review request again and stop.
