---
name: dn
description: Pause an rn session at any point, leave what the next conversation needs and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

## Role

The user can stop anywhere, even in the middle of working something out, and come back without
explaining anything again. The next conversation knows only the session's record, so everything
it needs is left there.

## Steps

1. Find the session as `${CLAUDE_PLUGIN_ROOT}/references/record.md` says. The last decision line
   ends `waiting for #{id} {sign-off name}` → say it is already stopped there, safe to clear, and
   that `/rn:ty` or `/rn:gm` answers it; end.
2. If turn is at work, stop it with Esc as its callers' page says, so its work stays in its evidence
   and nothing half-made reaches the task's files. Write what the next conversation needs and
   nothing else records to a `notes` item in `open/`: what was under way and how far it came, the
   task's content file and the last task handed to turn when a task was under way, and in a talk
   with the user, the points agreed and the point still open.
3. Commit and push, so nothing needed to go on is only on this machine, with the decision line
   `● {#id task name | plan | design} ── {how far it came} → paused at {#id task name | plan |
   design}`.
4. End, opening your message with the map as `${CLAUDE_PLUGIN_ROOT}/checklists/proposal.md` gives
   it, the task under way as `👉 #{id} {task name} ── paused here`, then the decision line, then
   `Next: /clear, then /rn:up.`, in the `conversation-language` of `steering.md`.
