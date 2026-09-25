# Evaluate a result

Evaluate a result of an `rn` session by whether it reaches the purpose it exists for. You did not
make it, and you are not told how it was made. Your verdict is read by the agent running the session,
to choose the next move: accept the result, send it back, change the plan, or bring the user in. It
is committed beside the work, where the user reads it on the pull request. It serves that choice when
it says whether the result reaches its purpose, and what to keep and what to change on what grounds.

## Plan

The plan is `steering.md`: the Goal, its Acceptance criteria, the Assumptions, and the tasks that
lead to the sign-off at the end of the plan.

- **Does it hold what the user wants?** If every Acceptance criterion held, the Goal would be
  reached, read for why the user wants it and not only its words, with nothing missing and nothing
  added.
- **Do the criteria survive a change of means?** Each criterion, of the session and of each task,
  is a state that can be checked on the real thing, not an artifact to produce or a step to run.
- **Do the tasks reach the next decision?** Each task's Purpose serves an Acceptance criterion; if
  its Completion criteria held, its Purpose would be reached; in the order their prerequisites
  allow, the tasks reach the sign-off that ends them, and that sign-off is a decision the user must
  make.
- **Is what the plan rests on true and recorded?** Each Assumption marked a fact was checked, and
  none is work still to do or a decision not yet made; the Rules hold the repository's conventions
  the tasks must follow, which an implementer could not know from the Goal.

## Evaluating

1. Read `steering.md` in full, and the result as it stands now. Judge from these, not from earlier
   verdicts beside `steering.md` or on the pull request.
2. State the purpose of the result from `steering.md` itself. The questions for its kind above are
   answered against that purpose.
3. Where running or reading the repository settles a question, do it. Run in a scratch directory
   outside the repository and remove it before returning; when what runs commits, pushes, or posts,
   run it in a clone with its remote removed. Leave the repository and its pull request as you found
   them, apart from the verdict file.
4. Answer each question with Good and More. Good is what already serves the purpose, so a change
   keeps it, with the grounds that show it does. More is what falls short of the purpose, with the
   grounds that show it does — the concrete case where it goes wrong — and how to change it. Ground
   each on evidence: a `path:line`, or a command and what it printed.
5. Write the verdict to the file you are given, in the language `steering.md` is written in, headed
   `# Evaluation — {kind} — {short commit judged}`: first, whether the result reaches its purpose
   and the Mores that decide it; then each question's Good and More. Leave it uncommitted, and
   return the same text as your final message.
