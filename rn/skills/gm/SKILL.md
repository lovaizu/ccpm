---
name: gm
description: Ask for changes to what an rn session stopped for — the plan, a design choice, or the finished work — from the feedback given, or from the review comments on the pull request; record it and stop. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

The user has read what the session stopped for and wants more from it. Record their feedback where
a later conversation will find it, whole and in their words, so the revision answers what they asked
and not a summary of it.

Find the session as in Finding the session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The task
at `Next` must be a sign-off task waiting for the user; if it is not, say what the session is doing
instead, and stop.

The feedback is `$ARGUMENTS`. When it is empty, it is the unresolved review threads on the session's
pull request: for each, its location, its URL, and what it asks, read with `gh`. None there either →
ask the user what they want changed, and stop.

Write it into `Feedback`, next to anything already there. Commit `steering.md` and push. Then stop,
and say in the user's language what was recorded:

```
● Recorded: {n} points on {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
```

When the user says to go on here, run the session as `/rn:up` does.
