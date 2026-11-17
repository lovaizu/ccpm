---
name: gm
description: Sends back what rn put up for your sign-off, with what to change or alone to have rn read your comments on the pull request, so that rn changes the decisions it comes from. Use when the person types /rn:gm.
argument-hint: "[what to change, in your own words]"
disable-model-invocation: true
---

The person typed /rn:gm to send the sign-off waiting back. As `rn`'s orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation. Their words follow word for word, empty where they typed the command alone:

$ARGUMENTS

## Steps

1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py send-back`, which keeps the sign-off waiting sent back and prints it. Only the person's typed /rn:gm sends a sign-off back, so this is the one moment you run it.
2. Where they typed the command with no words, read what they want changed by `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py comments`, which prints their comments on the pull request since you put the sign-off up.
3. Judge each thing they want by the purpose and the best practices, for the decision it changes, and have the tree-keeper write each such decision, with their words word for word, as your part's step 2 says, so that the rounds start again from the design. Then go on by your part's steps.
