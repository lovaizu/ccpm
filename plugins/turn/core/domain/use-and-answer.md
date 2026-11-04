# Use and answer

How generator, evaluator, refactorer and proofreader each answer the questions their run was given,
in the same way, so that what one finds good another finds good on the same work.

1. **The work is read whole, and what runs is run.** Read each file of the work given you, `work`,
   to its end with the Read tool, as its user would meet it. Run each command given you,
   `commands`, as its user would, and read what it prints. A command that would reach the person's
   own files, such as their Downloads, rather than the repository or a temporary folder, is not
   run: tell it in your reply, as a fault of the design. Read the work, not your memory of it:
   a line you made is not the line its user reads until you read it there.
2. **Each question is answered as the work's user.** Stand where the work's user stands, as the
   template's goal names them, with only the work and what they would have beside it. For each
   question your run was given, write either:
   - `good`, where the work brings its user what the question asks, with `lines`: each place that
     brings it, as `<path>:<line>` or `<path>:<from>-<to>`, the line numbers as the Read tool
     shows them; or
   - `more`, where it does not yet, with `good_when`: what the user gets once it is good, in one
     sentence, in the user's terms. Never say how to make it: the one who makes it holds the
     sources, and a fix named here would be argued over instead of the user's need.

   A question asks what the work brings its user, not whether a rule of form is kept. Do not hunt
   for defects the user would never meet: a work mended for them does not get better for its user.
3. **The answers are written and checked.** Write them, in the form of
   `${CLAUDE_PLUGIN_ROOT}/core/domain/forms/answers.json`, at the path given you, `answers`, then
   run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/answers.py check {run} {answers}`, as a command of
   its own, with your run values `run` and `answers` put in for `{run}` and `{answers}`. It names each question given you that has no
   answer, each answered twice or not given, and each line that does not lie in the work. Mend
   the answers until it gives 0. It gives 2 where it cannot check, with why: a fault of the run,
   which you tell in your reply, never work around.
