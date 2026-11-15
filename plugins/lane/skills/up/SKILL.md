---
name: up
description: Proposes the rules and routes that hold a plugin's skill and subagents to the steps and order you wrote, shows your steps as they'll read once laid, and lays them once you approve. Use when you type /lane:up <plugin>, or ask Lane to hold a plugin to its steps.
argument-hint: "<the plugin's folder>"
---

You're Lane's up in this conversation, for the plugin in "$ARGUMENTS". Lane's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/up.md`: read it whole first. It names `lay.py`, which is `${CLAUDE_PLUGIN_ROOT}/scripts/lay.py`, and `result.py`, which is `${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py`, each run by `python3`.

## Steps
