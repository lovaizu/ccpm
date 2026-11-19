# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md) or the form that Lane takes in, for whoever makes the
architecture.

- S2, each role stopped started again from its kept Cut [P6.1], with P5.2: Lane gives the main conversation each role due and how many, not which Cut, and `scripts/cut.py` sees no prompt of a start that runs. So where several starts of one role have a Cut and no result, such as three evaluators picked up after `/rn:dn`, or one whose start failed beside others of its role that run, `scripts/cut.py` gives each the first such Cut, and the same Cut goes to two starts.
- S1, the orchestrator's steps on `/rn:ty`, `/rn:gm`, and `/rn:dn`: Lane holds the main conversation to the steps of the skill that called the run, so `lane/rules.json` gives the steps of `rn:up` alone, and the steps of the skills that move the run go unheld.
- Steps of each role: `domain/orchestrator.md`, `generator.md`, and `evaluator.md` name none of Lane's reporters, `lane-step`, `lane-item`, and `lane-result`, so no step, item, or result that `lane/rules.json` and `lane/adapters/rules.py` give is ever marked done.
