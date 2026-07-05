# Migration Workflow

Invoked by a command skill (`on`/`dn`/`up`/`ty`/`gm`) when the active session's `steering.md`
`Rn version:` line does not match the installed plugin's version — the skill's own version-check step
(a plain string comparison) is what triggers this file; this file only reconciles once triggered. Run
once per invocation.

Coordinator only: no implementation expert, and no QA/Design/Craft/Verification review, spawns for this
procedure itself — unlike the per-task review chain in
[`task-execute-workflow.md`](./task-execute-workflow.md) / [`task-verify-workflow.md`](./task-verify-workflow.md).
The coordinator reads each artifact, judges drift, and edits it directly.

## Steps

Reconcile the three artifacts below **in this order** — steering, then design, then tasks — since a
task's own drift can only be judged correctly once `steering.md`'s structure itself is current.

1. **Reconcile `steering.md` against [`steering-template.md`](./steering-template.md).** Compare the
   session's `steering.md` — its header block (`Rn version:` / `Design:`), and its `Goal` / `Acceptance
   criteria` / `Assumptions` / `Rules` / `Tasks` / `State` fields — against the current
   `steering-template.md`. Judge by reasoning what has drifted from current convention (a renamed or
   reshaped field, a since-added header line, a since-changed per-field rule) and edit `steering.md`
   directly to close it.

2. **Reconcile `design.md` against [`design-template.md`](./design-template.md), if the session has
   one.** Read the session's `steering.md` `Design:` line; if it is absent, the session has no
   `design.md` — skip this step entirely. If present, follow `design-template.md`'s own "Updating an
   existing design.md" procedure to bring the document current; that procedure (including its shape-
   migration case) is the reconciliation mechanism — do not re-derive reconciliation logic here.

3. **Reconcile each remaining task against `steering-template.md`'s "Task definition requirements"
   table.** For every unchecked task in `steering.md`'s `Tasks` section, judge its Purpose /
   Prerequisites / Steps / Completion criteria against each row of that table — Granularity,
   Specificity, Objectivity, Prerequisites, Criteria vs steps, Flat tasks, Done annotation — and edit
   the task directly to close any drift (e.g. a Completion criterion phrased as an action instead of an
   end-state, or a Steps list missing a review step the current Process selection section now requires).
   Leave every already-checked-off task untouched — reconciliation targets the forward-looking
   remainder, not the record of what already happened.

## No user gate; then stamp the version

Apply the reconciling edits from all three steps and commit them directly. This is not one of the three
scheduled gates (plan / design / evaluation) described in `task-verify-workflow.md`'s "Review gates",
and it does not go through per-task QA/Craft/Design review — it is a mechanical, no-gate procedure.
Once the reconciling edits are committed, update the session's `steering.md` `Rn version:` line to the
installed plugin's version — the last step, so the stamp only advances once the artifacts it certifies
are actually current.

## Comparison is always current-vs-current

Every comparison above asks one question only: does this artifact match what the **currently
installed** templates/workflows require, right now. This file never reads `CHANGELOG.md` and never
reasons about version ranges or deltas between the session's recorded version and the installed one —
the recorded version's only job is detecting *that* a mismatch exists (the per-skill check that
triggers this file); it plays no part in *what* gets reconciled. This holds regardless of which version
the session started from, so there is no per-version bookkeeping to maintain here.
