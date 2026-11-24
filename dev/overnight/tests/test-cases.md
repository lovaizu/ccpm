# Test cases

## E2E cases

None in code, as overnight holds the prompts of ask and status. The walkthrough run of the README's
request tries it whole, as Test strategy says under Scenario testing. That run checks KR1.1. The
last line of its status shows the share that KR1.1 measures, such as
`0 of 3 pieces stopped by the usage limit, a wait for an answer, or the session closing.`

## Integration cases

`integration/` holds a file for each sequence and one for the principles. They run with the
stand-in of Claude Code in `claude_code/`.

## Unit cases

`unit/` holds a file for each module of the parts in `plugins/overnight/domain/`.

## Properties

`properties/` holds a file for each of the runner, pieces, and status. Each file lists its
invariants at its top.

## Trace

Run `python3 dev/scripts/trace.py check overnight` from the top of the repository.

## Gaps

- S1: hand-over records the piece as running only after it starts the runner. A runner whose
  conversation ends at once, such as where `claude` isn't found, then has no record to end in. So
  no case can show that piece failed with the system's words.
- P5.2: the README and `pieces.command.main` leave open how the table shows a piece that a stop
  left. So the cases check only that its row names the stop, and doesn't show it running or
  waiting.
- P5.1: the README and `pieces.command.main` leave open how a row shows several waits. They leave
  open too how it shows a wait that ends another day, or last words of several lines. So no case
  checks those rows.
