# turn

The experience turn must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/turn/tests` from the repository root. The property
  tests, `tests/properties.py`, run by `sh dev/properties.sh turn`, and the mutation testing, set
  in `cosmic-ray.toml`, by `sh dev/mutate.sh turn`, as [dev/README.md](../README.md) says.
- Trials, each in a new folder of its own, one at a time, the top of each file saying what it takes:
  - `trials/trial.py` runs turn as its user does on a task folder, `one`, a small script's README,
    or `readme`, a CSV tool's, keeping what the run gave back in `<new folder>.work/`;
  - `trials/judge.py` judges each item of the folders `trial.py` kept afresh, by one bar;
  - `trials/flow/flow.py` tries the orchestrator and its flow on each way a run can take, the roles
    stood in for with the replies `trials/flow/replies.py` sets;
  - `trials/roles/roles.py` tries each role on its own, and `trials/roles/kept.py` the generator and
    the first user kept started within a round.
- `results.json` in `trials/flow/`, `trials/roles/` and `trials/readme/` keeps what earlier runs of
  those trials found, as the session's decisions cite them.
