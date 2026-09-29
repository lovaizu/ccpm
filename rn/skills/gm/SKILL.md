---
name: gm
description: Give feedback on the sign-off an rn session is waiting for — the plan, the design, or the deliverable — from the words given, or from the review comments on the pull request; record it and stop, so the session goes back to before that sign-off. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

## Purpose

Feedback is a sign that the user and the session do not yet see the same thing, so the session goes
back to before the sign-off: the plan or the design is worked out again with the user, and the
deliverable gets tasks. The user's words are kept whole, since the work is answered and evaluated by
them, and a summary would shift that measure.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line is
   not `waiting for #{id} {sign-off name}` → say what the session is doing, and stop.
2. The feedback is `$ARGUMENTS`; without it, the pull request's review threads whose last comment is
   the user's, each with its location and URL. Write it to a `feedback` item in `open/`.
3. Commit and push with the decision line
   `● #{id} {sign-off name} ── feedback → {work out the plan again | work out the design again | add tasks}`,
   and say, everything in braces in the user's language:

   ```
   ● {took the feedback on the plan, the design, or the deliverable}. {next: say "go on", or /clear and /rn:up}
   ```

4. When the user says to go on, go on as `/rn:up` does.
