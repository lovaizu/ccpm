# rn's test gaps

This page is for whoever makes rn's architecture and its cases. It names each place where rn's
cases, in `dev/rn/tests/`, can't follow [the architecture](../architecture.md) or one another. Each
case named here stays xfail with its gap as the reason.

- `test_starts_due_from_the_root_read_the_run_in_rns_worktree`, in
  `unit/test_rn_lane_adapters.py`: the case writes the plan into rn's worktree alone, with none of
  the documents that the command names as its inputs, so `tree/design.py`'s `read`, which holds the
  plan to `tree/inputs.py`, refuses it with "its inputs name no architecture, which the code best
  practice takes". Its Given needs the plan's inputs in the worktree, as `rn_bench.worktree` writes
  them, or the starts due need to read the plan by its schema alone.
- `test_a_role_that_writes_beside_its_deliverable_is_told_its_step`, in
  `integration/test_rn_principles.py`: the generator writes at its step 1, as it marks no step done,
  and `lane/adapters/rules.py` gives `writes` only at steps 3 and 4, as its contract says, while
  Lane judges a call by the rules of the step due alone, so the guard lets the write through. The
  case needs the generator at step 3, with steps 1 and 2 marked done, or step 1 needs `writes`. It
  also types no `/rn:up`, so no run of Lane holds the start.
