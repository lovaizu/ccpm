# turn

The experience turn must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/turn/tests` from the repository root.
- Acceptance trials: `trials/trial.py` runs turn as its user does on a task folder, `one` for the
  Flow trial and `readme` for the others, and `trials/baseline.py` the version in use on the same
  task; each keeps what its run gave back in `<new folder>.work/`, and `trials/judge.py` judges
  KR1.1 on those folders at once. The top of each file says what it takes; run each trial three
  times at once, each in a new folder of its own.
