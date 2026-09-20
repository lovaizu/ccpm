---
name: ty
description: Approve the pending rn confirmation — sign off whatever was last presented (plan, design, or evaluation gate, or a reviewed result) and advance. Has side effects (continues the workflow) — run only on explicit /rn:ty.
disable-model-invocation: true
---

# /rn:ty — Approve

Approves the pending confirmation and advances. No revision.

## Steps

1. **Check the version, so approval lands on a current session.** Compare `steering.md`'s
   `Rn version:` to the installed version; on mismatch, run the migration section of
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md` first.

2. **Identify what's pending, so the right thing gets approved.** Find the most recent gate or
   reviewed item awaiting sign-off. If more than one is plausible, ask which, opening with the
   status block.

3. **Record it approved, so the workflow has a fact to advance from.** Mark the pending item as
   approved.

4. **Advance from the approved point.** Plan or design gate → check the task off, continue the task
   loop at the next unchecked task per `${CLAUDE_PLUGIN_ROOT}/references/task.md`. Evaluation gate →
   check the task off; the session closes; open the closing report with the status block. Nothing
   pending → say so, opening with the status block, and stop.
