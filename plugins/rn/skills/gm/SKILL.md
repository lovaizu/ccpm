---
name: gm
description: Sends back what rn put up for the user's sign-off and waits for it, with what to change, or alone to have rn read the user's comments on the pull request. Use when the user types /rn:gm, with or without their words.
argument-hint: "[what to change, in your own words]"
disable-model-invocation: true
---

The user typed /rn:gm to send the sign-off waiting back. tree.py recorded it as this command loaded, and dropped the lesson where the sign-off is one:

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py send-back`

As rn's orchestrator, carry out the steps below, with your part in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`, which you read whole first unless you've read it in this conversation. Their words follow word for word, empty where they typed the command alone:

$ARGUMENTS

## Steps

The steps aren't written yet. They take the moves of S3 of rn's architecture after the user sends a sign-off back, and of S6 after they send back a lesson or the pull request handed over.
