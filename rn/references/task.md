# Task loop

Runs one task from `steering.md`. Read by `on` and `up` wherever they hand off to "the task loop",
and re-entered by `/rn:ty` once a gate is approved.

## Steps

1. **Build the deliverable as its owner would state it, so the work aims at the purpose, not a
   recipe.** Dispatch `Agent` with `model: sonnet`, carrying the Goal one-liner, this task's
   Purpose / Steps / Completion criteria verbatim, the Rules, and the files in play. It stages paths
   explicitly, commits with a plain conventional message (never containing `complete task #`),
   pushes, and returns what changed and the commit SHA(s). The coordinator never edits the
   deliverable itself — only `steering.md`. "Evaluation sign-off" skips this step: it builds
   nothing, it judges what already exists.

2. **Have the result judged by someone other than its author.** Run
   `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` — kind Design for a "Design sign-off" task, kind
   Deliverable for any other build task, kind Session for "Evaluation sign-off" (against the real,
   finished artifacts). Post the verdict on the PR. NG → back to step 1 with the findings; three NG
   rounds on the same task → stop and ask the user, opening with the status block.

3. **At an ordinary task, check it off once judged OK, so a fresh conversation reads it as done.**
   Check the task's steps off in `steering.md`; commit `<type>: complete task #N — <name>`; push; go
   to step 5.

4. **At a gate task ("Design sign-off", "Evaluation sign-off"), stop instead of checking off.**
   Present the judged artifact with the status block and wait. `/rn:ty` records the approval, checks
   the task off, and resumes this loop at the next unchecked task; `/rn:gm` sends it back to step 1
   with the feedback.

5. **Otherwise, move straight to the next unchecked task.** Nothing here waits on the user unless it
   is genuinely theirs to decide — a discovery that would change the agreed plan or design is raised
   at once (status block), never held for a gate.

Judgment and execution run on different models: the implementer (step 1) is dispatched with
`model: sonnet`; the evaluator (step 2) is dispatched with `model: opus`.
