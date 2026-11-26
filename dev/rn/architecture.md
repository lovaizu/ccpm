# rn architecture

## User stories

- S1: the user wants what they asked for working for the one need they pick, early, asking in
  their own words, and to decide what happens to each need left.
- S2: the user wants to stop a run and go on with it later, in any conversation, losing nothing.

## Solution strategy

### Principles

rn piles up the [vital few](https://en.wikipedia.org/wiki/Pareto_principle) that bring a
deliverable's people to their aim, and cuts the trivial many thoroughly.

- P1: the goal reached earliest
  - P1.1: each run aims at one need that the user picks.
  - P1.2: the least that runs, through every kind of deliverable that the need takes, goes to the
    user before anything more is made.
  - P1.3: a mend that keeps what the run decided starts at once, with no weighing before it.
- P2: the user as one who uses it
  - P2.1: the user is asked only what only they can decide, one point at a time, in plain words
    with a recommendation and why.
  - P2.2: each need that the user or the issue named stays on the list, and only the user decides
    what happens to it.
  - P2.3: each message to the user opens with where the run stands.
  - P2.4: rn talks in the user's language and writes in the repository's, asking only where they
    disagree.
- P3: best practices in full
  - P3.1: each deliverable, when first made or remade, meets every necessary condition of its
    kind's best practice before the user touches it.
  - P3.2: before the user, each deliverable is tried by one who didn't make it, with only what its
    people have.
  - P3.3: a remake that brings no remedy has a limit, and each finding left goes to the user as a
    proposal.
  - P3.4: a mend is checked by its kind's best practice, the repository's checks, and the unit
    tests.
- P4: one measure of the vital few
  - P4.1: each fact that would change what the run aims at is weighed by one shared measure, by
    one role alone, before it does.
- P5: each role on its own work
  - P5.1: leading, weighing, making, judging, and mending are separate roles, each started with
    only what its work needs.
  - P5.2: each part of the run's record has one writer.
  - P5.3: a step that has one right result is done the same way each time, without a role's
    judgment.
- P6: nothing lost on a stop
  - P6.1: the run's state lives in files on its branch, so that it goes on from any conversation.
  - P6.2: a stop lets each record being written end whole before the run halts.
- P7: the user's repository left as it was
  - P7.1: rn works on its own copy of the repository and its own branch.
  - P7.2: the ready mark and the merge stay the user's.

### Concept model

![rn's concepts](images/concept-model.svg)

- Steering\
  Holds what the run aims at and why, and where it stands, for each judgment and each pick-up.
  Its form is [its schema](../../plugins/rn/domain/schemas/steering.schema.json)'s.
- Opportunity\
  A need in the words of those who have it, which the user picks or leaves.
- Solution\
  How the picked need is met, with the riskiest assumption it rests on and that assumption's test
  on the real thing.
- Step\
  One stretch of the way to the picked need, which ends once the user says it's enough.
- Deliverable\
  One file or folder that a step makes for the people, of one kind.
- Best practice\
  The field's established way to make one kind of deliverable, and its conditions, which making
  and judging both stand on.
- Round\
  One making of a deliverable, tried by its maker and then judged by one who didn't make it.
- Fix\
  One mend of a deliverable whose Rounds are over, which keeps each decision of the run. It holds
  the problem in the words that raised it, and what the mend gave.

Strategies:

- The steering split into what the run aims at, written by one role alone, and where it stands,
  written by scripts alone. [P5.2]\
  Intent: no part of the record has two writers, and the run's standing moves the same way at
  each event.
- Each need kept on the tree, the one the user picked marked as the run's target. [P2.2]\
  Intent: no need is dropped without the user's say, and the run knows which one it serves.
- The steps listed in order, the walking skeleton first, each naming the need it meets.
  [P1.2]\
  Intent: the run puts the least that runs in the user's hands before it makes more.
- Each step marked open while rn makes it, trying while it's in the user's hands, and done once
  the user says it's enough. [P6.1]\
  Intent: the run's files alone say what waits for the user.
- Each point for the user kept as an open question, and their answer, word for word, as a
  decision of theirs. [P2.1]\
  Intent: a point and the user's own words outlive the conversation that asked them.
- Each remedy that a Round's judgment brings kept as a decision of the run. [P3.3]\
  Intent: the next Round and each later mend rest on what was weighed.
- A Round past the limit taken only where a remedy was written since the last. [P3.3]\
  Intent: each vital gap is mended before the limit ends the remaking.
- Each Fix kept beside the deliverable's Rounds, with the problem in the words that raised it.
  [P6.1]\
  Intent: a pick-up finds a Fix under way and starts it again on the same problem.

### Components

![rn's components](images/components.svg)

- orchestrator (prompt)\
  Leads the run to the user's picked need, as the user's one contact.
- vital few (prompt)\
  Holds the one measure by which rn tells the vital few from the trivial many.
- pruner (prompt)\
  Keeps what the run aims at to the vital few, with every need named kept for the user to pick.
- generator (prompt)\
  Makes a deliverable with which its people reach their aim, by its kind's best practice.
- evaluator (prompt)\
  Checks, as the people, whether a deliverable or the pull request whole reaches their aim.
- fixer (prompt)\
  Mends a made deliverable at once, within the run's decisions.
- scripts (script)\
  Does each step that has one right result, and alone writes where the run stands.
- hook (hook)\
  Turns each delete that a role runs in Bash to a script, on every call.

Strategies:

- Each command only an entry point, pointing to the orchestrator's steps for each event. [P5.1]\
  Intent: every event reaches the one role that hands it on.
- The main conversation as the orchestrator, which starts and stops each other role. [P5.1]\
  Intent: the user talks with one role through the run.
- Each fact that would change what the run aims at handed to a new pruner, with the run's folder,
  the user's words, and the fact. [P4.1]\
  Intent: one role holding the measure weighs all that the run aims at takes in, as an outsider
  would.
- One shared prompt of the measure, which both the orchestrator and the pruner read. [P4.1]\
  Intent: the two roles weigh by one measure, which changes in one place.
- The pruner's result handed to a script, which writes the steps into where the run stands.
  [P5.2]\
  Intent: the pruner decides the way, and only scripts write the run's standing.
- Each problem with a deliverable whose Rounds are over handed at once to a new fixer. [P1.3]\
  Intent: a mend within what was weighed starts without a wait, and one that changes it is
  weighed first, as the fixer names it.
- The orchestrator speaking only from the steering and the user's words. [P2.1]\
  Intent: the talk brings back nothing the pruner cut, such as an issue's means.
- Each need shown numbered in the user's words, and one of them recommended with its grounds. [P2.1]\
  Intent: the user judges only which need brings them closest to what they're after.
- The languages proposed once at the start and kept as the user's decisions. [P2.4]\
  Intent: the user reads rn in their own language, and others read the repository in its own.
- One generator and one evaluator for each Round, the evaluator judging every condition from one
  trial. [P3.2]\
  Intent: the people's use is one act, so it's tried once and judged whole.
- The evaluator given the deliverable and its best practice, never what rn meant. [P3.2]\
  Intent: it meets only what the people would meet.
- A new generator for the refactoring once each condition is good, with no evaluator. [P3.1]\
  Intent: a new reader meets what the maker misses, and the checks and tests show the intent
  holds.
- A new fixer for each Fix, with only the deliverable, its best practice, the run's decisions,
  and the problem in its own words. [P3.4]\
  Intent: the fixer mends what went wrong within what was decided.
- A fixer whose mend would change a decision mending nothing, and naming the change. [P4.1]\
  Intent: only a weighing changes what the run aims at.
- The pull request checked whole by an evaluator once each step is done, with its CI. [P3.2]\
  Intent: a newcomer to the work reads the whole diff before the merge is proposed.
- Each step that has one right result done by a script that the role runs. [P5.3]\
  Intent: each role spends its judgment and its context only where a step needs them.
- A stop taken from /rn:dn or the user's words, and a pick-up from /rn:up. [S2]\
  Intent: the user stops and goes on at the moment they choose, and a new run never asks about an
  old one.
- A stop waiting for each pruner at work to end, then stopping the other roles and pushing the
  run's folder. [P6.2]\
  Intent: a pick-up reads a whole steering, and GitHub keeps the work so far as well as the
  user's computer.
- Each role's delete in Bash sent by the hook to a script of exact paths. [P5.3]\
  Intent: a role's clean-up never waits on a permission prompt, and stays in the work and the
  temporary folder.

### Sequences

#### S1: the least that runs for the picked need, in the user's hands

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant P as pruner
  participant T as steering
  participant S as scripts
  participant G as generator
  participant E as evaluator
  participant F as fixer
  U->>O: /rn:on [S1]
  O->>U: asks what it can help with, an issue's number or a few words [S1]
  U->>O: what they want, in their own words [S1]
  O->>O: reads the issue it names and the repository [P2.1]
  O->>S: makes the run's worktree, its branch, and its steering (Steering) [P7.1]
  O->>P: starts one with the run's folder, the user's words, and the request (Steering) [P4.1]
  P->>P: weighs the request by the measure of the vital few [P4.1]
  P->>T: writes the outcome, each need named or found in its own words, and the pick as an open question (Steering, Opportunity) [P2.2]
  P-->>O: ends [P5.1]
  O->>S: commits the steering (Steering) [P5.3]
  loop until no question is open [P2.1]
    O->>U: where the run stands, and the open question, the needs numbered, with a recommendation and why [P2.3]
    U->>O: answers [P2.1]
    O->>P: starts one with the answer, word for word (Steering) [P4.1]
    P->>T: writes the answer as the user's decision, and for a pick, the target and its solution with its riskiest assumption (Steering, Solution) [P1.1]
    P-->>O: ends, with the steps to the target, the walking skeleton first (Step) [P1.2]
    O->>S: writes the steps into the steering, and commits (Steering, Step) [P5.2]
  end
  loop each deliverable of the step, each after those it rests on [P1.2]
    loop each Round, until each condition is good [P3.1]
      O->>G: starts one with the steering, the deliverable, and its best practice (Deliverable, Best practice) [P5.1]
      alt a point it can't settle [P2.1]
        G-->>O: the point, for a pruner to weigh or leave to the user (Round) [P4.1]
      else
        G->>G: makes it by every necessary condition of its kind's best practice, by the run's decisions [P3.1]
        G->>G: tries it as its people would, and goes back to its decisions where they fall short [P3.2]
        G->>S: runs the repository's checks on its files [P5.3]
        G-->>O: ends, with the Round written (Round) [P5.2]
        O->>E: starts one with the deliverable and its best practice (Round, Best practice) [P3.2]
        E->>S: makes a folder of the people's starting state [P3.2]
        E->>E: tries it there as its people would, and names for each condition what's good or what would make it good [P3.2]
        E-->>O: ends, with the Round judged (Round) [P5.2]
        O->>P: starts one with the judged Round (Round) [P4.1]
        P->>T: writes each remedy that the measure keeps as a decision, and past the limit, each finding with none as a proposal (Steering) [P3.3]
        P-->>O: ends [P5.1]
      end
    end
    O->>G: starts a new one with the refactor best practice of its kind (Best practice) [P3.1]
    G->>G: refactors it, keeping its intent, and runs the repository's tests [P3.1]
    G-->>O: ends, which ends the deliverable's Rounds (Round) [P5.2]
    O->>S: puts it up, committed and pushed in the draft pull request, and marks it done (Steering, Deliverable) [P5.3]
  end
  O->>S: marks the step trying (Step) [P6.1]
  loop until the user says it's enough [P2.1]
    O->>U: what it does, what it doesn't do yet, how to try it, and each finding left as a proposal [P1.2]
    U->>O: /rn:ty, or /rn:gm with what to change [P2.1]
    alt /rn:gm with what to change [P1.3]
      O->>S: writes the Fix, with the problem in the user's words (Fix) [P6.1]
      O->>F: starts one with the Fix, the deliverable, its best practice, and the run's decisions (Fix) [P5.1]
      alt its mend would change a decision [P4.1]
        F-->>O: ends, mending nothing, with the decision named (Fix) [P4.1]
        O->>P: starts one with the decision named, which takes the deliverable's Rounds again (Steering) [P4.1]
      else
        F->>F: mends the deliverable, and checks it by its best practice, the repository's checks, and the unit tests [P3.4]
        F-->>O: ends, fixed (Fix) [P5.2]
        O->>S: puts it up again (Deliverable) [P5.3]
      end
    else /rn:ty [P2.1]
      O->>S: marks the step done (Step) [P5.2]
    end
  end
  O->>S: pushes, and waits for the pull request's CI [P5.3]
  O->>E: starts one with the outcome, the pull request whole, and its CI [P3.2]
  E-->>O: ends, with each finding [P5.2]
  opt a finding [P3.2]
    O->>O: takes it as a problem with the deliverable whose file it is, mended as /rn:gm's [P1.3]
  end
  O->>P: starts one with the run's end (Steering) [P4.1]
  P-->>O: ends, with a proposal for each need left, to keep it in an issue or to leave it [P2.2]
  O->>S: marks the final check passed, so the run ends once nothing is asked (Steering) [P6.1]
  O->>U: the need reached, each need left with its proposal, CI, and the merge proposed [P2.2]
  opt the user says which needs to keep [P2.2]
    O->>P: starts one with the answer, word for word (Steering) [P4.1]
    O->>S: opens an issue for each need kept, in its own words [P2.2]
  end
  U->>U: marks the pull request ready, and merges [P7.2]
```

#### S2: a run stopped, and picked up later

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant S as scripts
  participant G as generator
  participant E as evaluator
  participant F as fixer
  U->>O: /rn:dn, or asks to stop for now [S2]
  O->>O: waits for each pruner at work to end, as its write stays whole [P6.2]
  O->>G: stops it [S2]
  O->>E: stops it [S2]
  O->>F: stops it [S2]
  O->>S: commits and pushes the run's folder (Steering, Round, Fix) [P6.2]
  O->>U: where it stopped, and what waits for the user [P2.3]
  Note over U,O: Later, in any conversation
  U->>O: /rn:up [S2]
  O->>S: lists the runs of this repository whose pull request is open (Steering) [P6.1]
  opt more than one run [S2]
    O->>U: asks which run to go on with [P2.1]
    U->>O: answers [S2]
  end
  O->>S: lists what's due from the run's files, an open question, a step trying, a Round, or a Fix (Steering, Round, Fix) [P6.1]
  O->>U: where it picks up, and what waits for the user [P2.3]
  alt a Round under way [P6.1]
    O->>G: starts a new one from the Round's files [P6.1]
    O->>E: starts a new one from the Round's files [P6.1]
  else a Fix under way [P6.1]
    O->>F: starts a new one from the Fix's files [P6.1]
  end
```

### Deployment

![rn's deployment](images/deployment.svg)

The user installs rn as [the README](../../plugins/rn/README.md#installation) says, and types
`/rn:on` at their repository's root.

Strategies:

- rn's own git worktree and branch for each run. [P7.1]\
  Intent: the user goes on with their own work, and their side stays as it was.
- The pull request opened as a draft, which the user marks ready. [P7.2]\
  Intent: nobody reviews or merges the work before the user has seen it checked whole.

### Directory structure

```text
plugins/rn/                        what Claude Code installs for the user
├── skills/                        /rn:on, /rn:up, /rn:dn, /rn:ty, and /rn:gm, each pointing to the orchestrator
├── agents/                        the pruner's, the generator's, the evaluator's, and the fixer's starts
├── hooks/                         the hook that turns a role's delete to a script
└── domain/
    ├── orchestrator.md            each event's own steps, then those that every event shares
    ├── vital-few.md               the measure of the vital few
    ├── pruner.md                  what the pruner does
    ├── generator.md               what the generator does
    ├── evaluator.md               what the evaluator does
    ├── fixer.md                   what the fixer does
    ├── schemas/                   the form of the steering and of each role's result
    ├── best-practices/            rn's best practice of each kind
    └── scripts/                   each step with one right result, as a role runs it

dev/rn/                            what only rn's developers use
└── tests/unit/                    the unit tests of rn's code

.claude/worktrees/                 rn's worktree of each run
└── rn-<yyyymmdd>-<slug>/          one run's worktree, on the work's branch

.rn/                               what rn writes on the work's branch
└── <yyyymmdd>-<slug>/             one run's folder
    ├── steering.json              the steering
    └── rounds/<deliverable>/      each Round and each Fix of the deliverable, in the order made
```

## Test strategy

The user's run of a real request is the end-to-end check. A test at a higher level than the unit tests is added
only for a fault that the user's run found and that a test should have caught before it, or for
an operation that can't be undone.

| Check | Test target | Kind | When | Exit criteria or measure |
|---|---|---|---|---|
| Lint | Parts | Quality | During the work | 0 findings. |
| Static analysis | Parts | Quality | During the work | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | During the work | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | During the work | A case for each class of input that an interface's contract treats apart, and every case passes. |
| Code coverage | Parts | Quality | During the work | 100% statement (C0) and branch (C1) coverage. |
| Scenario testing | Product | Quality | Apart from the work | The user's run of a real request puts the walking skeleton in their hands, with no stop that a fault caused. |
| Installation testing | Product | Quality | Apart from the work | Once ccpm's marketplace lists rn, it installs alone by the README's commands in a fresh home. |
| Configuration testing | Product | Quality | During the work | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | During the work | Claude Code's strict check of the plugin passes. |
