# Lane

What lane must give its users is in [its product vision](product-vision.md).
[architecture.md](architecture.md) says how lane gives it, and how to check that it does.

- Tests: run `python3 -m unittest discover -s dev/lane/tests` from the repository root. They lie
  in `tests/unit/`, at the path of what each tests, and `tests/architecture/`, a file for each
  sequence of the architecture, `test_s<n>_*.py`, with a test for each of its paths. S1 and S2 have
  one file each, the four sequences of S3 have `test_s3_run.py`, `test_s3_held.py`,
  `test_s3_result.py`, and `test_s3_at_once.py`, and S4 has `test_s4_up.py`. The architecture tests
  lay the README's walkthrough, and the proposals of `tests/product-vision/` on a copy of
  `tests/product-vision/changelog/`, with the adapters in `tests/product-vision/adapters/` and the
  stand-in dependency `tests/product-vision/checker/`. What the double of Claude Code does beyond
  the hooks reference is in `TRIES` in `testing.py`. Each entry names the version and the day of
  the try that showed it.

  `sh dev/scripts/properties.sh lane` runs the property-based tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh lane` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- What every plugin's tests stand on is in `testing.py`, and what every plugin's trials stand on
  is in `trials/trying.py`.
- Product vision trial: `python3 dev/lane/tests/product-vision/trial.py` tries O1 of the product
  vision three times, as the architecture's Tests say. In each run, a stand-in for the user on
  Opus, given the intent of `tests/product-vision/intent_o1.md`, writes and lays its own rules and
  routes on a copy of `tests/product-vision/changelog/` with the files of
  `tests/product-vision/o1/`. The trial then runs the plugin by typing `/changelog:write` with words
  that invite a break, in `claude -p` and in an interactive session, with a stand-in for the person
  answering each point. Give a number of runs to try fewer. The top of the file says what each run must show and how the trial measures KR1.1
  and KR1.2. `tests/product-vision/test_trial.py` tries the trial's judge on records with known
  answers, and `trial.py --person` the person's stand-in.
