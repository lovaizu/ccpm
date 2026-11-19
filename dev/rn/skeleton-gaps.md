# rn's skeleton gaps

Each place where rn's skeleton, in `plugins/rn/`, can't follow
[the architecture](architecture.md) or the form that Lane takes in, for whoever makes the
architecture.

- Cut [P4.1], with P2.1 and P5.2: Lane names each start by its role alone, in the moves of `starts_due.in.schema.json` and in the `role` of `checklist.in.schema.json`, while several starts of one role run at once: an evaluator for each group, and a generator for each deliverable. So `lane/adapters/checklist.py` can't find the Cut whose best practice or conditions give a step's items, `lane/adapters/starts_due.py` counts the starts of a role that run but can't tell which Cut each holds, and `scripts/cut.py` takes the Cuts that run from the orchestrator, which no code holds once `/compact` drops them.
- Strategy of Lane applied to every activity of every role's steps [P5.1]: Lane's rules take fixed paths and commands, with no value of the start, so `lane/rules.json` can't hold the generator to writing only its deliverable and its result, an evaluator to never reading the design tree or its Round's generator's Cut and result, or either to `scripts/check.py <role> <Cut>` as its check, and it leaves these rules out.
- S1, the generator's point it can't settle [P1.2]: the generator ends with a point at its step 2, while Lane's `order` rule lets a role end only once it has done each step, so `lane/rules.json` gives the result `point` at step 4, where the generator never gets with a point.
- S1, the orchestrator's steps on `/rn:ty`, `/rn:gm`, and `/rn:dn`: Lane holds the main conversation to the steps of the skill that called the run, so `lane/rules.json` gives the steps of `rn:up` alone, and the steps of the skills that move the run go unheld.
- Run, the run's end once the user signs off the pull request [S1]: `starts_due.in.schema.json` doesn't say how a command move names the command, such as `/rn:ty` or `rn:ty`, so `lane/adapters/starts_due.py` can't yet be built to tell the `/rn:ty` that ends the run.
- Steps of each role: `domain/orchestrator.md`, `generator.md`, and `evaluator.md` name none of Lane's reporters, `lane-step`, `lane-item`, and `lane-result`, so no step, item, or result of `lane/rules.json` is ever marked done.
