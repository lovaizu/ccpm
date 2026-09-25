---
name: ty
description: Approve the decision an rn session stopped for — the plan, a design choice, or the finished work — record it, and stop. It commits, pushes, and at the last sign-off marks the pull request ready, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

The user approves what the session stopped for. Record it in `steering.md`, so the work goes on from
there without asking again, and stop.

Find the session as in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. Check the sign-off at `Next`
and set `Next` past it. At a Design sign-off, record the choice — the one `$ARGUMENTS` names, or your
recommendation — as a Fact in `Assumptions`. At the Evaluation sign-off, the session ends: remove
`evaluations/` and mark the pull request ready with `gh pr ready`. Commit and push.

Then say, in the user's language:

```
● Approved: {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
```

At the Evaluation sign-off, say instead that the session is finished, that the merge is theirs, and
what `Notes` says waits on it.
