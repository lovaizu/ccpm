# rn architecture

## User stories

- S1: the user wants the deliverable they're after, asking in their own words with no
  specification.
- S2: the user wants to pause a run and resume it later in any conversation, losing neither time
  nor work.

## Solution strategy

### Principles

rn piles up the vital few that bring a deliverable's people to their aim, and cuts the trivial many.

- P1: toward the people's aim
  - P1.1: the run reviews its course by its facts at each event.
  - P1.2: the user is asked only what only they can decide, one point at a time.
  - P1.3: work that rests on a plan or a deliverable starts once the user signs it off.
- P2: judged by the people's aim
  - P2.1: a deliverable is tried as its people would, with only what they have.
  - P2.2: a trial names only what's good and what would make it good.
- P3: made the field's established way
  - P3.1: running, making, and judging are separate roles.
  - P3.2: content is made the field's established way and refactored, or lightly by its check
    alone.
  - P3.3: remaking has a limit, and each finding left goes to the user as a proposal.
- P4: each role on its own work
  - P4.1: each role starts with only what its work needs.
  - P4.2: what a role makes stays in files, and roles hand each other short results.
  - P4.3: a step that has one right result is done the same way each time, without a role's
    judgment.
- P5: the shortest path
  - P5.1: a role that leaves its steps is told at once and goes back.
  - P5.2: deliverables that rest on none still being made are made at the same time.
  - P5.3: work that a stop leaves alone goes on.
- P6: nothing lost on a stop
  - P6.1: the run's state lives in files, so that it goes on from any conversation.

### Data model

![rn's data](images/data-model.svg)

- Design tree\
  Holds what to make, why, and how far the run got, for each review and each pick-up. Its form is
  [the design tree best practice](../../plugins/rn/domain/best-practices/design-tree/best-practice.md)'s.
- Cut\
  A role's part of the design tree, so that each role starts with only the decisions its work needs.
- Best practice\
  The field's established way to make one kind of deliverable, and its conditions, which making
  and judging both stand on.
- Round\
  One making or refactoring of a deliverable, which its maker and its judge each try as its people
  would. What each found good or short decides the next mend.

Strategies:

- Each design tree edit checked before its commit, on each condition of its best practice that
  code can check. [P1.1]\
  Intent: the work always rests on a design tree in form.
- The plan kept as the design tree's own deliverable, and each sign-off as its deliverable done.
  [P1.3]\
  Intent: the run's files alone say what waits for the user and what may start.
- Each point that the user settles kept as an open decision of its condition, and their answer
  as its decision. [P6.1]\
  Intent: a point and its answer outlive the conversation that asked it.
- A finding that the people would never meet dropped by holding its condition good. [P1.1]\
  Intent: the next generator gets as given each finding of a condition still short.

### Components

![rn's components](images/components.svg)

- orchestrator (prompt)\
  Leads the run to the people's aim.
- generator (prompt)\
  Makes a deliverable with which its people reach their aim.
- evaluator (prompt)\
  Checks, as the people, whether a deliverable reaches their aim.
- scripts (script)\
  Does each step that has one right result.

Strategies:

- Each command an entry alone, pointing to the orchestrator's steps for each event. [P1.1]\
  Intent: every event reaches the one place that reviews the run, as no command checks its input.
- The main conversation as the orchestrator, which starts and stops each other role. [P3.1]\
  Intent: the talk with the user and the review of the design tree share one context.
- One generator and one evaluator for each Round, the evaluator judging every condition from one
  trial. [P2.1]\
  Intent: the people's use is one act, so it's tried once and judged whole.
- The generator trying the deliverable as its people would, and going back to its decisions on a
  shortfall they meet. [P2.1]\
  Intent: the maker finds its own shortfall, and hands on only what it saw serve the people.
- The generator taking as given what the last evaluator found good or short. [P2.2]\
  Intent: the generator mends by the judge's own measure.
- The last Round's roles resumed within a session, and started from its files in a new
  conversation. [P6.1]\
  Intent: each mend starts from what the last Round learned, wherever the run goes on.
- A point that a role can't settle taken to the user as given, and the answer taken back as
  given. [P1.2]\
  Intent: the user answers the role's own question, and the role gets the user's own words.
- Each step that has one right result done by a script that the role runs. [P4.3]\
  Intent: each role spends its judgment and its context only where a step needs them.
- rn's order given to Lane as the starts due from the design tree, each deliverable's rounds
  beside the others'. [P5.2]\
  Intent: the user waits for the slowest deliverable, not for all of them in turn.
- Lane applied to every activity of every role's steps that it can hold, the orchestrator's
  included. [P5.1]\
  Intent: a role that leaves its steps notices at once and goes back.
- Each step held to what it does, never to one OS's tools, such as Glob or Bash's `find`. [P5.1]\
  Intent: rn runs alike on each OS that Claude Code runs on.
- A refusal that only the user can mend stopping only the work it concerns. [P5.3]\
  Intent: the user mends one blocker while every other deliverable goes on.

### Sequences

#### S1: a deliverable made in rounds

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant T as design tree
  participant S as scripts
  participant G as generator
  participant E as evaluator
  U->>O: /rn:on [S1]
  O->>U: asks what they want [S1]
  U->>O: what they want, in their own words [S1]
  O->>S: makes the run's worktree, and its design tree with the goal as put (Design tree) [P4.3]
  loop each event: a request, an answer, a sign-off, a send-back, or a role ended [P1.1]
    opt a sign-off [P1.3]
      O->>S: records it (Design tree) [P4.3]
    end
    O->>T: reviews it by the run's facts and the user's words (Design tree) [P1.1]
    O->>S: lists each node that the change touches, to read again (Design tree) [P1.1]
    O->>S: checks and commits the change (Design tree) [P6.1]
    opt a refusal that only the user can mend [P5.3]
      O->>U: the blocker, and what the user does, the other work going on [P5.3]
    end
    alt a point the orchestrator can settle [P1.2]
      O->>T: settles it, with its ground (Design tree) [P1.2]
    else a point only the user can settle [P1.2]
      O->>U: one point, with a recommendation [P1.2]
      U->>O: answers [P1.2]
    else a plan or a deliverable waiting for sign-off [P1.3]
      O->>S: puts it up, committed and pushed in the pull request [P4.3]
      O->>U: puts it up, with each finding left as a proposal [P3.3]
      U->>O: /rn:ty, or /rn:gm with what to change [P1.3]
    else each deliverable whose inputs are signed off, resting on none still being made [P5.2]
      par one for each such deliverable [P5.2]
        O->>G: starts it with its Cut, or resumes the last Round's (Cut) [P4.1]
        alt a point it can't settle [P1.2]
          G-->>O: the point (Round) [P1.2]
          O->>T: keeps it as an open decision of its condition (Design tree) [P6.1]
          O->>U: the point, as given [P1.2]
          U->>O: answers [P1.2]
          O->>T: writes the answer as its decision (Design tree) [P6.1]
          O->>G: resumes it with the answer, as given [P1.2]
        else
          G->>G: makes the content by its kind's best practice, or, once each condition is good, refactors it by the refactor best practice, taking the last evaluator's findings as given (Best practice, Round) [P3.2]
          G->>G: tries it as its people would, and goes back to its decisions where a condition that they meet falls short [P2.1]
          G->>G: names what's good [P2.1]
          G->>S: runs the repository's checks on its files [P4.3]
          G-->>O: ends, with the Round written (Round) [P4.2]
          O->>E: starts it with its Cut, or resumes the last Round's (Cut) [P4.1]
          E->>S: makes a folder of the people's starting state [P2.1]
          E->>E: tries it there as its people would [P2.1]
          E->>E: names, for each condition, what's good or what would make it good [P2.2]
          E-->>O: ends, with the Round written (Round) [P4.2]
          O->>T: takes each finding that helps the people into the decision it comes from, and holds good each condition whose finding they'd never meet (Design tree) [P1.1]
          O->>T: keeps each finding past two rounds of content or of refactoring as an open decision of its condition (Design tree) [P3.3]
        end
      end
    end
  end
  O->>U: the pull request, with each decision taken without asking [S1]
  U->>O: /rn:ty, and merges [P1.3]
```

#### S2: a pause and a pick-up

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant T as design tree
  participant S as scripts
  participant G as generator
  participant E as evaluator
  U->>O: /rn:dn [S2]
  O->>G: stops it [S2]
  O->>E: stops it [S2]
  O->>S: commits and pushes the run's folder (Design tree) [P6.1]
  O->>U: where it stopped, and the point or sign-off waiting [S2]
  Note over U,O: Later, in any conversation
  U->>O: /rn:up [S2]
  O->>S: finds the run to pick up from the runs' commits (Design tree) [P6.1]
  opt no run found [S2]
    O->>U: asks which run to pick up [S2]
  end
  O->>T: reads where it stopped (Design tree) [P6.1]
  O->>U: where it picks up, and the point or sign-off waiting [S2]
  O->>G: starts each role stopped again, from the Round's files and a fresh Cut (Round, Cut) [P6.1]
```

### Deployment

![rn's deployment](images/deployment.svg)

The user installs rn as [the README](../../plugins/rn/README.md#installation) says, which installs
Lane, and types `/rn:on` at their repository's root.

Strategies:

- rn's own git worktree for each run. [S2]\
  Intent: the user goes on with their work, and a pause leaves their side as it was.

### Directory structure

```text
plugins/rn/                        what Claude Code installs for the user
├── skills/                        /rn:on, /rn:up, /rn:dn, /rn:ty, and /rn:gm, each pointing to the orchestrator
├── agents/                        the generator's and the evaluator's starts
├── domain/
│   ├── orchestrator.md            the event's own step, then those that every event shares
│   ├── generator.md               what the generator does
│   ├── evaluator.md               what the evaluator does
│   ├── schemas/                   the form of each Cut and result
│   ├── tree/                      the code that checks the design tree
│   ├── check/                     the code that checks each role's result against its form
│   ├── rounds/                    the code that reads and writes the Rounds
│   ├── template/                  the code that holds a document to its kind's template
│   ├── repository/                the code that makes a run's worktree and puts a deliverable up
│   └── best-practices/            rn's own best practice of each kind
├── scripts/                       each step with one right result, as a role runs it
└── lane/                          what rn gives Lane
    ├── rules.json                 the rules of each role's steps
    └── adapters/                  the starts due from the design tree, and a step's practices

dev/rn/                            what only rn's developers use
└── tests/                         the test cases, from unit to integration

.claude/worktrees/                 rn's worktree of each run
└── rn-<yyyymmdd>-<goal>/          one run's worktree, on the work's branch

.rn/                               what rn writes on the work's branch
├── <yyyymmdd>-<goal>/             one run's folder
│   ├── design-tree.json           the design tree
│   └── rounds/                    each Round
└── best-practices/                each best practice made on a run
```

## Test strategy

| Check | Test target | Kind | When | Exit criteria or measure |
|---|---|---|---|---|
| Lint | Parts | Quality | During the work | 0 findings. |
| Static analysis | Parts | Quality | During the work | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | During the work | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | During the work | Every case passes. |
| Unit testing | Parts that hold a prompt | Benchmark | During the work | Each case's results over 3 runs. |
| Code coverage | Parts | Quality | During the work | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | During the work | 0 counterexamples of each invariant that rn's product vision, README, and this document state. |
| Integration testing | Architecture | Quality | During the work | Every case passes, with a double of each prompt, and each handoff gives the data the data model names. |
| Contract testing | Architecture | Quality | Apart from the work | On each new gh, each recorded command gives what it recorded. |
| Traceability | Architecture | Quality | During the work | Every element tested, every case naming one level up, and each strategy's case failing broken. |
| Installation testing | Product | Quality | Apart from the work | Once ccpm's marketplace lists rn, it installs with Lane by the README's commands in a fresh home. |
| Configuration testing | Product | Quality | During the work | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | During the work | Claude Code's strict check of the plugin passes. |
