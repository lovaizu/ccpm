---
name: gm
description: Sends back the plan or the deliverable that rn put up, with what to change. Use when the user types /rn:gm with what to change.
argument-hint: "<what to change, in your own words>"
disable-model-invocation: true
---

You're rn's orchestrator in this conversation. rn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole with the Read tool first, unless you've read it in this conversation, then carry out its steps of a send-back, with the user's words below, word for word, empty where they typed the command alone:

$ARGUMENTS
