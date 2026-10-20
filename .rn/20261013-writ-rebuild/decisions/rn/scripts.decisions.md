# What rn's scripts do

rn's scripts serve the conductor as the design (`dev/rn/design.md`, Physical view) says: find a
kind's checklists, write a work's CCS, put the proposal together, and read and write where the
session stands. This unit builds what the first unit needs, from `/rn:up <what they want>` to the
plan sign-off; later units add to the same scripts.

## Form

- One command, `rn/scripts/rn.py <subcommand> ...`, run as `python3
  "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"` from the top of the user's repository, as turn's
  `turn.py` is; Python 3.9 or later, standard library only; it prints JSON or the text the
  conductor shows, and on a stop exits 1 with what went wrong and what to do.
- Tests in `dev/rn/tests/` with unittest, every line and branch run, every mutant caught by Cosmic
  Ray with `dev/rn/cosmic-ray.toml` as `dev/turn/cosmic-ray.toml` is set, property tests with
  Hypothesis where an input varies, as turn's are (`dev/turn/tests/`).
- The scripts never commit or push; the conductor alone does.

## Subcommands for the first unit

- `session`: the session the checked-out branch is in: the folder `.rn/<yyyymmdd>-<slug>/` the
  branch changed from the default branch whose `steering.md` front matter `status` is not
  `finished`; prints its path and its state, or that there is none.
- `start <slug>`: makes the session's folder `.rn/<yyyymmdd>-<slug>/` with today's date and its
  `state.json`, for the conductor to commit on the branch it made; stops where the slug is not
  lowercase letters, digits and hyphens, or the folder is there.
- `checklists <kind>`: the paths of the checklists for a kind: rn's own
  `${CLAUDE_PLUGIN_ROOT}/checklists/**/<kind>.md`, and the user's addition
  `.rn/checklists/<kind>.md` where it is there; stops where neither is there, saying a checklist
  for that kind is to be made first.
- `ccs <work> <path of the work> --kind <kind> --receiver <who> --use <what for> --has <path>
  [--has <path>]... [--decisions <path>] [--reference <path>]...`: writes
  `<session>/ccs/<work>.json`, with the work, the receiver, what it is used for, each path of what
  the receiver has with it, the kind's checklists, the decisions and references, and the
  conversation's and the artifacts' languages from the plan; prints the call to hand turn's
  `turn:up`, with the result at `<session>/ccs/<work>-result.json`.
- `state [<key>=<value>]...`: prints where the session stands from `state.json`, or sets the keys
  given: the stage (`asking`, `plan`, `documents`, `tasks`, `deliverable`, `lessons`, `ready`) and
  the sign-off it waits at, if any, with the feedback kept for it.
- `proposal <work>`: puts the proposal together from `<session>/ccs/<work>-result.json`, the plan
  and `state.json`: the three sign-offs, done, current and ahead; what changed since the last
  proposal at this sign-off; the pull request's link from the plan's `pr`; and each item of the
  work's checklists with its Good and lines, or what it still lacks; it keeps the items it showed
  in `state.json`, for the next proposal's "what changed".
