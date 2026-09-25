---
name: dn
description: Pause an rn session — record where it stands in steering.md and push everything, so a fresh conversation picks it up with /rn:up. It commits and pushes, so run it only on an explicit /rn:dn.
disable-model-invocation: true
---

# /rn:dn — Pause

The conversation is about to end: the context is nearly full, or the user is done for now. The next
conversation will know only `steering.md` and git, so everything it needs to go on must be there when
this one ends.

Find the session as in Finding the session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. An
agent the session started that is still running would change the repository after the pause: wait for
it to return. An evaluation it wrote is part of the session: commit it.

Write in `State` where the session stands: `Next`, the first task not yet complete and how far it got —
its work done but not yet evaluated, with the commits, or evaluated but not yet decided on, or sent back
to retry, with the evaluation; `Feedback`, as it is; `Notes`, what this conversation knows that the next
one needs and nothing else records. Set `status` to `paused` and `paused_at` to today.

Commit the work in progress and push, so nothing is left only on this machine. Files the session made
that are not part of the work are its scratch: remove them. A file you cannot place is the user's to
decide: show it to them and wait.

Then stop. Open your message with the session's map, as in Stopping for the user in
`${CLAUDE_PLUGIN_ROOT}/references/turn.md`, with 👉 at the task the session stopped at and what
comes next:

```
👉 #{id}      {task name} ── stopped here; next: /clear, then /rn:up
```
