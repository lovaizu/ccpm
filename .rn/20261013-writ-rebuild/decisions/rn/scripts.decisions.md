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
- `session` also gives the sign-off waiting for the user's answer, the last proposal commit with no
  `Rn-Answer:` commit after it, and `answer approved|feedback --message` keeps the user's answer as
  a move marked `Rn-Answer: <answer> <sign-off>`, refusing where no sign-off waits: `/rn:ty` and
  `/rn:gm` then act only on a proposal the user was shown, read from what is pushed rather than a
  key the conductor writes, and the learner's stretch ends at each answer.
- Every CCS but the plan's names the plan as a source: each work traces back to the goal through
  the criteria it serves (rn's Principle 1), and turn's roles read only what the CCS names.
- The deliverable's CCS names, as its work, every file the branch changed outside `.rn/`, and its
  kind `deliverable` has rn's checklist `checklists/session/deliverable.md`, asking that the
  finished work, used as the user would, does each acceptance criterion: the UX has an AI that did
  not make it use the finished work for each criterion before the deliverable sign-off, and which
  files the work is, a machine can tell.
- The plan's Documents list each document as `- <name>: <path>`, its name the one its decisions and
  CCS take, held by the plan's form: the design proposal finds each document and its decisions from
  it.
- The design proposal gives, under the pull request's link, each document's link on the branch and
  its decisions, one line each; the deliverable's gives the criteria and each task's decisions; at
  every sign-off a proposal again shows what changed. A work with more than five decisions, or one
  longer than 200 characters, stops the proposal: the UX takes a core that does not fit in a few
  short lines as a sign the work is not yet simple, and five lines of a line each is what a glance
  takes in.
- Dropped from rn 0.9.0's scripts: `state key=value`, `--decisions`, `--reference`, and turn's
  items in the proposal, as the state is now a CCS replaced whole and a proposal shows only what
  the UX's Sign-offs gives.
