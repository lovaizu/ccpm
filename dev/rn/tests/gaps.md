# rn's test gaps

This page is for whoever makes rn's architecture and its cases. It names each place where rn's
cases, in `dev/rn/tests/`, can't follow [the architecture](../architecture.md) or one another. Each
case named here stays xfail with its gap as the reason.

- S2, the pause, and the Strategy of Components that gives rn's order to Lane as the starts due:
  `lane/adapters/starts_due.py` gives each start due from the design tree whatever command was
  typed last, so after `/rn:dn` stops each role, it gives the stopped starts due again, and Lane
  stops the orchestrator's end of its turn. The cases
  `test_a_pause_leaves_lane_no_start_due_so_the_turn_ends` and the `a pause` case of
  `test_starts_due_wait_for_the_sign_off_of_a_new_runs_plan` ask for no start due once the last
  command typed is `/rn:dn`, as S2 draws the run waiting until `/rn:up`.
- The Strategy of Components that gives rn's order to Lane as the starts due:
  `lane/adapters/starts_due.py` says it gives 1 for a design tree that isn't JSON, while
  `rounds.folder`, which finds the run's folder, passes over such a tree as one with no work left,
  so no run's folder with it reaches the adapter, and no case can give it. The cases of the
  adapter's refusals take a design tree out of its schema instead.
