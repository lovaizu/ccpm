---
name: ty
description: Approve the decision an rn session stopped for — the plan, a design choice, or the finished work — record it, and stop. It commits, pushes, and at the last sign-off marks the pull request ready, so run it only on an explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

The user has read what the session stopped for and approves it. Record the approval where a later
conversation will find it, so the work goes on from here without asking again.

Find the session as in Finding the session in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. The task
at `Next` must be a sign-off task waiting for the user; if it is not, say what the session is doing
instead, and stop.

Mark its step `[x]`. When `Feedback` holds a revision, the user has now approved past it: set it to
none. Then set `Next`:

- Plan sign-off → the task after it.
- Design sign-off → the tasks that follow from the choice are to be written. The choice is the one
  `$ARGUMENTS` names, or your recommendation when it names none; write it in `Assumptions` as a Fact
  the user chose at this sign-off.
- Evaluation sign-off → the session ends. Remove its `evaluations/`: they served the decisions made
  along the way, and this approval is the last of them. Mark the pull request ready with
  `gh pr ready`.

Commit everything the approval changed and push. Then stop, and say in the user's language what was
approved and how the work goes on:

```
● Approved: {sign-off name}. Next: /clear, then /rn:up — or say "go on" to continue here.
```

At the Evaluation sign-off, say instead that the session is finished, that the merge is the user's,
and what `Notes` says waits on the merge.

When the user says to go on here, run the session as `/rn:up` does.
