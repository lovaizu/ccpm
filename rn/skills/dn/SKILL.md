---
name: dn
description: Pause an rn session at any point — leave what the next conversation needs and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

## Purpose

The user can stop anywhere, even in the middle of working something out, and come back without
explaining anything again. The next conversation knows only the session's record, so everything it
needs is left there.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. Write what the next conversation needs and nothing else records to a `notes` item in `open/`: what
   was under way, and in a talk with the user, the points agreed and the point still open.
3. Commit and push with the decision line `● paused ── → {what was under way}`.
4. Stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, with
   the task under way as:

   ```
   👉 #{id} {task name} ── stopped here; next: /rn:up
   ```
