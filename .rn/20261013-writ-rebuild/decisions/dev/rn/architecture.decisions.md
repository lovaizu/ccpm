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
