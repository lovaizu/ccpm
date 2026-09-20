---
name: gm
description: Ask rn to revise what it last presented — /rn:gm <text> revises against that feedback; plain /rn:gm takes the feedback from the session PR's unresolved review threads. Has side effects (revises, commits, pushes, replies on the PR) — run only on explicit /rn:gm.
disable-model-invocation: true
---

# /rn:gm — Revise

Records a revise verdict, the counterpart of `/rn:ty`. Every piece of feedback is acted on; none is
dropped.

## Steps

1. **Bring an older session current first, so the revision lands on the current shape.** Compare
   `Rn version:` with the installed version in `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`;
   on a mismatch run the migration section of `${CLAUDE_PLUGIN_ROOT}/references/steering.md`.

2. **Take the feedback from where the user put it, so text and PR comments are not confused.**
   `$ARGUMENTS` non-empty after trimming → it is the feedback; go to step 3. Empty → the feedback is
   on the PR; go to step 4.

3. **Revise the pending item against the text, then present it again.** The pending item is what
   was last presented for a decision; with nothing pending, treat the text as a direct instruction.
   Make the change through the task loop's implementer (`${CLAUDE_PLUGIN_ROOT}/references/task.md`
   step 1) when it touches the deliverable, or directly when it touches `steering.md`; have it
   judged again; re-present with the session-status block.

4. **Work every unresolved review thread, so nothing the reviewer wrote is lost.** Read the PR's
   review threads (`gh api graphql` on `reviewThreads`, paginated). For each thread that is
   unresolved and where the reviewer has the last word: address it, commit and push, and reply on
   that thread with what changed and the commit; or, when the ask is unclear, reply with the
   question and change nothing. Never resolve a thread — that is the reviewer's act. Report when
   the queue is empty, opening with the session-status block.
