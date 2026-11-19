# rn's test gaps

This page is for whoever makes rn's architecture and its cases. It names each place where rn's
cases, in `dev/rn/tests/`, can't follow [the architecture](../architecture.md) or one another. Each
case named here stays xfail with its gap as the reason.

- The bench quotes the ground of a commit in single quotes, as `rn_bench.py:114` says
  `commit {RUN} '{ground}'`, and the ground of
  `test_an_edit_of_the_design_tree_is_committed_with_its_ground` holds apostrophes: "A module's -m
  is how invoicer's users run Python". The shell splits it, and tree.py gives its usage.
- `test_findings_past_the_limit_start_no_further_round` of `integration/test_rn_principles.py`
  makes a second round of content after a first judged short with no decision changed, while
  `test_findings_with_no_decision_changed_give_none` of `unit/test_rn_rounds.py` gives no start
  there, as the finding waits for the orchestrator.
- `test_a_deliverable_done_with_a_condition_not_good_is_refused` of
  `integration/test_rn_components.py` asks for the command named. The design tree's schema
  refuses a done deliverable that keeps its conditions, naming the place
  `deliverables/0/inputs`, before status.faults can name the deliverable.
- No case gives the design tree a `decided` that holds its ground or a date, which the design tree
  schema's `pattern` refuses, so schemas/form.py leaves `pattern` unread.
- The generator's Cut holds each decision with its `by`, as `decisions` of `unit/test_rn_rounds.py`
  gives it, so `schemas/cut.schema.json` takes `by` beside each decision.
