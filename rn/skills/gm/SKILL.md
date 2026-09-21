---
name: gm
description: Ask rn to revise what it last presented — /rn:gm <text> revises against that feedback; plain /rn:gm takes the feedback from the session PR's unresolved review threads. Has side effects (revises, commits, pushes, replies on the PR) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Records a revise verdict, the counterpart of `/rn:ty`. Every piece of feedback is acted on; none is
dropped.

## Steps

1. **Take up the conductor's role and enter the session.** Read
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, then run Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

2. **Take the feedback from where the user put it, so text and PR comments are not confused.**
   `$ARGUMENTS` non-empty after trimming → it is the feedback; go to step 3. Empty → the feedback is
   on the PR; go to step 4. Empty and the session has no PR → say so and stop: the feedback comes
   as `/rn:gm <text>`.

3. **Revise the pending item against the feedback, then present it again.** The pending item is
   what was last presented for a decision; with nothing pending, treat the feedback as a direct
   instruction. Think from what the feedback is for, not from its wording, and apply the same lens
   to the whole artifact, not only the line named. A change to the deliverable goes through the
   task loop (`${CLAUDE_PLUGIN_ROOT}/references/task.md`, from step 1). A change to `steering.md`
   is the conductor's to write — the feedback is the user's word, so the Goal and the Success
   criteria may move with it — and is then judged per Judging the plan in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`. Re-present with the session-status block.

4. **Work every unresolved review thread, so nothing the reviewer wrote is lost.** The reviewer
   on the session PR is the user. Read the PR's review threads (`gh api graphql` on
   `reviewThreads`, paginated). For each thread that is unresolved and where the reviewer has the
   last word: address it as in step 3, commit and push, and reply on that thread with what changed
   and the commit; or, when the ask is unclear, reply with one question only the reviewer can
   answer, with a recommendation, and change nothing. Never resolve a thread — that is the
   reviewer's act. Report when the queue is empty, opening with the session-status block.
