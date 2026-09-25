---
name: dn
description: Pause an rn session — record where it stands in steering.md and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

The conversation is about to end. The next one knows only `steering.md` and git, so leave there
everything it needs to go on, and nothing else.

Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. Write where it stands in
`State`, set `status` to `paused` with `paused_at`, commit and push, and leave no scratch behind.
Then stop, opening your message with the map as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`:

```
👉 {#id task name} ── stopped here; next: /clear, then /rn:up
```
