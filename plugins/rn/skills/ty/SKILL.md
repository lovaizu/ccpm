---
name: ty
description: Approves what rn put up for your sign-off, the plan, a deliverable, a lesson, or the pull request handed over, so that the work resting on it goes on. Use when the person types /rn:ty.
disable-model-invocation: true
---

The person typed /rn:ty to approve the sign-off waiting. As `rn`'s orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation.

## Steps

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py approve`, which keeps the sign-off waiting signed off and prints it. Only the person's typed /rn:ty approves, so this is the one moment you run it.
2. Plan the rest again from what the person signed off, and have the tree-keeper write the sign-off with the plan where it changed, as your part's step 2 says, so that `tree.py` marks doing each deliverable whose turn it gave. Then go on by your part's steps.
