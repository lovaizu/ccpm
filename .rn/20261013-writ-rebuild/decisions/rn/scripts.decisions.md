# What rn's scripts do

rn's scripts hold the conductor's moves a machine can judge, as `dev/rn/architecture.md` says; what
each subcommand takes and gives is in `rn/scripts/rn.py`. Kept here is why it is so.

- The scripts commit and push each move, `state --message` and `start --message`, rather than
  leaving it to the conductor: a move is kept whole or not at all, and a rule written only in the
  skill's words is followed by chance.
- `state` commits every change, `git add -A`, and refuses a move that changed files with
  `state.json` as kept last: the state is replaced whole at every move (rn's Principle 2), so a
  move without a new state is a slip.
- A plan out of the template of rn's plan checklist F-1 is refused, not kept, with how to undo it:
  the session reads the plan by its IDs and front matter, and a plan kept out of form halts every
  later move.
- `ccs` refuses changes not committed or pushed: turn makes the work from the decisions, and a
  fresh conversation goes on only from what is pushed.
- A CCS names the work's decisions by its name, `decisions/<work>.decisions.md`, the kind's
  checklists, the user's addition, rn's `usability.md` for a checklist, and rn's checklist for a
  fix: every work comes from its decisions, and every change turn makes is a fix.
- A proposal is made from the pushed record alone and kept as an empty commit marked
  `Rn-Sign-off: <sign-off>`, so the next proposal at the same sign-off shows what changed since.
- Dropped from rn 0.9.0's scripts: `state key=value`, `--decisions`, `--reference`, and turn's
  items in the proposal, as the state is now a CCS replaced whole and a proposal shows only what
  the UX's Sign-offs gives.
