# Turn

The experience Turn must give is in [ux.md](ux.md). How Turn is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/turn/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s1_s3_start.py`, `test_s2_answer.py` and
  `test_s2_rounds.py`, with a test for each of its paths. The architecture tests run Turn's
  guard and Pin's, each by its plugin's hook entries on its `hooks/lanes.json`, through the double
  of Claude Code in `dev/lane/testing.py`, and `plan.py`, `rounds.py`, `throwaway.py` and Pin's
  `check.py` by the commands the rules name, on the subject `tests/ux/tidy/`.

  `sh dev/scripts/properties.sh turn` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh turn` runs the mutation testing set in `cosmic-ray.toml` on the unit
  tests, as [dev/README.md](../README.md) says.
- Turn's guard: `plugins/turn/hooks/` is laid by `python3 plugins/lane/scripts/lay.py write` from a
  proposal, as `.claude/rules/dev.md` says, and is never changed by hand. The proposal holds each
  rule that the guard holds the planner, the generator and the evaluator to, and the routes on up's
  step 2. `python3 plugins/lane/scripts/lay.py up plugins/turn` prints each lane
  laid, for a proposal that lays them again.
- ux trials: `python3 dev/turn/tests/ux/trial.py` tries O1 and O2 of the UX three times each, as
  the architecture's ux says: an AI on Opus stands in for the person, given the intent of
  `tests/ux/intent_readme.md`, `tests/ux/intent_man_page.md` or `tests/ux/intent_o2.md`, on a copy
  of `tests/ux/tidy/`; for O2, the plugin `tests/ux/caller/` stands in for a calling AI's plugin.
  Give `readme`, `man-page` or `o2`, and a number of runs, to try one alone. Each runs in an
  interactive session of Claude Code, as Turn's roles run in the background. The top of the file
  says what each run must show and how each key result is measured.
