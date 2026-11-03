# lane

The experience lane must give is in [ux.md](ux.md). How lane is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/integration/`.

  `sh dev/properties.sh lane` runs the property tests, `properties_*.py`, and
  `sh dev/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's E2E tests stand
  on is in `trials/trying.py`.
- E2E tests: `python3 dev/lane/tests/e2e/trial_changelog.py` tries O1 of the UX three times, as
  the README's walkthrough runs it, on `tests/e2e/changelog/` with the README's proposal,
  `tests/e2e/changelog.json`. `python3 dev/lane/tests/e2e/trial_routes.py` tries O2 three times
  on the same plugin with its `lead` and `reviewer`, from `tests/e2e/routes.json`, in an
  interactive session. `python3 dev/lane/tests/e2e/trial_lanes.py` tries the other lanes three
  times on its `noter`, whose steps lie in its part, from `tests/e2e/lanes.json` and the adapter in
  `tests/e2e/adapters/`. `python3 dev/lane/tests/e2e/trial_at_once.py` tries two runs of its
  `drafter` at once three times, each with its own value, from `tests/e2e/at_once.json`. The top
  of each file says what each run must show.
