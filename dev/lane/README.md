# lane

The experience lane must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/lane/tests` from the repository root. The property
  tests, `tests/properties_*.py`, run by `sh dev/properties.sh lane`, and the mutation testing,
  set in `cosmic-ray.toml`, by `sh dev/mutate.sh lane`, as [dev/README.md](../README.md) says.
- What every plugin's tests stand on is `testing.py`, and what every plugin's trials stand on
  `trials/trying.py`.
- Trials: `trials/notes_trial.py` tries lane as the building AI meets it, laying lanes on the
  README's `notes` and on turn and running notes as laid; `trials/memo_trial.py` tries every lane
  on memo, a plugin whose steps call for each. The top of each file says what it takes.
