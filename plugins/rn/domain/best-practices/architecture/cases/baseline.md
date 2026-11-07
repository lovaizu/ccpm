# Baseline

The shortfalls of the designs made under the architecture best practice before this one, which
its questions must catch, as the meta's Q10 asks of a best practice made from real cases. Each
names the question that catches it. The designs are `dev/lane/architecture.md` and
`dev/rn/architecture.md`, and the code built from them had one module of 1,342 lines and tests
written after it, as [the code best practice's baseline](../../code/cases/baseline.md) says.

| Shortfall | Where it shows | Question |
| --- | --- | --- |
| Neither design states a quality its structure must meet as a scenario with a measure. Each choice argues from the product vision's key results, so no driver asks that a part change or run in a test on its own. | Neither has a section of qualities, and no line names modifiability or testability. | Q1 |
| One list mixes levels of abstraction. Lane's Components sets the user, the process `lay.py`, the module `step.py`, and the folder of modules `lanes/` side by side. | `dev/lane/architecture.md:248` to `:285` | Q2 |
| A component holds unrelated decisions. Lane's guard.py decides "which checks run on an event, whether a run is on, and what the role, the main conversation, and whoever runs the plugin hear from it," and grew to 1,342 lines. rn's tree.py decides a dozen, from the tree's form to the draft pull request, with no component inside it. | `dev/lane/architecture.md:268`, `dev/rn/architecture.md:174`, `plugins/lane/hooks/lane/domain/guard.py` | Q2 |
| Neither design says which component may depend on which. guard.py imports every other module, and reads the clock, the environment, and files itself, so no test runs its rules without them. | `plugins/lane/hooks/lane/domain/guard.py:52` to `:60`, `:301`, `:473`, `:801` | Q3 |
| The data model leaves every field to the code, and gives a contract only for what the user writes. The data that passes between Lane's components, such as a kept call, has none. | `dev/lane/architecture.md:426`: "The fields of each data lie where the code builds it." | Q4 |
| The design changes with fixes inside a component: 63 commits changed Lane's, such as `eae91a0d`, on how a path that a lane takes reads. | `git log --oneline -- dev/lane/architecture.md` | Q8 |
| Both test their main processes `FULL` at unit and again at architecture, so the slower level repeats each case. | `dev/lane/architecture.md:953`, `dev/rn/architecture.md:538` | Q9 |
| The Tests sections give the levels and how far each tries a process, and no test for any path of a sequence, and the tests came after the code. | `dev/lane/architecture.md:939`, `dev/rn/architecture.md:530`, and the code best practice's baseline | Q10, and the code best practice's Q8 |
