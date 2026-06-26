---
name: gm
description: Register a revise verdict on the work under review — the counterpart to /rn:ty. With an argument, /rn:gm <text> takes <text> as the feedback and revises the pending item against it. With no argument, /rn:gm processes the current PR's review comments through the PR-feedback workflow. Has side effects (revises work, commits, pushes, replies on the PR) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Registers a revise verdict ("good, more") on the work under review. The feedback comes from `$ARGUMENTS` when present, otherwise from the current PR's review comments.

## Steps

1. **Branch on the argument.** If `$ARGUMENTS` is non-empty, it is the feedback — go to step 2. If empty, the feedback lives in the PR's review comments — go to step 3.

2. **With feedback (`$ARGUMENTS` present).** Treat `$ARGUMENTS` as a revise verdict on the pending item — the thing the assistant last presented for confirmation, or the work under review. Apply the revision, re-doing or redispatching the work as needed, then report. Do not enter the PR-feedback loop.

3. **From the PR (no argument).** Read `${CLAUDE_PLUGIN_ROOT}/references/pr-feedback-workflow.md` and run that loop against the current PR's review comments.

4. **Either way, this is a revise verdict** — the counterpart to `/rn:ty` (approve). It drops nothing: every piece of feedback is acted on.
