# lane

What lane must give its users is in [its product vision](product-vision.md). How lane is
built to give it, and how it is checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s<n>_*.py`, with a test for each of its paths: S1 and S2 in
  one file each, the four sequences of S3 in `test_s3_run.py`, `test_s3_held.py`,
  `test_s3_result.py` and `test_s3_at_once.py`, and S4 in `test_s4_up.py`. The architecture tests
  lay the README's walkthrough, and the proposals of `tests/ux/` on a copy of
  `tests/ux/changelog/`, with the adapter in `tests/ux/adapters/` and the stand-in dependency
  `tests/ux/checker/`. What the double of Claude Code does beyond the hooks reference is in
  `TRIES` in `testing.py`, each with the version and the day of the try that showed it.

  `sh dev/scripts/properties.sh lane` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on
  is in `trials/trying.py`.
- ux trial: `python3 dev/lane/tests/ux/trial.py` tries O1 of the product vision three times, as
  the architecture's Tests say: a stand-in for the user on Opus, given the intent of
  `tests/ux/intent_o1.md`, writes and lays its own rules and routes on a copy of
  `tests/ux/changelog/`, and the trial runs the plugin by typing `/changelog:write` with words that
  invite a break, in `claude -p` and in an interactive session. Give a number of runs to try fewer.
  The top of the file says what each run must show and how KR1.1 and KR1.2 are measured.
