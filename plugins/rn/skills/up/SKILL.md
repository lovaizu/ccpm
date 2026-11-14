---
name: up
description: Makes what the user asks for, such as a document, code, or a plugin, so that the people it's for can use it for what they're after, asks the user only the points that are theirs, and leaves one pull request for them to merge. Use when the user types /rn:up with what they want, in their own words, or /rn:up alone to go on with a run that stopped. Not for a one-line fix that Claude Code makes at once, and not for approving or sending back what rn put up, which /rn:ty and /rn:gm do.
argument-hint: "[what you want, in your own words]"
allowed-tools: Read, Write, Bash, Agent, SendMessage, TaskStop, EnterWorktree
---

You're rn's orchestrator in this conversation, for the request "$ARGUMENTS". rn's folder is `${CLAUDE_PLUGIN_ROOT}`. Your part is in `${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md`: read it whole first. It holds the steps that every moment of the run shares, and the steps below are those of the moment when the user types `/rn:up`. You run tree.py as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tree.py`, and rn's best practices lie in `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/`.

## Steps

The steps aren't written yet. With a request, they take the moves of S1 of rn's architecture up to the goal confirmed and the plan put to the user. Alone, they take the moves of S5: the runs left, which one to pick up, the run's worktree entered, and `Picking up`, or, where no run is left, the skill's result `none` and that no run is left to pick up, with no role started.
