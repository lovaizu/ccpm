---
name: up
description: Resume an rn session in a fresh conversation — bring an older session up to date, act on the user's recorded answer, and run the work to their next decision. It writes files, commits, pushes, and posts replies on the pull request, so run it only on an explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume

## Purpose

The session goes on from where the user left it, by the decisions they made, as if it had never
stopped, until their next decision.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, bringing it up to date if
   an earlier `rn` started it.
2. Say:

   ```
   ● Resuming {slug} at #{id}: {task name}
   ```

3. Set `status` to `running` and remove `paused_at`.
4. Go on as in After the user decides in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`.
