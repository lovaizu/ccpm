---
name: gm
description: Ask rn to revise what it last presented — /rn:gm <text> revises against that feedback; plain /rn:gm takes the feedback from the session PR's unresolved review threads. Has side effects (revises, commits, pushes, replies on the PR) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Records a revise verdict, the counterpart of `/rn:ty`. Every piece of feedback is acted on; none is
dropped.

## Steps

1. **Take up the conductor's role, so someone works toward the Goal from this command's first
   step.** Read `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`; what follows runs under it.

2. **Bring an older session current first, so the revision lands on the current shape.** Compare
   `Rn version:` with the installed version in `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`;
   on a mismatch run the migration section of `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

3. **Take the feedback from where the user put it, so text and PR comments are not confused.**
   `$ARGUMENTS` non-empty after trimming → it is the feedback; go to step 4. Empty → the feedback is
   on the PR; go to step 5. Empty and the session has no PR → say so and stop: the feedback comes
   as `/rn:gm <text>`.

4. **Revise the pending item against the text, then present it again.** The pending item is what
   was last presented for a decision; with nothing pending, treat the text as a direct instruction.
   Think from what the feedback is for, not from its wording: a change to the deliverable goes
   through the task loop (`${CLAUDE_PLUGIN_ROOT}/references/task.md`, from step 1), a change to
   `steering.md` is the conductor's own; the same lens is applied to the whole artifact, not only
   the line named. A fact or number changes only on evidence, never to match the feedback.
   Feedback that repeats a finding already made becomes a Rule in `steering.md`. Read the revised
   thing itself before it goes on; have it judged again; re-present with the session-status block.

5. **Work every unresolved review thread, so nothing the reviewer wrote is lost.** Read the PR's
   review threads (`gh api graphql` on `reviewThreads`, paginated). For each thread that is
   unresolved and where the reviewer has the last word: address it as in step 4, commit and push,
   and reply on that thread with what changed and the commit; or, when the ask is unclear, reply
   with one question only the reviewer can answer, with a recommendation, and change nothing. Never resolve a thread — that is the reviewer's act.
   Report when the queue is empty, opening with the session-status block.
