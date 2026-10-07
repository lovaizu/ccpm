---
name: gm
description: Give feedback on the sign-off an rn session is waiting for — the plan, the design, or the deliverable — from the words given, or from the user's comments on the pull request; record it and stop, so the session goes back to before that sign-off. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

## Purpose

Feedback is a sign that the user and the session do not yet see the same thing, so the session goes
back to before the sign-off and works out again what the feedback shows they do not yet share. The
user's words are kept whole, since the work is measured by them, and a summary would shift that
measure.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The last decision line does
   not end `waiting for #{id} {sign-off name}` → say what the session is doing, and stop.
2. The feedback is `$ARGUMENTS`; without it, every comment the `gh` user wrote on the pull request
   after that stop commit, on a line or on the whole, each with its place and URL. Neither → ask the
   user for their feedback, and stop. Write it whole, in their words, to a `feedback` item in `open/`.
3. Commit and push with the decision line
   `● #{id} {sign-off name} ── feedback in {file} → {working out the plan or the design again, or tasks for it}`,
   and say, in the `conversation-language` of `steering.md`, translating the line below:

   ```
   {the decision line}

   Say "go on", or /clear and then /rn:up.
   ```

4. When the user says to go on, go on as `${CLAUDE_PLUGIN_ROOT}/skills/up/SKILL.md` says, from its
   third step.
