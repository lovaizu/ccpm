# rn

The experience rn must give is in [ux.md](ux.md), and how it is built to give it, and checked, is
in [architecture.md](architecture.md).

- Tests: `python3 -m unittest discover -s dev/rn/tests` from the repository root.
- Trials: `trials/moves/` tries rn's prompts one move at a time, each case from a session state
  made beforehand in a repository of its own, with turn, gh and the user stood in for:
  `python3 dev/rn/trials/moves/moves.py --help` says what it takes and lists the cases.
