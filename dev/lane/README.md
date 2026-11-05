# lane

The experience lane must give is in [ux.md](ux.md). How lane is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s<n>_*.py`, with a test for each of its paths. The
  architecture tests lay the proposals of `tests/ux/` on a copy of `tests/ux/changelog/`, with the
  adapter in `tests/ux/adapters/` and the stand-in dependency `tests/ux/checker/`. What the double
  of Claude Code does beyond the hooks reference is in `TRIES` in `testing.py`, each with the
  version and the day of the try that showed it.

  `sh dev/scripts/properties.sh lane` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on
  is in `trials/trying.py`.
- ux trials: `python3 dev/lane/tests/ux/trial.py` tries O1 and O2 of the UX three times each,
  as the architecture's ux says: a developer AI on Opus, given the intent of `tests/ux/intent_o1.md`
  or `tests/ux/intent_o2.md`, writes and lays its own proposal on a copy of
  `tests/ux/changelog/`, and the trial runs the plugin with an ask that invites a break. Give
  `o1` or `o2`, and a number of runs, to try one alone. The top of the file says what each run
  must show and how each key result is measured.
