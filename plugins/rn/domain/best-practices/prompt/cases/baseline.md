# Baseline

The shortfalls of prompts made before this best practice, which its questions must catch, as the
meta's Q10 asks of a best practice made from real cases. The prompts are rn's roles and Lane's
guide for the AI that proposes lanes, and the briefs this project's main conversation wrote for its
makers. Each names the question that catches it.

| Shortfall | Where it shows | Question |
| --- | --- | --- |
| The orchestrator never reads the design tree by its words alone: the skill's `allowed-tools` only approves `tree.py` ahead, and no guard holds a read in the main conversation. | `plugins/rn/skills/up/SKILL.md:5`, and `plugins/rn/domain/up.md:6`: "you never read the design tree" | Q7, Q8 |
| Each role's last step allows one command alone, then has the role run another, with a sentence saying the first rule doesn't cover it. | `plugins/rn/domain/evaluator.md:30`, `plugins/rn/domain/generator.md:31`, and `plugins/rn/domain/planner.md:36`, "so an instruction not to run the work's scripts doesn't cover it" | Q14 |
| One step bundles the making, the record's fields, its form, a file never to read, and the commands the role may run. | `plugins/rn/domain/generator.md:29` | Q5 |
| A rule never to read the tree stands twice in one prompt, in words that differ. | `plugins/rn/domain/planner.md:29-30` and `:34`, and `plugins/rn/domain/generator.md:24` and `:29` | Q14 |
| A step names one command three times. | `plugins/rn/domain/evaluator.md:30` and `plugins/rn/domain/generator.md:31`, `tree.py record` | Q15 |
| The orchestrator's way of judging a point lies behind a question number of another best practice, two links from the skill, and moves when someone makes that best practice again. | `plugins/rn/domain/up.md:47-48`: "as Q17 of `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/plugin/best-practice.md` says" | Q2, Q15 |
| The guide that the AI reads to propose lanes runs 195 lines under its title before its next heading, and 446 in all, with no list of its contents. | `plugins/lane/docs/lanes.md:2-3`: "the proposal your AI writes them in" | Q15 |
| The brief that had a subagent build rn's code pointed at a rule file and a best practice, and held no step and no guard for the tests first, so the maker wrote the unit tests after the code. | rn's code, `52847bd9` to `ca1839c6`, and the maintainer's record of the session, 2026-11-08 | Q5, Q8 |
| Feedback kept only in the main conversation's notes never reached the subagents that did the work, so the same fault came back. | The maintainer's record of the session, 2026-11-04 | Q2 |
| Trials ran with a judge and a stand-in that no one had tried on kept records, on a throwaway check that was itself broken, and five rules went into a role's prompt from the judge's verdicts. | Turn's trials, before its removal in `52847bd9`, and the maintainer's record of the session, 2026-11-07 | Q16 |
| A planner left the setup out of the commands its people run, so each try of the deliverable gave `tidy: not found`, and no step held the try before a role wrote its answers. | Turn's trials, and the maintainer's record of the session, 2026-11-07 | Q1, Q8 |
