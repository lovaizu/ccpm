# rn

The experience rn must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/rn/tests` from the repository root.
- Trials: each file in `trials/` but `common.py` runs one scene of rn as its user would, in the
  practice repository, with the rn and turn of this working tree copied as they are when the trial
  starts: `python3 dev/rn/trials/<scene>.py --help` says what it takes. Trials run one at a time,
  since they share the practice repository.
- The learner on its own: `python3 dev/rn/trials/learner/learner.py <new folder>` starts rn:learner
  on a session set beforehand, its record and a conversation of the conductor's, holding a slip
  each shows, as the architecture's Verification says; it needs no practice repository.
