# Use and answer

How the generator and the evaluator each answer the questions their run was given, in the same
way, so that what one finds met the other finds met on the same work.

1. **The work is read whole, and what runs is run.** Read each file of the work, `{work}`, to its
   end with the Read tool, as its user would meet it. Run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py {run}`, which runs each command the work's
   user runs, in order, in a throwaway copy of the repository with a throwaway home, and read what
   each printed. Read the work, not your memory of it: a line you made is not the line its user
   reads until you read it there.
2. **Each question is answered as the work's user.** Stand where the work's user stands, as the
   best practice's goal names them, with only the work and what they would have beside it. For
   each question your run was given, write either:
   - under `met`, with `lines`: each place that brings the user what the question asks, as
     `<path>:<line>` or `<path>:<from>-<to>`, the line numbers as the Read tool shows them; or
   - under `not_met`, with `lacks`: what the user still lacks, in one sentence, in the user's
     terms. Never say how to make it: the one who makes it holds the sources, and a fix named here
     would be argued over instead of the user's need.

   A question asks what the work brings its user, not whether a rule of form is kept. Do not hunt
   for defects the user would never meet: a work mended for them does not get better for its user.
3. **The Answers are written and checked.** Write them at `{answers}`, in the form of
   `${CLAUDE_PLUGIN_ROOT}/core/domain/forms/answers.json`. Then run
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/rounds.py check {run} {answers}`, with your run values put
   in for `{run}` and `{answers}`, as a command of its own. It names each question given you that
   has no answer, each answered twice or not given, and each line that does not lie in the work.
   Mend the Answers until it gives 0. It gives 2 where it cannot check, with why: a fault of the
   run, which you tell in your last message, never work around.
