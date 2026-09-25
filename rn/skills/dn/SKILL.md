---
name: dn
description: Pause an rn session in the middle of the work — record where it stands in steering.md and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

## Purpose

The user can stop in the middle of the work and come back without explaining anything again. The next
conversation knows only `steering.md` and git, so everything it needs is left there, and nothing else.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. Write what the next conversation needs in `Notes`.
3. Commit and push.
4. Stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`:

   ```
   👉 {#id task name} ── stopped here; next: /clear, then /rn:up
   ```
