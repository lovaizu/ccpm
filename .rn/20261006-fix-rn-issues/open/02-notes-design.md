# Where the design stood when paused

- The design points are agreed and written in `01-notes-design.md`; no point is waiting on the user.
- `writ` had been called for `rn/README.md` and `rn/docs/design.md` (in parallel, by a
  general-purpose agent each running `writ:up`); both were stopped at the pause and left no edits. The
  verification document had not been started. Next: call `writ` again, once per document, README and
  design document first, then the verification document.
- Found while waiting: each `writ` agent, started from the main conversation, ended its own turn
  "waiting for pith" and returned without a result, since pith's agents ran in the background too.
  A caller cannot get `writ`'s result this way, the same fault as #44 one level down; the design's
  way of waiting has to hold for agents an agent starts, and `writ` must be called so that it returns
  its result.
