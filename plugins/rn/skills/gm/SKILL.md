---
name: gm
description: Keeps the feedback the user sends back on the proposal at an rn sign-off with `/rn:gm <feedback>`, and stops so the conversation can be cleared; the next `/rn:up` finds the point behind the feedback and acts on it. Runs only when the user types /rn:gm.
disable-model-invocation: true
argument-hint: "<feedback>"
---

`rn.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run from the top of the repository.
`goal.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/goal.md`.
`ux.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/ux.md`.
`architecture.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/architecture.md`.
`build.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/build.md`.
`learnings.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/learnings.md`.
`messages.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/messages.md`.
`orchestrator.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md`.

Read `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md` whole first, then
`${CLAUDE_PLUGIN_ROOT}/prompts/feedback.md` whole, and take its steps on the user's feedback
after `/rn:gm`, which is "$ARGUMENTS".
