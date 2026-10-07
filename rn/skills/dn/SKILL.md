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

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line ends
   `waiting for #{id} {sign-off name}` → say, in the `conversation-language` of `steering.md`, that
   it is already stopped there, safe to clear, and that `/rn:ty` or `/rn:gm` answers it; stop.
2. Write what the next conversation needs and nothing else records to a `notes` item in `open/`: what
   was under way and how far it came, and in a talk with the user, the points agreed and the point
   still open. Uncommitted edits while a task is under way are that task's, made by its generator
   even when the pause stopped it before it returned: name the task, what its generator was sent to
   do, and that the edits are not yet checked.
3. Commit and push, with an unfinished task's edits beside the item, so nothing needed to go on is only
   on this machine, with the decision line
   `● {#id task name | plan | design} ── {how far it came} → paused at {#id task name | plan | design}`.
4. Stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`, the
   point paused at as `👉 {#id task name | plan | design} ── paused here`, then the decision line, then
   `Next: /clear, then /rn:up.`, in the `conversation-language` of `steering.md`.
