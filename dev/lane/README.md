# lane

The experience lane must give is in [ux.md](ux.md). How lane is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/architecture/`. The architecture
  tests lay the proposals of `tests/ux/` on a copy of `tests/ux/changelog/`, with the adapter in
  `tests/ux/adapters/` and the stand-in dependency `tests/ux/checker/`.

  `sh dev/scripts/properties.sh lane` runs the property tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on
  is in `trials/trying.py`.
- ux trials: `python3 dev/lane/tests/ux/trial_changelog.py` tries O1 of the UX three times, as
  the README's walkthrough runs it, on `tests/ux/changelog/` with the README's proposal,
  `tests/ux/changelog.json`. `python3 dev/lane/tests/ux/trial_routes.py` tries O2 three times on
  the same plugin with its `lead` and `reviewer`, from `tests/ux/routes.json`, in an interactive
  session. The top of each file says what each run must show.
