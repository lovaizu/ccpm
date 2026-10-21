# What rn's design says

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
