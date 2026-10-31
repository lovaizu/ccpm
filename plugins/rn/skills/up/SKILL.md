---
name: up
description: Takes a piece of work the user asks for in rough words with `/rn:up <what you want>` to a pull request marked ready, asking them only what is theirs to decide, one point per message, and stopping at the goal sign-off, the ux and the architecture sign-off where the work needs such a document, and the deliverable sign-off; with `/rn:up` alone, in this conversation or a fresh one, goes on with the session on the checked-out branch from where its steering stands. Runs only when the user types /rn:up, and from /rn:ty once a sign-off is approved.
disable-model-invocation: true
argument-hint: "[what you want]"
---

`rn.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run from the top of the repository.
`goal.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/goal.md`.
`ux.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/ux.md`.
`architecture.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/architecture.md`.
`build.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/build.md`.
`learnings.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/learnings.md`.
`messages.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/messages.md`.
`orchestrator.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md`.
`steering.json` below is `${CLAUDE_PLUGIN_ROOT}/forms/steering.json`, the steering's form.

Read `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md` whole first, and take its step 1 on the
user's words after `/rn:up`, which are "$ARGUMENTS".
