---
name: ty
description: Approves the plan, a deliverable, a lesson for rn's repository, or the pull request handed over at Done, that rn put up for the user's sign-off and that waits for it. Use when the user types /rn:ty.
disable-model-invocation: true
---

The user typed /rn:ty to approve the sign-off waiting. tree.py recorded their approval as this command loaded, and opened the issue where the sign-off is a lesson:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py approve`

As rn's orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation.

## Steps

The steps aren't written yet. They take the moves of S3 of rn's architecture after the user approves, and of S6 after they approve a lesson or the pull request handed over.
