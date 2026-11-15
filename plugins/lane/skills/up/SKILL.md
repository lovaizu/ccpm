---
name: up
description: Proposes the rules and routes that hold a Claude Code plugin's skill and subagents to the numbered steps and order its builder wrote, shows the steps as they'll read once laid, and lays them once the caller approves. Use when the person types /lane:up <plugin>, or asks to have Lane hold a plugin to its steps, or to lay Lane's rules again after the steps or Lane changed.
argument-hint: "<the plugin's folder>"
---

You're Lane's up in this conversation, for the plugin in "$ARGUMENTS". Lane's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/up.md`: read it whole first. It names `lay.py`, which is `${CLAUDE_PLUGIN_ROOT}/scripts/lay.py`, and `result.py`, which is `${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py`, each run by `python3`.

## Steps

1. Take the caller: the person, where they typed `/lane:up`, or yourself, an AI, where you called this skill by the Skill tool, as no person's reply comes in a run you called.
2. Carry out your part's steps for the plugin.
