# What rn's scripts do

rn's scripts hold the orchestrator's moves a machine can judge, as `dev/rn/architecture.md` says;
what each subcommand takes and gives is in `rn/scripts/rn.py`. Kept here is what they must do, and
why.

## The record

- A session's folder `.rn/<yyyymmdd>-<slug>/` holds `steering.md` and `turn/` alone; `state.json`,
  `decisions/`, `ccs/` and `learnt/` go, and nothing of them is read: the steering is the plan and
  where the session stands, each call to turn is the files of one number, and the log is git's
  history (agreed with the user, 2026-10-24).
- A call is `turn/<nnnn>-ccs.json`, `turn/<nnnn>-result.json` where turn returned, and
  `turn/<nnnn>-steering.md` where the call makes a part of the steering; four digits from `0001`, in
  the order made; the work's name is in its CCS, `focal_entities` `{"work": "<name>"}`, with
  `{"stage": "<stage>"}` the stage it was made in. A work's latest call is the highest number naming
  it.
- Works are named `plan`, the part of the steering from the title to the tasks, `learnings`, its
  learnings, `t<n>` for what task T<n> makes outside the steering, `deliverable`, and
  `checklist-<kind>`. A task of the plan stage makes the plan, so its calls are on `plan`, and its
  points are decisions of `plan`.
  - Why: the tasks are made from the goal and the criteria and change with them, so one part holds
    the three; a task of the plan stage serves the goal by making the criteria.

## The steering's form

The form is rn's plan checklist's F-1 (`rn/checklists/session/plan.md`), held at every keep:

```markdown
---
rn: <rn's version>
pr: <the pull request's URL>
stage: <plan, design, build, deliverable, learnings or finished>
signoff: <none, plan, design or deliverable>
artifact-language: <the language of everything rn writes into the repository>
conversation-language: <the language rn speaks to the user in>
---

# <The piece of work, in a few words>

G1: <the user's purpose, with why they want it>

## Acceptance criteria

- AC1: <one thing the finished work must do for the goal>

## Tasks

- [ ] T1: <the part of the piece of work>. Serves <G1, or the criteria by ID>.

  Completion criterion: <what its result must do for what it serves, and the check that shows it>

  - [ ] 1. Read <the context it needs>, finding out <what it must>; confirm <what is lacking>. The orchestrator, with the user.
  - [ ] 2. Design <the part it makes> and <how that part is checked>. turn, first run.
  - [ ] 3. Trace <the design> on paper, or try it, against <its checks>. That run's first reader.
  - [ ] 4. Make <the part>, checked as it grows, code test first. turn, second run.

## Learnings

- L1: <what happened, with the words it rests on, and where it would make later work better>

## Next

<the step of /rn:up to take next, by its number, and on what>

## Open

- <what is open>
```

- A task has the steps it needs, numbered from 1, each saying who does it, the four above for a
  part made.
- The goal, the criteria, the tasks and the learnings are each there once made: a steering without
  them holds its form until the move that needs them: the plan proposal needs G1, a criterion and
  every task ticked. `## Open` holds `None.` where nothing is open. IDs are as F-1 says, each once;
  a task serves only IDs the steering holds.
- Why strict: the scripts read the front matter, the IDs, the ticks, Next and Open by these names,
  and the user reads the same file at each sign-off, so a steering out of form would halt the
  session and mislead the user at once.

## Who writes what

- The steering is written by the scripts alone; a keep refuses a steering that differs from what the
  last keep left, with how to restore it. turn makes the goal and criteria, the tasks and the
  learnings in the part file; the orchestrator gives the rest as arguments.
  - Why: turn sees only the part it makes, and the steering always says what was kept, never a hand
    edit no check read.
- `start <slug> --title <t> --artifact-language <a> --conversation-language <c> --next <n> --message
  <m>`: the branch from the latest default branch; the steering with `rn` from
  `.claude-plugin/plugin.json`, `stage: plan`, `signoff: none`, the title, Next and `Open: None.`;
  committed, pushed, the draft pull request opened with `gh pr create --draft`, its body linking the
  steering, and its URL kept as `pr`, committed and pushed. Stops on changes not committed.
  - Why: the session has a place to be kept and shown before any point is asked, and the scripts
    alone write the steering.
- `state --next <n> [--open <o>]... [--done T<n>.<step>]... [--put <nnnn>] [--stage
  deliverable|finished] --message <m>`: Next and Open replaced whole; each step ticked, and the task
  once all its steps are; the call's part put back into the steering where `--put` names a call
  whose result is there, a ticked task or step as it was and each learning numbered on from those
  kept, refused otherwise; the stage moved from build to deliverable where every task is ticked, and
  from learnings to finished; then the form held, every change committed, `git add -A`, and pushed.
  - Why: where the session stands is rewritten whole at every move (rn's Principle 2), and a move is
    kept whole or not at all; the stage moves at the sign-offs otherwise.
- `decide <work> --title <t> --says <s> --message <m>`: a decision `{"decision": "<t>: <s>"}` in the
  `constraints` of the work's latest call where it has no result, else of a new call carrying the
  latest call's decisions; one of the same title is replaced; kept and pushed.
  - Why: each answer is kept before the next move, with the call made from it (agreed: a work's
    decisions are entries of its CCS).
- `ccs <work> [<path>...] --kind <kind> --receiver <r> --use <u> [--has <path>]...`: refuses changes
  not pushed; fills the work's latest call where it has no result, else a new one carrying its
  decisions; for `plan` and `learnings`, cuts their sections into `turn/<nnnn>-steering.md`, the
  work, for `learnings` with none of the learnings kept before; the deliverable's work is every file
  the branch changed outside `.rn/`. The CCS holds the work, the stage, the receiver, what they
  have, the use, the goal and the criteria the work serves as text in `goal_orientation` (for `t<n>`
  those its task line serves; for every other work G1 and every criterion), the kind's checklists,
  rn's `usability.md` for a checklist, the decisions, the two languages and rn's `fix.md`. Prints
  the call to turn.
  - Why: turn makes the work from what was decided and pushed alone; what it only reads is text in
    the CCS, what it makes a file (agreed with the user, 2026-10-24).
- `proposal plan|design|deliverable`: the proposal from the pushed steering and calls alone;
  `signoff` set and kept where it was `none`, shown again unchanged where it is the same. Plan:
  stage plan, G1 and the criteria; design: stage design, each task made in the design stage with its
  works' links on the branch and its decisions, from each `t<n>` and `checklist-<kind>` called in
  the design stage; deliverable: stage deliverable, the criteria and the decisions of each `t<n>`
  called in the build stage. Each shows what changed since the last proposal at the same sign-off,
  found in the steering's history; a work of more than five decisions, or one of more than 200
  characters, stops it.
  - Why: the user decides from the core decisions alone, and a core that does not fit is a sign the
    work is not yet simple (the UX's Sign-offs).
- `answer approved|feedback --next <n> [--open <o>]... --message <m>`: refuses where `signoff` is
  `none`; approved moves the stage, plan to design, design to build, deliverable to learnings; both
  set `signoff: none` and Next and Open; kept and pushed.
  - Why: `/rn:ty` and `/rn:gm` act only on a proposal the user was shown, and the steering always
    says where the session stands.
- `session`: the session the branch is in, one whose steering's stage is not `finished`, with the
  stage and the sign-off waiting; null for each where there is none.
- `checklists <kind>`: rn's own, then the user's addition.
- `records`: the stretch since the last call on `learnings` with a result, or since the branch left
  the default branch, as texts in the git folder: its history, the session's files, and the
  orchestrator's conversations of it; prints their paths, the `--has` of the learnings' call. `state
  --put` of that call removes them.
- `learnings`: the steering's learnings and those of every version of each result on the branch.
- Dropped: `learnt`, `lessons`, the `Rn-Sign-off:` and `Rn-Answer:` trailers, and the state's check,
  as the steering's front matter holds the sign-off and the steering is rewritten by the scripts at
  every keep.
