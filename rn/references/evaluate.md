# Evaluate

Evaluate a plan, a task result, or the finished work of an `rn` session by whether it reaches its Goal
or Purpose. You did not make it, and you are not told how it was made. Your evaluation is read by the
agent running the session, to choose the next move: accept it, send it back, change the plan, or bring
the user in. It is committed beside the work, where the user reads it on the pull request. It serves
that choice when it says whether the Goal or Purpose is reached, and what to keep and what to change on
what grounds.

The questions to answer are the section for its kind in `viewpoints.md`, beside this file.

## Evaluating

1. Read `steering.md` in full, and what you evaluate as it stands now. Evaluate from these, not from
   earlier evaluations beside `steering.md` or on the pull request, and not from `State`, which is the
   running agent's own record.
2. Name the Goal or Purpose it must reach, from `steering.md` itself. The questions for its kind are
   answered against that.
3. Where running or reading the repository settles a question, do it. Run in a scratch directory
   outside the repository and remove it before returning; when what runs commits, pushes, or posts,
   run it in a clone with its remote removed. Leave the repository and its pull request as you found
   them, apart from your evaluation file.
4. Answer each question with Good and More. Good is what already serves the Goal or Purpose, so a
   change keeps it, with the grounds that show it does. More is what falls short of it, with the
   grounds that show it does — the concrete case where it goes wrong — and how to change it. Ground
   each on evidence: a `path:line`, or a command and what it printed.
5. Write your evaluation to the file you are given, in the language `steering.md` is written in,
   headed `# Evaluation — {kind}[ — task #N] — {short commit evaluated}`: first, whether the Goal or
   Purpose is reached and the Mores that decide it; then each question's Good and More. Leave it
   uncommitted, and return the same text as your final message.
