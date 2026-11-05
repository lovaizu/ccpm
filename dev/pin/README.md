# Pin

The experience Pin must give is in [ux.md](ux.md). How Pin is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/pin/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s1_s3_start.py` and `test_s2_s4_answer.py`, with a test for
  each of its paths. The architecture tests run Pin's guard by Pin's hook entries on
  `plugins/pin/hooks/lanes.json`, through the double of Claude Code in `dev/lane/testing.py`, and
  `check.py` by the command the pinner's rule names.

  `sh dev/scripts/properties.sh pin` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh pin` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- Pin's guard: `plugins/pin/hooks/` is laid by `python3 plugins/lane/scripts/lay.py write` from a
  proposal, as `.claude/rules/dev.md` says, and is never changed by hand. The proposal lays on the
  pinner each rule that the architecture's guard holds: it writes only `{design}`, runs only the
  check on it, passes the check after each change, and gives `asks` or `done` as each run ends, its
  `results`. `python3 plugins/lane/scripts/lay.py up plugins/pin` prints each lane laid, for a
  proposal that lays them again.
- ux trials: `python3 dev/pin/tests/ux/trial.py` tries O1 and O2 of the UX three times each, as
  the architecture's ux says: an AI on Opus stands in for the person, given the intent of
  `tests/ux/intent_o1.md` or `tests/ux/intent_o2.md`, on a copy of the notes app in
  `tests/ux/notes/`, which the architecture tests read too; for O2, the plugin `tests/ux/maker/`
  stands in for a maker AI's plugin. Give `o1` or `o2`, and a number of runs, to try one alone. The
  top of the file says what each run must show and how each key result is measured.
