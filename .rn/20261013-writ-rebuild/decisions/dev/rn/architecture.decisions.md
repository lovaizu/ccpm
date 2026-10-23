# What rn's design says

## Concept, agreed with the user (2026-10-23)

- User: whoever wants to hand a whole piece of work, even work of days, to an agent.
- Purpose: they ask without preparing anything, only answer what they are asked, and their purpose
  is achieved.
- Concept: rn keeps the work aimed at the purpose and its execution straight, against two drifts:
  the work drifting from the purpose, kept by a plan whose every task traces to the purpose and by
  replanning at every move; and the AI itself drifting, kept by a short state replaced at every move
  and by guards. The conductor asks the user only the points that are theirs, one per message, and
  takes their approval at three sign-offs: the plan, the documents, the finished work. Each work is
  made through turn.
- rn's own principles: (1) every task traces back to the purpose, through the acceptance criteria
  it serves; (2) at every move the conductor replaces a short state with the checked facts alone,
  and replans from that state alone.
- Means, decided in the architecture and named there plainly: the short state is ACC's CCS
  (`state.json`, https://arxiv.org/abs/2601.11653), and each work goes to turn as a CCS; each rule a
  machine can judge is stopped at the moment by lane's guard. ACC and CCS are means, not
  principles.

The design is read by whoever builds or changes rn; it is remade on dev/architecture.md after lane
and turn, and replaces what dev/rn/design.md says now where the two differ.

## design

### B-2, B-3: The components and how they work
- rn has no step that finishes a work after turn returns it; dev/rn/design.md:105-108, where the
  conductor reads each Good and fixes a few lines by hand, goes (the user, 2026-10-21).
  - A question goes to the user while turn runs, by message from turn's orchestrator through rn's
    orchestrator to the front, and turn goes on with the answer (dev/architecture.md, A plugin
    that uses another).
  - Each Good is read at its lines by turn's first user; rn's script checks only that the lines
    exist and every item is there.
  - What would be a fix by hand is settled in the hearing before turn runs, as a decision; a change
    the user asks at a sign-off is written into the decisions, and turn goes on from its last step.
  - The front only talks, and a fix by the orchestrator would be work no hook keeps, while a finisher
    holds no more than turn's maker does and returns its fix unread by a first user.

## Moved out of the architecture, for tests and steps (2026-10-23)

- [step: up] On `/rn:up <what they want>`, the conductor finds the points to decide from the user's words, the repository and its documentation; a point read from them is still confirmed, as the UX says.
- [test: lanes] The guard stops a move that would let a sign-off pass without the user's `/rn:ty`, keep a plan outside the form rn's checklist for plans gives, start a work before the decision it follows is kept, start a task's making before its steps before it are ticked, or keep a change anywhere but the piece of work's own branch; a rule in words is followed by chance, a stop at the moment holds every time.
- [step: up] After the plan sign-off, the conductor confirms with the user, as a point, which documents the purpose needs, and has each made from the one before it, the UX, then the README, then the design; the design is built to what the README promises.
- [step: up] What of the README only the built work can give, such as how to install it and its links, is the last task, made and used by turn's first user as every task is; how the work is installed is known only once it is built.
- [step: up] After the design sign-off, the conductor writes the tasks into the plan, each a part a user of the finished work can try, with its completion criterion, the acceptance criteria it names, and its steps, each a box ticked when done: read the context it needs and confirm what is lacking (the conductor, with the user); design the part it makes and how that part is checked (turn, first run); trace the design on paper against its checks (that run's first user); make it, checked as it grows, code test first (turn, second run); a task begun on a gap fills it with a guess, and checks designed and traced before the making show its slips while they are small.
- [step: up] The steps are written in every task, their content its own, and what is done inside a step stays in the commits and the records; a step written only where it differs leaves the others unseen and skipped.
- [step: up] A task's design goes into the part of the project's design document it changes, or into the task's decisions where the purpose needs no design document, and its checks into the project's tests, written before the making and failing; so nothing is made that no one uses once the work is done.
- [step: up] Where the project keeps its design document, its tests and how they are written is read from the repository first, and only what it does not say is confirmed with the user, with the documents after the plan sign-off; the answer goes where the project keeps such rules, or, where it keeps none, a fact every piece of work needs into `CLAUDE.md` and a rule for one part into a rule file scoped to that part by `paths`, since Claude Code loads `CLAUDE.md` in every session and such a rule only once a file it names is read or written; so no later piece of work asks it again.
- [step: up] A checklist or an environment a task lacks, such as a tool to install, becomes a task of its own before the task that needs it; a work made without it is made to a guess and made again.
- [step: up] Each change to the plan, a learning's place among them, is decided from the architecture; a change decided case by case drifts from the others.
- [step: up] While turn runs, the conductor passes each line turn tells on to the user in the conversation's language.
- [step: up] The conductor keeps each lesson in the record as turn returns it, so a piece of work gone on in several conversations still has them all.
- [test: scripts] A fresh `/rn:up` goes on with the piece of work whose folder the checked-out branch changed from the default branch and whose plan is not finished; the folders of merged ones stay in the repository, finished, so they are never taken up again, and those rn 0.9.0 left are found the same way.
