# pin

The experience pin must give is in [ux.md](ux.md). How pin is built to give it, and how it is
checked, is in [architecture.md](architecture.md).

- Tests: run `python3 -m unittest discover -s dev/pin/tests` from the repository root. They lie in
  `tests/unit/`, at the path of what each tests, and `tests/architecture/`.

  `sh dev/scripts/properties.sh pin` runs the property tests, `properties_*.py`, and
  `sh dev/scripts/mutate.sh pin` runs the mutation testing set in `cosmic-ray.toml`, as
  [dev/README.md](../README.md) says.
- Unit trials of the pinner: `python3 dev/pin/tests/unit/core/roles/trial_pinner.py` tries
  `pin:down` alone three times, a script answering "Yes." for the person and a project subagent
  named Explore giving set facts. `trial_resume.py` beside it tries a stopped run gone on in a new
  conversation, and `trial_reopen.py` a decision that maker's `reviser` reopens.
- ux trials: `python3 dev/pin/tests/ux/trial_down.py` tries O1 of the UX three times, as the
  README's walkthrough runs it, and `python3 dev/pin/tests/ux/trial_caller.py` tries O2 three
  times with the plugin `maker` in `tests/ux/maker/` standing in for Turn or rn. In each, an AI
  stands in for the person, answering from an intent written in `tests/pinning.py` and never shown
  pin.

Each trial takes `[runs] [first]`, the number of runs and the number of the first; the top of each
file says what each run must show.
