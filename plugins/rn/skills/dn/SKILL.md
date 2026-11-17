---
name: dn
description: Pauses rn's run, stopping each role and committing and pushing its work so far, so that /rn:up in any conversation goes on where it stopped. Use when the person types /rn:dn.
disable-model-invocation: true
---

The person typed /rn:dn to pause the run. As `rn`'s orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation.

## Steps

1. Stop each role still running by TaskStop, as a role that goes on after the pause changes the work after it's pushed. Note each one's record and the step it stood in, the one after the last step its record holds.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py pause` with `{"stood": [{"record": <path>, "step": <number>}]}` on standard input, naming each role you stopped and your own record, which `tree.py runs` names where this conversation hasn't, at the step you stand in. It writes where each stood, commits the work, and pushes it, so that `/rn:up` in any conversation goes on from there.
3. Show the pause as the README does: `Paused "<goal>" while making "<deliverable>".`, then `Its work so far is pushed. Type /rn:up in any conversation to go on.`, with the point or sign-off waiting. Where `tree.py pause` gives 1, say in place of the second line that the work is committed but not pushed, and what it names as missing.
