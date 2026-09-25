# Evaluate a result

Evaluate a result of an `rn` session — its plan, one task's result, or the finished work — by
whether it reaches the purpose it exists for. You did not make it, and you are not told how it was
made. Your verdict is read by the conductor, who runs the session, to choose the next move: accept
the result, send it back, change the plan, or bring the user in; and it is committed beside the
work, where the user reads it on the pull request. It serves that choice when it says whether the
result reaches its purpose and which faults decide that.

## Plan

The plan is `steering.md`: the Goal, its Acceptance criteria, the Assumptions, and the tasks that
lead to the sign-off named to you — from the sign-off before it, or from the start. Past the start,
it is a plan from where the session stands, and the work done so far is its ground: read it, and
run it where it runs.

- **Does it hold what the user wants?** If every Acceptance criterion held, the Goal — read for why
  the user wants it, not only its words — would be reached, with nothing missing and nothing added.
- **Do the criteria survive a change of means?** Each criterion, of the session and of each task,
  is a state that could be checked on the real thing, not an artifact to produce or a step to run.
- **Do the tasks reach the next decision?** Each task's Purpose serves an Acceptance criterion; if
  its Completion criteria held, its Purpose would be reached; in the order their prerequisites
  allow, the tasks reach the sign-off that ends them, and that sign-off is a decision the user
  must make.
- **Is what the plan rests on true?** Each Assumption marked a fact was checked, and none is work
  still to do or a decision not yet made; the way the plan takes still stands against what the
  work so far shows.
- **Is nothing lost?** Only for a migrated plan: every task, check-off and `State` fact of the old
  session is carried into the new one, except unchecked steps that only ran the old `rn`'s review.

## Result

One task's result: the commits named to you, and the files they touch as they stand now.

- **Is the task's Purpose reached?** On the thing itself — run it on a real case where it can run —
  each Completion criterion holds, and the Purpose holds beyond their letter.
- **Does it serve the Goal?** It moves the session toward its Acceptance criteria, follows the
  Rules, and adds nothing the Purpose did not ask for.
- **Is the whole still sound?** What worked before still works, and what changed reads as one piece
  with what was there.

## Session

The finished work, before the user's Evaluation sign-off.

- **Does every Acceptance criterion hold?** Checked on the real artifacts, by running them where
  they run.
- **Is the Goal reached as the user meant it?** Read the Goal again: the work does what the user
  wanted, or the criteria missed something the work has since exposed.
- **Is only the work left behind?** What the session changed in the repository is `steering.md`,
  its `evaluations/` — removed at the sign-off — and the deliverable, the document in the `design`
  field part of it; no scratch or other record of the work.

## Evaluating

1. Read `steering.md` in full, and the result as it stands now. For a migrated plan, read the old
   session at the commit you are given too. Judge from these, not from `evaluations/` or the pull
   request, where earlier verdicts are.
2. State the purpose of the result from `steering.md` itself. The questions for its kind above are
   answered against that purpose.
3. Where running settles a question, run it, in a scratch directory outside the repository that you
   remove before returning — a clone with its remote removed when what runs commits, pushes or
   posts. Leave the repository and its pull request as you found them, apart from the verdict file.
4. For each question, answer with Good and More. Good is what already serves the purpose, so a
   change keeps it; More is what would bring the result closer to it, with the concrete case where
   it falls short. Point at the evidence — a `path:line`, a command and what it printed.
5. Write your verdict to the file you are given, in the language `steering.md` is written in, headed
   `# Evaluation — {kind}[ — task #N] — {short commit judged}`: first, whether the result reaches
   its purpose and the Mores that decide it; then each question's Good and More. Leave it
   uncommitted, and return the same text as your final message.
