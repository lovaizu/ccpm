---
name: gm
description: Ask for changes to what an rn session stopped for — the plan, a design choice, or the finished work — from the feedback given, or from the review comments on the pull request; revise the session by it and stop. It commits and pushes, so run it only on an explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Good, more

## Purpose

The session is revised by what the user asks for as soon as they ask, so `steering.md` always says
what comes next. Their words are kept whole: the evaluator checks the revision by them, and a summary
would shift that measure.

## Steps

1. Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The first task not `[x]` is
   not a sign-off → say what the session is doing, and stop.
2. The feedback is `$ARGUMENTS`; without it, the unresolved review threads on the pull request, each
   with its location and URL. Add it to `Feedback`.
3. Revise by it: at the Plan sign-off the plan, at a Design sign-off the choices, at the Evaluation
   sign-off tasks added before it that answer it.
4. Commit, push, and say in the user's language:

   ```
   ● Revised: {n} points on {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
   ```

5. When the user says to go on, go on as `/rn:up` does.
