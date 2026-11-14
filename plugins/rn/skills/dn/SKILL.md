---
name: dn
description: Pauses rn's run, with its work so far committed and pushed and each role's step kept, so that /rn:up picks it up in any conversation. Use when the user types /rn:dn.
disable-model-invocation: true
---

The user typed /rn:dn to pause the run. As rn's orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation. You run tree.py as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py`.

## Steps

The steps aren't written yet. They take the moves of S4 of rn's architecture: each role still running stopped, its work committed with the step it stood at, the work pushed, and `Paused`.
