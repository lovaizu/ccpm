---
name: dn
description: Pauses rn's run where it stands, keeping all the work so far, so that /rn:up picks it up in any conversation. Use when the person types /rn:dn.
disable-model-invocation: true
---

The person typed /rn:dn to pause the run. As rn's orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation.

## Steps

1. Stop each generator and evaluator that runs, since its Round starts again from its Cut on the
   pick-up.
2. Commit the run's folder by `tree.py commit`, as step 4 of your part says, and push the run's
   branch, so that a pick-up in any conversation finds all the work so far.
3. Tell the person where the run stopped, the point or sign-off waiting, and that `/rn:up` with no
   words picks it up.
