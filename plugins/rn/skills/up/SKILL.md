---
name: up
description: Makes what you ask for, such as a document, code, or a plugin, so that the people it's for can use it, asking you only the points that are yours, or picks up a paused run. Use when the person types /rn:up with what they want, or alone to pick up, or asks rn to make something.
argument-hint: "[what you want, in your own words]"
---

You're `rn`'s orchestrator in this conversation, for the request "$ARGUMENTS", which is empty where the person picks up a paused run. `rn`'s folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first. It names `tree.py` and `record.py`, which are `${CLAUDE_PLUGIN_ROOT}/scripts/tree.py` and `${CLAUDE_PLUGIN_ROOT}/scripts/record.py`, each run by `python3`. It holds the steps that every moment of the run shares, and the steps below are those of the run's start or pick-up.

## Steps
