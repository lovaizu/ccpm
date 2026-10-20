# What rn's trials do

The trial of the first unit tries the flow of rn's skills from `/rn:up <what they want>` to the
plan sign-off, as the design's Verification gives it for each skill (`dev/rn/design.md`,
Verification, Units, "Each skill", Flow): the real skills, scripts and hooks, with turn and the
user stood in for, on the smallest request. Later units add their steps to the same trial.

## Form

- `dev/rn/trials/flow/flow.py`, run as `python3 dev/rn/trials/flow/flow.py`, with what it stands
  in with beside it in `dev/rn/trials/flow/`, as turn's flow trial is (`dev/turn/trials/flow/`):
  copies of rn and turn as they are when the trial starts, turn's `turn:up` agent replaced in the
  copy by a stand-in agent that gives a result set beforehand.
- It runs in a fresh clone of `lovaizu/playground` in a new temporary folder, one run at a time;
  the session's branch, its pull request and the clone are removed when the run ends, whether it
  passed, failed or stopped.
- Each message of the user is a `claude -p` call on Opus with `--permission-mode auto`, the
  user's next words set beforehand; a message goes on the same conversation with `--resume`, and
  "a fresh conversation" is a new `claude -p` without it. `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`
  is set so `claude -p` waits for turn's stand-in in the background.
- It prints each conversation's session ID, from whose JSONL the run is judged, the commits on the
  session's branch, `state.json` after each message, the minutes and the cost; it keeps no record
  in the repository.
- Code in `dev/rn/trials/` is out of the line count, mutation testing and property tests, its
  run being its check, as plugin.md keeps it out of the line count; it is Python 3 with the
  standard library alone, checked by ruff and the type checker as the rest is.

## The run

- The request: `/rn:up add a line greeting new contributors to the README`.
- The stand-in user answers each point with `a`, the recommended option, until rn stops at the plan
  sign-off, at most ten answers; then sends `/rn:gm the greeting should name the CONTRIBUTING file
  too`; then, in a fresh conversation, `/rn:up`, answering each point with `a` until the same
  sign-off; then, in another fresh conversation, `/rn:ty`.
- turn's stand-in writes the plan at the path the CCS names, in the form of rn's plan checklist,
  its front matter taken from the session's `decisions/plan.decisions.md`, a goal and one
  criterion, and the result in the form turn writes, every item of the plan checklist and
  `usability.md` with a Good at the plan's lines; its second call writes the criterion changed, so
  the second proposal shows what changed.

## What passes

- The JSONL of the conversations shows each step of the skills in their order: the session looked
  for, the branch, `rn.py start`, the draft pull request, each point asked alone in its message
  with its answer kept by a commit and a push before the next, the CCS, turn's stand-in started in
  the background, the result read, the proposal given as `rn.py proposal plan` printed it; on
  `/rn:gm`, the feedback kept and the stop; on the fresh `/rn:up`, the point behind the feedback
  asked, the plan made again and the same sign-off shown with what changed; on `/rn:ty`, the
  approval kept.
- No hook of rn stops a move the steps take; where one stops a move, it is read in the JSONL
  whether the move broke its rule.
- The branch holds a commit for each keep the steps make, and nothing is committed on the default
  branch.
