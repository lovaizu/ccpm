# Task loop

Runs the tasks in `steering.md` one at a time: build, judge, check off, next. Entered from `/rn:on`
and `/rn:ty` after the plan gate, and from `/rn:up` on resume.

## Roles

- **Conductor** — the agent in the conversation, per
  `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`; read it here if it is not in this conversation.
- **Implementer** — `Agent`, `model: sonnet`, no conversation history. Builds one task.
- **Evaluator** — `Agent`, `model: opus`, no conversation history. Judges one artifact per
  `evaluate.md`.

## Steps

1. **Hand the task to the implementer as its owner would state it, so the work aims at the
   Objective rather than at a recipe.** Dispatch the implementer carrying: the Goal in one line;
   this task's Objective, Steps and Success criteria verbatim; the Rules; the files in play; what
   the session has learned that bears on this task; and that it returns what changed and the
   commit SHA(s). For a "Design sign-off" task the deliverable is the approach, written at the
   path the `Design:` line names. "Evaluation sign-off" skips this step: nothing is built, the
   finished work is judged.

2. **Read the result before anyone else does, so the evaluator and the user see only work that
   could be complete.** Check it on the thing itself against the task's Success criteria and the
   Rules. A miss the conductor can see goes straight back to the implementer with what is missing;
   only then does it go on.

3. **Have the result judged by someone other than its author, so a pass means it does its job.**
   Run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` — kind Deliverable for an ordinary task, kind
   Design for "Design sign-off", kind Session for "Evaluation sign-off". NG → step 1 again with the
   findings; a Session NG names finished work that fails a criterion, so it becomes a task added
   before "Evaluation sign-off" in step 4, and the loop continues from that task. After three NG
   rounds on one task, stop and ask the user, showing the last verdict; the count starts again
   from the answer.

4. **Fold what was learned into `steering.md`, so the plan stays true and the next task starts
   from it.** After every result and every evaluation: an Assumption that proved false is corrected;
   a finding that came back once becomes a Rule; a task the work uncovered is added, one made
   unnecessary is removed; the `Design:` line names the design once it exists; a limit the user
   accepted at a gate becomes an Assumption, so the next evaluator judges against it instead of
   being told to excuse it. Commit with the task's work. A change to the Goal, the Success criteria or an approved design is the user's —
   raise it at once; never hold it for a gate.

5. **For an ordinary task, record completion where a fresh conversation will read it, then move
   on — the user is not asked what is not theirs to decide.** Check the task off per Checking a
   task off in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, commit and push. Then the next
   unchecked task.

6. **For a gate task, stop — the decision is the user's.** `Pending` already names the gate, the
   commit judged and the verdict's URL from the round that cleared it. Present the judged artifact
   and the evaluator's verdict and wait.
   `/rn:ty` checks the task off and continues with the next unchecked task; `/rn:gm` returns to
   step 1 with the feedback.
