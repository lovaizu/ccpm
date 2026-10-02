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

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line is
   `waiting for #{id} {sign-off name}` → say it is already stopped there, safe to clear, and that
   `/rn:ty` or `/rn:gm` answers it; stop.
2. Write what the next conversation needs and nothing else records to a `notes` item in `open/`: what
   was under way, and in a talk with the user, the points agreed and the point still open.
3. Commit and push, with an unfinished task's edits in the working tree beside the item, so nothing
   needed to resume is only on this machine, with the decision line `● {#id task name | plan | design} ── {paused} → {/rn:up}`.
4. Stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, with
   the task under way as:

   ```
   👉 #{id} {task name} ── {stopped here; next: /rn:up}
   ```

   The decision line is in the `artifact-language` of `steering.md`, and what you say in its
   `conversation-language`.
