---
name: up
description: Makes what you ask for, such as a document, code, or a plugin, so that the people it's for can use it for what they're after, asking you only the points that are yours, one at a time, and picks the work up where it stopped. Use when the person types /rn:up, or asks rn to make, go on with, or change a piece of work.
argument-hint: "<what you want, in your own words, or nothing to pick up where rn stopped>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py *)
---

You're rn's orchestrator in this conversation, for the request "$ARGUMENTS". rn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/up.md`: read it whole first, and then carry it out for the request.
