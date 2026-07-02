---
name: ty
description: Approve the pending rn confirmation — sign off whatever the assistant last asked the user to confirm (a plan, design, or evaluation gate, or a reviewed result) and advance the flow with no revision. Has side effects (continues the workflow) and is user-invoked — run only on explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

Approves the pending rn confirmation and advances the flow. Performs no revision.

## Steps

1. **Identify the pending approval.** Find the most recent approval / sign-off request — a scheduled gate (plan / design / evaluation) or a reviewed deliverable. Exclude weigh-in / escalation questions; those get answered, not approved here. State the identified target back. Proceed only if it is unambiguous; if more than one approval is plausibly pending, or it is unclear what is being approved, ask the user which before recording approval, opening that ask with the session-status block per `${CLAUDE_PLUGIN_ROOT}/references/status-display.md`.

2. **Record it as approved.** Register the pending confirmation as accepted.

3. **Advance the workflow.** Proceed from the approved point:
   - a plan or design gate passes — execution proceeds to the next task;
   - an evaluation gate passes — the session can close;
   - a reviewed item is accepted — it stands as final.

4. **Nothing pending.** If nothing is actually awaiting approval, say so and do nothing else.
