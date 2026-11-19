# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md) or the form that Lane takes in, for whoever makes the
architecture.

- S1, the orchestrator's steps on `/rn:ty`, `/rn:gm`, and `/rn:dn`: Lane holds the main conversation to the steps of the skill that called the run, so `lane/rules.json` gives the steps of `rn:up` alone, and the steps of the skills that move the run go unheld.
- Steps of each role: `domain/orchestrator.md`, `generator.md`, and `evaluator.md` name none of Lane's reporters, `lane-step`, `lane-item`, and `lane-result`, so no step, item, or result that `lane/rules.json` and `lane/adapters/rules.py` give is ever marked done.
