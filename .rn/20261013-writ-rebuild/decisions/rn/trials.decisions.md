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
  real one is, doing turn's generator's part alone, as the conductor reads each Good at its lines
  and sends back a work whose lines do not give it. It reads the CCS, sends the main conversation
  one line beginning `turn:` by SendMessage, as turn's runs do, makes the work from its decisions
  and checklists, and claims each item's Good with the lines that give it in turn's claim form,
  checked by turn's own `forms.py`; a script beside it writes the claim as the result, with no
  lesson, then it replies `{"returned": "<result>"}`.
- A file of the work that is there changes only where its decisions say; a new one is written in
  the template of its checklist's F-1; the finished work it leaves as it is.
- What the stand-in makes is not what is judged: the trial judges the conductor's moves.

## The stand-in user

- The request: `/rn:up add a line greeting new contributors to the README`.
- Each reply of rn is answered by what the moves it kept hold, as its words are in the
  conversation language, at most 60 messages in all:
  - A plan proposal kept, `Rn-Sign-off: plan`: the first time `/rn:gm the greeting should name the
    CONTRIBUTING file too`; after that, `/rn:ty`.
  - A design or deliverable proposal kept: `/rn:ty`.
  - Feedback kept, `Rn-Answer: feedback`: a fresh conversation, `/rn:up`.
  - The pull request marked ready: the run ends.
  - A reply offering option `a.`, a point, a learning or a line of turn's: `a`, the recommended
    option; one offering none, such as whether to open an issue shown: `yes`, and where it keeps no
    move either, the run is stuck and ends.
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
