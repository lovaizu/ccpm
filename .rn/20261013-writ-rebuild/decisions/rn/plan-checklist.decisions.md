# What rn's checklist for plans says

The work is `rn/checklists/session/plan.md`, rn's checklist for the kind `plan`, made again to the
design (`dev/rn/design.md`) and the README (`rn/README.md`), which the plan of 0.9.0 does not
follow.

## Who uses a plan, and for what

- The user reads the plan at the plan sign-off, to approve what the finished work will do and why,
  or to send it back.
- The conductor reads it in every later conversation, to go on to the user's purpose without asking
  again, and writes the tasks into it after the design sign-off.
- turn makes each later work with the plan as what it is used for: the documents, each task's
  result serving the acceptance criteria it names, and the finished work used for every criterion.

## What a plan holds

- The front matter: `rn` (the installed rn version), `pr` (the pull request's URL), `status`
  (`running`, or `finished` once the pull request is marked ready), `artifact-language` and
  `conversation-language`; rn's script reads `pr`, `status` and the two languages by these names.
- The goal, with the ID `G1`: the user's purpose as rn wrote it down, with why they want it.
- The acceptance criteria, `AC1`, `AC2`...: each one thing the finished work must do for the goal,
  in a form the finished work can be checked against; together they give the whole goal. A changed
  criterion keeps its ID; a removed one's ID is not used again.
- The documents the purpose needs, such as a UX, a README or a design, each with its path, settled
  with the user after the plan sign-off; empty until then.
- The tasks, settled after the design sign-off, empty until then: each with an ID `T1`, `T2`..., a
  checkbox done when its result is taken, and the acceptance criteria it serves.
- Each task a thin slice, as the tracer bullets of `to-tickets` in `mattpocock/skills` (MIT) are
  cut: one thing a user of the finished work can try, through every part it needs, small enough for
  turn to make in one run, after every task it builds on. The building of rn itself showed why: its
  hooks asked of turn whole, four checks with their shared parts and tests in one run, took two hours
  and stopped in the first round with nothing taken.
- No sign-off is a task, and the plan holds no state of the session: where the session stands is in
  `state.json`.
- No split of the criteria into attractive and must-be quality: the README and the UX speak of
  acceptance criteria alone.
- Each point the plan rests on is in the plan's decisions (`decisions/plan.decisions.md`), confirmed
  with the user one per message, the looked-up ones included; the plan holds what was decided, not
  how.

## What the items ask

- Whether the user can tell from the plan alone why they want the goal, and that the criteria give
  all of it.
- Whether each criterion can be checked on the finished work, and says what it does for the goal
  rather than how it is built.
- Whether each criterion is the user's: a point it rests on was confirmed with them.
- Once the tasks are written: whether every criterion has a task serving it, and every task names
  the criteria it serves, and whether each is a thin slice tried on its own.
- The version is `0.1.0`: rn 0.9.0 released the plan's checklist as
  `rn/references/essentials/plan.md`, with no version and no item IDs, so no ID is taken.
