# What rn's trials do

The conductor's flow trial tries rn's skills over the whole course, from `/rn:up <what they want>`
to the pull request marked ready, as `dev/rn/architecture.md` Verification, Units, "The conductor",
Flow, gives it: the real skills, scripts, learner and its lanes, with turn and the user stood in
for, on the smallest request that reaches each move: one point or more to decide, one criterion,
one document and one task.

## Form

- `dev/rn/trials/flow/flow.py`, run as `python3 dev/rn/trials/flow/flow.py <new folder>`, with
  its stand-in for turn beside it in `dev/rn/trials/flow/`: copies of rn and turn as they are when
  the trial starts, the copy of turn's `turn:up` agent replaced by the stand-in.
- It runs in a fresh clone of `lovaizu/playground` in the new folder; the session's branch on the
  playground and its pull request are removed when the run ends, whether it passed, failed or
  stopped; the clone is left in the folder to read.
- Each message of the user is a `claude -p` call by lane's `dev/lane/trying.py` `claude`, which
  takes the conversation to go on with (`--resume <session id>`) where one is given; a fresh
  conversation is a call without it. It waits for the stand-in in the background, as turn's trials
  do.
- Code in `dev/rn/trials/` is out of the line count, mutation testing and property tests, its run
  being its check; Python 3 with the standard library alone, checked by ruff and the type checker.

## turn's stand-in

- An agent `turn:up` in the copy of turn, on a fast model, given the call as its prompt as the
  real one is. It reads the CCS, sends the main conversation one line beginning `turn:` by
  SendMessage, as turn's runs do, writes the work at each path the CCS names, and writes the
  result with a script beside it, every item of every checklist the CCS names with a Good at the
  work's first line and no lesson, then replies `{"returned": "<result>"}`.
- The plan it writes from the plan's decisions in the template of rn's plan checklist F-1, its
  front matter taken from them, a goal, the criteria, the Documents and the Tasks the decisions
  hold, each in its form; any other work as a few lines saying what its decisions say; the
  finished work it leaves as it is.
- What the stand-in makes is not what is judged: the trial judges the conductor's moves.

## The stand-in user

- The request: `/rn:up add a line greeting new contributors to the README`.
- Each reply of rn is answered by what it holds, at most 60 messages in all:
  - "Plan sign-off": the first time `/rn:gm the greeting should name the CONTRIBUTING file too`;
    after that, `/rn:ty`.
  - "Design sign-off" or "Deliverable sign-off": `/rn:ty`.
  - "feedback is kept": a fresh conversation, `/rn:up`.
  - "ready to merge": the run ends.
  - anything else, a point, a learning or a line of turn's: `a`, the recommended option.
- Each `/rn:ty` and `/rn:gm` goes on the same conversation, as the user types them where they read
  the proposal.

## What it prints

- Each conversation's session ID, each message sent and the last lines of each reply, from whose
  JSONL the run is judged; the commits on the session's branch with the files each changed and its
  trailers; whether each commit but a proposal's changed `state.json`; the learner's stops and
  `learnt/` files; the pull request's state at the end; the minutes and the cost.

## What passes

- The commits show each move in the architecture's order: the start, each point kept before the
  next, the plan, the plan proposal, the feedback, the plan made again, the plan proposal with what
  changed, the approval, the lessons kept, the documents' points, the plan with its Documents, the
  document, the design proposal, the approval, the lessons, the tasks into the plan, the task's
  steps ticked, the deliverable, its proposal, the approval, the lessons, each learning's answer,
  `status: finished`; each commit but a proposal's replaces `state.json`; nothing is committed on
  the default branch; the pull request is ready.
- The JSONL shows each point asked alone in its message in the README's form, each `turn:` line
  passed on, each proposal given as `rn.py proposal` printed it, and the learner's lanes stopping
  only where their checks should.
