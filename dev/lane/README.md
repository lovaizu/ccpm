# lane

The experience lane must give is in [ux.md](ux.md). How lane is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root.

  `sh dev/properties.sh lane` runs the property tests, `tests/properties_*.py`, and
  `sh dev/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on is
  in `trials/trying.py`.
- Trials: `trials/notes_trial.py` tries lane as the building AI meets it. It lays the README's lanes
  on `trials/notes` by `lay.py write` and runs notes as laid. `trials/memo_trial.py` tries every
  lane on `trials/memo`, a plugin whose steps call for each. Both stand on `trials/lane_trials.py`,
  and the top of each file says what it takes.
