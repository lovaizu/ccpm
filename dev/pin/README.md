# Pin

What Pin must give its users is in [its product vision](product-vision.md), and every decision of
its documents in [its design tree](design-tree.md). How Pin is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/pin/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s1_s2_start.py` and `test_s3_answer.py`, with a test for
  each of its paths. The architecture tests run Pin's guard by Pin's hook entries on
  `plugins/pin/hooks/lanes.json`, through the double of Claude Code in `dev/lane/testing.py`, and
  `check.py` by the command the pinner's rule names.

  `sh dev/scripts/properties.sh pin` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh pin` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- Pin's guard: `plugins/pin/hooks/` is laid by `python3 plugins/lane/scripts/lay.py write` from a
  proposal, as `.claude/rules/dev.md` says, and is never changed by hand. The proposal, with
  `"plugin": "plugins/pin"`, lays on the pinner each rule that the architecture's guard holds: it
  writes only `{design}`, changes it only with Edit once made, runs only the check on it, and
  passes the check after each change. Its routes are laid on step 2 of the orchestrator: `down`
  starts the pinner, the pinner's `asks` waits for the user, and its `done` ends the run.
  `python3 plugins/lane/scripts/lay.py up plugins/pin` prints each lane laid, for a proposal that
  lays them again.
- ux trial: `python3 dev/pin/tests/ux/trial.py` tries O1 of the product vision three times in each
  of its two ways, as the architecture's Tests says: typed, where the stand-in types `/pin:down`,
  and called, where the plugin `tests/ux/maker/` stands in for the user's AI, writes a design tree
  and calls the skill. An AI on Opus stands in for the person, given the intent of
  `tests/ux/intent_typed.md` or `tests/ux/intent_called.md`, on a copy of the notes app in
  `tests/ux/notes/`, which the architecture tests read too. Give `typed` or `called`, and a number
  of runs, to try one alone. The top of the file says what each run must show and how each key
  result is measured.
