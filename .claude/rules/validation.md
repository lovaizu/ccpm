# Validation (ccpm)

How a product made here is checked before it ships: by using it as its user would, not by covering
every case up front.

## Check the attractive quality by using the product

- **Check the attractive quality by validation: use the product as its user would, on the golden
  path, and compare what happened with what it aims for.**
  - Rationale: the attractive quality is why the user chooses the product, so the checking effort goes
    there first.
- **Do not cover edge cases or alternative flows up front; fix a failure of what the user takes for
  granted when it shows up in use.**
  - Rationale: such failures are easy to see and quick to fix. Covering them up front grows a list of
    checks that all pass while no one has checked the attractive quality.
- **Check by script, every time, whatever a script can decide.**
  - Rationale: it costs nothing to run and gives the same answer every time.
