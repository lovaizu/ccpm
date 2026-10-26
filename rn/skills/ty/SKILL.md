---
name: ty
description: Approves the proposal the user is shown at an rn sign-off, the plan's, the design's or the deliverable's, when they type `/rn:ty`; keeps the approval on the session's branch and goes on with the work. Runs only when the user types /rn:ty.
disable-model-invocation: true
---

`rn.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"`, run from the top of the repository.
`plan.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/plan.md`.
`design.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/design.md`.
`build.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/build.md`.
`learnings.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/learnings.md`.
`messages.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/messages.md`.
`orchestrator.md` below is `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md`.

Read `${CLAUDE_PLUGIN_ROOT}/prompts/orchestrator.md` whole first, then
`${CLAUDE_PLUGIN_ROOT}/prompts/approval.md` whole, and take its steps on the user's `/rn:ty`.
