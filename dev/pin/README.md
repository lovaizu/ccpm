# Pin

The experience Pin must give is in [ux.md](ux.md). How Pin is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/pin/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s1_s3_start.py` and `test_s2_s4_answer.py`, with a test for
  each of its paths. The architecture tests run Pin's guard by Pin's hook entries on
  `plugins/pin/hooks/lanes.json`, through the double of Claude Code in `dev/lane/testing.py`, and
  `check.py` by the command the pinner's rule names.

  `sh dev/scripts/properties.sh pin` runs the property tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh pin` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- Pin's guard: `plugins/pin/hooks/` is laid by `python3 plugins/lane/scripts/lay.py write` from a
  proposal, as `.claude/rules/dev.md` says, and is never changed by hand. The proposal lays on the
  pinner each rule that the architecture's guard holds: it writes only `{design}`, runs only the
  check on it, passes the check after each change, and gives `asks` or `done` as each run ends, its
  `results`. `python3 plugins/lane/scripts/lay.py up plugins/pin` prints each lane laid, for a
  proposal that lays them again.
