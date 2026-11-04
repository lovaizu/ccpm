# Turn

The experience Turn must give is in [ux.md](ux.md). How Turn is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/turn/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`.

  `sh dev/properties.sh turn` runs the property tests, `properties_*.py`, and
  `sh dev/mutate.sh turn` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- ux trials, each in an interactive session of Claude Code, as Turn's roles run in the background:
  - `python3 dev/turn/tests/ux/trial_readme.py` tries O1 of the UX on a README, as the README's
    walkthrough runs it;
  - `python3 dev/turn/tests/ux/trial_module.py` tries O1 on code whose parts stand apart;
  - `python3 dev/turn/tests/ux/trial_new_kind.py` tries O2, on a kind Turn ships no template for;
  - `python3 dev/turn/tests/ux/trial_caller.py` tries O3, with the plugin `caller` in
    `tests/ux/caller/` standing in for rn.

  In each, an AI stands in for the person, answering from an intent written in the file and never
  shown Turn. Each takes `[runs] [first]`, the number of runs, three by default, and the number of
  the first; the top of each file says what each run must show.
