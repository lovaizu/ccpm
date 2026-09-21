# Task loop

Runs the tasks in `steering.md` one at a time: build, judge, check off, next. Entered from `/rn:on`
and `/rn:ty` after the plan gate, and from `/rn:up` on resume.

## Roles

- **Conductor** — the agent in the conversation. This loop runs under the role in
  `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`, taken up by the command that entered it; read
  it again here if it is not in this conversation.
- **Implementer** — `Agent`, `model: sonnet`, no conversation history. Builds one task.
- **Evaluator** — `Agent`, `model: opus`, no conversation history. Judges one artifact per
  `evaluate.md`.

Judgment and execution run on different models; the `model` parameter is where the split is
enforced.

## Steps

1. **Hand the task to the implementer as its owner would state it, so the work aims at the
   Objective rather than at a recipe.** Dispatch the implementer carrying: the Goal in one line;
   this task's Objective, Steps and Success criteria verbatim; the Rules; the files in play; what
   the session has learned that bears on this task — earlier findings, a changed Assumption; and
   the commit convention — stage paths by name (never `git add -A`), a plain conventional message
   that does not contain `complete task #`, push, never force, return what changed and the commit
   SHA(s). For a "Design sign-off" task the deliverable is the approach, written at the path the
   `Design:` line names. "Evaluation sign-off" skips this step: nothing is built, the finished work
   is judged.

2. **Read the result before anyone else does, so the evaluator and the user see only work that
   could be complete.** Check it on the thing itself — not on the implementer's report — against
   the task's Success criteria and the Rules: does it show what the report claims; does every fact
   or number in it have a source; does every term carry a meaning the reader can take, with no
   history, self-evident lines or repetition. Try it on a copy in a scratch directory outside the
   repository, removed before the command stops — never by breaking the repository in place. A
   miss the conductor can see goes straight back to the implementer with what is missing; only
   then does it go on.

3. **Have the result judged by someone other than its author, so a pass means it does its job.**
   Run `${CLAUDE_PLUGIN_ROOT}/references/evaluate.md` — kind Deliverable for an ordinary task, kind
   Design for "Design sign-off", kind Session for "Evaluation sign-off". NG → step 1 again with the
   findings; a Session NG names finished work that fails a criterion, so it becomes a task added
   before "Evaluation sign-off" in step 4, and the loop continues from that task. After three NG
   rounds on one task, stop and ask the user one thing, with a recommendation, opening with the
   session-status block.

4. **Fold what was learned into `steering.md`, so the plan stays true and the next task starts
   from it.** After every result and every evaluation: an Assumption that proved false is corrected;
   a finding that would recur becomes a Rule; a task the work uncovered is added, one made
   unnecessary is removed; the `Design:` line names the design once it exists. Commit with the
   task's work. A change to the Goal, the Success criteria or an approved design is the user's —
   raise it at once, as one question with a recommendation, opening with the session-status block;
   never hold it for a gate.

5. **For an ordinary task, record completion where a fresh conversation will read it, then move
   on — the user is not asked what is not theirs to decide.** Check the task off per Checking a
   task off in `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, commit and push. Then the next
   unchecked task.

6. **For a gate task, stop — the decision is the user's.** Write `State`'s `Pending`: the gate,
   the commit its artifact was judged at, and where the verdict is (the PR comment, or "in
   conversation"); commit `docs: present {task name} for the verdict`; push. Then present the
   judged artifact and the evaluator's verdict with the session-status block and wait. `/rn:ty`
   checks the task off and continues with the next unchecked task; `/rn:gm` returns to step 1
   with the feedback.
