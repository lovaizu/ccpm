# rn's test gaps

Each place where rn's test cases, in this folder, can't follow [the architecture](../architecture.md)
and the skeleton in `plugins/rn/`, for whoever makes the architecture.

- Test strategy, Installation testing: `dev/scripts/e2e.py` runs Claude Code on plugin folders, and
  has no way to run the README's install commands in a fresh home's shell. So
  `test_rn_installs_by_the_readmes_commands` runs them by itself, and no case shows `/rn:up` answer
  in rn as installed.
- Solution strategy, Every item handled, and S1 `GD->>R: checks its record`, for the orchestrator:
  its part takes its steps again at each turn from the first that has work, and a Record marks no
  turn, so rn's check can't tell which steps a turn took. It holds a turn whose record begins its
  part again at step 1 to every step, step 8 included, which has work only where `/rn:up` alone
  finds no run left, and a turn that records no step 1 to nothing, as the steps of an earlier turn
  meet each. `test_a_sign_off_waiting_and_only_the_steps_with_work_recorded_lacks_nothing` holds
  the first as the architecture draws it, and no case can show the second.
- S1, an evaluator's end held: the double of Claude Code gives a subagent no Edit, and its Write
  only makes a new file, so no integration case shows an evaluator mend its Answers after rn's
  check holds its end, and pass. `test_an_evaluators_end_whose_answers_leave_out_a_condition_is_held`
  shows only the hold.
