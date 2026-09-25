# Evaluate a result

Evaluate a result of an `rn` session by whether it reaches the purpose it exists for. You did not
make it, and you are not told how it was made. Your verdict is read by the agent running the session,
to choose the next move: accept the result, send it back, change the plan, or bring the user in. It
is committed beside the work, where the user reads it on the pull request. It serves that choice when
it says whether the result reaches its purpose, and what to keep and what to change on what grounds.

What the result must reach, and the questions to answer, are its kind's section of `purpose.md`,
beside this file.

## Evaluating

1. Read `steering.md` in full, and the result as it stands now. Judge from these, not from earlier
   verdicts beside `steering.md` or on the pull request.
2. State the purpose of the result from `steering.md` itself. The questions for its kind are
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
   `# Evaluation — {kind}[ — task #N] — {short commit judged}`: first, whether the result reaches
   its purpose and the Mores that decide it; then each question's Good and More. Leave it
   uncommitted, and return the same text as your final message.
