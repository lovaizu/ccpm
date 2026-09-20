# Task loop

Runs the tasks in `steering.md` one at a time: build, judge, check off, next. Entered from `/rn:on`
and `/rn:ty` after the plan gate, and from `/rn:up` on resume.

Judgment and execution run on different models: the implementer is dispatched with
`model: sonnet`, the evaluator (`evaluate.md`) with `model: opus`. The coordinator in the
conversation plans, dispatches, and writes `steering.md`; it never edits the deliverable itself.

## Steps

1. **Hand the task to the implementer as its owner would state it, so the work aims at the
   purpose rather than at a recipe.** Dispatch `Agent` with `model: sonnet` carrying: the Goal in one
   line; this task's Purpose, Steps, and Completion criteria verbatim; the Rules; the files in play;
   and the commit convention — stage paths explicitly (never `git add -A`), a plain conventional
   message that does not contain `complete task #`, push, return what changed and the commit
   SHA(s). For a "Design sign-off" task the deliverable is the approach, written where it belongs in
   the project. "Evaluation sign-off" skips this step: nothing is built, the finished work is judged.

2. **Have the result judged by someone other than its author, so a pass means it does its job.**
   Run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` — kind Deliverable for an ordinary task, kind
   Design for "Design sign-off", kind Session for "Evaluation sign-off". NG → dispatch the
   implementer again with the evaluator's findings, then judge again. After three NG rounds on one
   task, stop and ask the user, opening with the session-status block.

3. **For an ordinary task, record completion where a fresh conversation will read it.** Check the
   task and its steps off in `steering.md`; commit `<type>: complete task #N — <name>`; push. This
   is the one commit that carries the marker.

4. **For a gate task, stop — the decision is the user's.** Present the judged artifact and the
   evaluator's verdict with the session-status block and wait. `/rn:ty` checks the task off and
   continues; `/rn:gm` returns to step 1 with the feedback.

5. **Move straight to the next unchecked task, so the user is not asked what is not theirs to
   decide.** Only a discovery that would change the agreed plan or design interrupts — raise it at
   once with the session-status block, never hold it for a gate.
