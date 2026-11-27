---
name: gm
description: Asks rn to change what the user tried, in their words. Use when the user types /rn:gm with what to change.
argument-hint: "<what to change, in your own words>"
disable-model-invocation: true
---

You're rn's orchestrator in this conversation. rn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole with the Read tool first, unless you've read it in this conversation, then carry it out for `/rn:gm`, with the user's words below, word for word, empty where they typed the command alone:

$ARGUMENTS
