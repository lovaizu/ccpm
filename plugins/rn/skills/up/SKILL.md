---
name: up
description: Makes what the user asks for so that the people it's for can use it, asking only the points that are the user's, or picks up a paused run. Use when the user types /rn:up, alone or with what they want.
argument-hint: "[what you want, in your own words]"
---

You're rn's orchestrator in this conversation. rn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole with the Read tool first, unless you've read it in this conversation, then carry out its steps of a new request where the words below hold one, and of a pick-up where they're empty, with the user's words below, word for word, empty where they typed the command alone:

$ARGUMENTS
