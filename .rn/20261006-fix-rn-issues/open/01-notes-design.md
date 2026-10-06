# Design points for rn, from the audit of 0.9.0

Sources: steering.md (Facts on the audit), issues #39, #41, #43, #44, #45, #46, `rn/docs/design.md`,
`rn/references/conduct.md`, `rn/hooks/`.

## Quality is built in by whoever makes a thing

- Every maker writes to the viewpoints of what it makes: the conductor to `conductor.md`, `plan.md`
  and `design.md` for what it writes and says, a generator to its task's viewpoint file, `writ` to
  its own. The viewpoints are the form a thing is written in, not only the questions it is checked by.

    0.9.0 wrote first and checked after, by a first user, for everything the conductor wrote; the
    check found what writing to the viewpoints would have avoided (#45), at the cost of a run each.

## A first user uses only what use shows

- A first user is started for a task result and for the deliverable's scenes, where running the work
  shows what its maker cannot see. A question, the plan, a proposal, and a report are not used by a
  first user; the conductor writes them to their viewpoints, and the user reads them.
- Decided by the conductor on the user's "go on", over a first user trying to build from the design
  points before `writ` writes (one run more per design) and over today's use of everything; shown to
  the user at the Design sign-off.
- Each thing is used once; a fix of an attractive More is used once more, on that point alone; nothing
  else starts a first user. `report.md` goes, since nothing uses a report.

    Unbounded use was the cause of #39 and of the length in #46: every run added a report and every
    fix a run.

## What the user reads is bounded by what they decide (#46)

- A stop gives the map, the conductor's view of how close each attractive criterion has come, each
  point the user decides (a More left, an `Assumption`, something taken away), and the next move with
  why. The goal, the criteria, and every Good and More stay whole in the record and on the pull
  request, not in the message.
- The same holds for every short result an agent returns to its caller, `writ`'s and pith's
  included, and is written once in `.claude/rules/plugin.md` § Results.

## The design stage calls writ once per document (#39)

- Before `writ` is called, the conductor reads the agreed design points against `design.md` as a
  writer would, and settles every gap it finds; gaps that do not depend on each other go to the user
  together.
- A point `writ` still returns is settled, and handed to `writ` with its result file, so it fixes
  only what the point touches.

## The user is asked only what is theirs (#45)

- A point is put to the user only when the goal, the request, and the repository leave more than one
  answer that gives the user something different; what they settle is written as a Fact naming where.

## The hooks hold only what a machine can tell, in the conductor's own session (#43, #44)

- `/rn:on` and `/rn:up` record the session id of the conversation that runs rn; every conductor check
  applies only to that session and to the agents it started. Another session passes, and a message to
  another session is never stopped.
- The conductor waits for the agents it started by ending its turn with one line on what runs; the
  agent's return wakes it. The turn-end check that sends the conductor on is removed, since it is what
  forbids that wait and what sent another session on with rn's work.
- An approval is recorded after the user has spoken since the stop, in words or by `/rn:ty`; a commit
  that records one with no user message since the stop is stopped.
- The verification document's coverage is checked only once the design writes it, from the Design
  sign-off on.
- Removed with the first user's use of questions: the check that a settled report on a question lets
  no More go.
- Kept: the record's form, the decision line, pushed commits, only the conductor uses git, the first
  user's reads and writes kept to its own, the conversation-language check, and the record read again
  after Claude Code summarizes the conversation.

## What the user sees taken away

- No first user takes up a question, the plan, or a proposal before the user reads it; the user is
  the first reader of what the conductor writes.
- A proposal no longer repeats the goal, every criterion, and every Good and More; they are on the
  pull request.
- `/rn:ty` is no longer the only way to approve; saying so in words is recorded the same.

## /rn:on keeps the branch the user started on (#41)

- When the current branch is not the default branch, has no commits of its own, and is at the latest
  default branch, `/rn:on` works on it and pushes it under the same name.

## rn is checked by running a whole session

- The verification document adds a run of one session from `/rn:on` to the Design sign-off on the
  practice repository, measuring the time it takes, the lines the user reads at each stop, and what the
  user was asked, against rn 0.9.0's run.

## writ is run in the conductor's own conversation

- The conductor runs `writ:up` itself with the Skill tool, not through an agent: an agent's own agents
  report after it has returned, so a `writ` run inside an agent returns without its result. pith,
  called from the conductor's conversation, returned its result whole (`open/03-report-readme.md`).
