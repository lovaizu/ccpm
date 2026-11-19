# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md), for whoever makes the architecture.

- Directory structure, S1: `schemas/` holds the form of a sign-off, which Data model lacks and no
  arrow of S1 carries, as `/rn:ty` reaches the orchestrator alone, so the skeleton holds no
  sign-off schema.
- Directory structure: no line holds `domain/template/`, the template check that `check/` runs on a
  generator's document and `dev/scripts/check.sh` runs on each plugin's documents, or
  `hooks/adapters/`, rn's adapters that Lane runs for each start's Cut, a step's practices, and the
  results kept for S2's pick-up.
