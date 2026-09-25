---
name: dn
description: Pause an rn session — record where it stands in steering.md and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

## Purpose

The user can come back to the session without explaining anything again. The next conversation knows
only `steering.md` and git, so everything it needs is left there, and nothing else.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.
2. Write where it stands in `State`; set `status` to `paused` and `paused_at` to today.
3. Remove the session's scratch, commit, and push.
4. Stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`:

   ```
   👉 {#id task name} ── stopped here; next: /clear, then /rn:up
   ```
