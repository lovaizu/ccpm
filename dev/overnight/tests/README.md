# Test cases

## E2E cases

overnight holds prompts, so no E2E test is written. The walkthrough run of the README's queue tries
it whole, as Scenario testing says.

## Integration cases

[integration/](integration/) holds a test for each path, principle item, component's decision, and
handoff. Each runs the scripts' parts as the skills and the runner run them. The doubles of Claude
Code and of the clock lie in [claude/](claude/) and [overnight_bench.py](overnight_bench.py).

## Unit cases

[unit/](unit/) holds the tests of each interface of `plugins/overnight/domain/` and of
`scripts/queue.py`. Each test names the integration case it supports.

## Properties

[properties/](properties/) holds a test for each invariant that the requirements state. Their
generators lie in [overnight_generators.py](properties/overnight_generators.py).

## Trace

Run `python3 dev/scripts/trace.py check overnight` from the top of the repository. Then run
`python3 dev/scripts/trace.py doubles` to check the double of Claude Code.

## Gaps

- session: no contract names the output form of `claude`, so the cases take `stream-json`, which
  P5.1 needs.
