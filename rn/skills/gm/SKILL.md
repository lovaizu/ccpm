---
name: gm
description: Ask for changes to what an rn session stopped for — the plan, a design, or the finished work — from the feedback given, or from the review comments on the pull request; revise the session by it, have the revision evaluated, and stop. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

## Purpose

The session is revised by what the user asks for as soon as they ask, and stops again for their
answer, so they can clear their conversation: `steering.md` says what comes next. Their words are
kept whole, since the evaluator evaluates the revision by them, and a summary would shift that
measure.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The first task not `[x]` is
   not a sign-off → say what the session is doing, and stop.
2. The feedback is `$ARGUMENTS`; without it, the pull request's review threads whose last comment is
   the user's, each with its location and URL.
3. Add it to `Feedback` and revise what the sign-off decides on by it, in the shape
   `${CLAUDE_PLUGIN_ROOT}/references/conduct.md` gives it: the plan, the design documents, or, for the
   finished work, tasks added before its sign-off. Reply on each pull request thread it came from with what
   changed and the commit, in the comment's language, leaving resolving it to the user.
4. At the Plan or a Design sign-off, take the turn as in `${CLAUDE_PLUGIN_ROOT}/references/conduct.md`:
   it stops at the same sign-off. At the Finished work sign-off, commit, push, and say in the user's
   language:

   ```
   ● Revised: {n} points on {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```

5. When the user says to go on, go on as `/rn:up` does.
