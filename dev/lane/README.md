# lane

The experience lane must give is in [ux.md](ux.md). How lane is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/architecture/`.

  `sh dev/properties.sh lane` runs the property tests, `properties_*.py`, and
  `sh dev/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on
  is in `trials/trying.py`.
- ux trials: `python3 dev/lane/tests/ux/trial_changelog.py` tries O1 of the UX three times, as
  the README's walkthrough runs it, on `tests/ux/changelog/` with the README's proposal,
  `tests/ux/changelog.json`. `python3 dev/lane/tests/ux/trial_routes.py` tries O2 three times on
  the same plugin with its `lead` and `reviewer`, from `tests/ux/routes.json`, in an interactive
  session. The top of each file says what each run must show.
- Until their cases have architecture tests, as [architecture.md](architecture.md#test) plans,
  trials of single cases also lie in `tests/ux/`. `trial_lanes.py` tries the other lanes three
  times on its `noter`, whose steps lie in its part, from `tests/ux/lanes.json` and the adapter in
  `tests/ux/adapters/`. `trial_at_once.py` tries two runs of its `drafter` at once three times,
  each with its own value, from `tests/ux/at_once.json`. `trial_dependency.py` tries a command of a
  dependency's skill three times on its `verifier`, from `tests/ux/dependency.json` and the
  stand-in dependency `tests/ux/checker/`.
