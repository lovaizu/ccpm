# turn

The experience turn must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/turn/tests` from the repository root. The property
  tests, `tests/properties.py`, run by `sh dev/properties.sh turn`, and the mutation testing, set
  in `cosmic-ray.toml`, by `sh dev/mutate.sh turn`, as [dev/README.md](../README.md) says.
- Trials, one at a time, each run in a folder of its own in the system's temporary folder, whose
  path it prints, the top of each file saying what it takes:
  - `trials/orchestrator/orchestrator.py` tries the orchestrator on each way a run can take, the
    roles stood in for with the replies `trials/orchestrator/replies.py` sets;
  - `trials/roles/roles.py` tries each role on its own, and `trials/roles/kept.py` the generator and
    the first user settling the work between themselves by message.
