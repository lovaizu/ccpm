# rn's test gaps

Each place where rn's test cases, in this folder, can't follow [the architecture](../architecture.md)
and the skeleton in `plugins/rn/`, for whoever makes the architecture.

- Test strategy, Installation testing: `dev/scripts/e2e.py` runs Claude Code on plugin folders, and
  has no way to run the README's install commands in a fresh home's shell. So
  `test_rn_installs_by_the_readmes_commands` runs them by itself, and no case shows `/rn:up` answer
  in rn as installed.
- S1, an evaluator's end held: the double of Claude Code gives a subagent no Edit, and its Write
  only makes a new file, so no integration case shows an evaluator mend its Answers after rn's
  check holds its end, and pass. `test_an_evaluators_end_whose_answers_leave_out_a_condition_is_held`
  shows only the hold.
