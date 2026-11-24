# rn architecture

## User stories

- S1: the user wants the deliverable they're after, asking in their own words, checking only the
  steps they choose.
- S2: the user wants to pause a run and resume it in any conversation losing nothing, or to
  cancel it.

## Solution strategy

### Principles

rn piles up the [vital few](https://en.wikipedia.org/wiki/Pareto_principle) that bring a
deliverable's people to their aim, and cuts the trivial many thoroughly.

- P1: toward the people's aim
  - P1.1: the run reviews its course at each event by what it has done and learned.
  - P1.2: the user is asked only what only they can decide, one point at a time, in their own
    terms.
  - P1.3: work that rests on the plan or on a deliverable that the user checks starts at their
    sign-off.
- P2: judged by the people's aim
  - P2.1: a deliverable is tried as its people would, with only what they have.
  - P2.2: a trial names only what's good and what would make it good.
  - P2.3: the work is checked whole before its merge is proposed.
- P3: made the field's established way
  - P3.1: running, weighing the plan, making, and judging are separate roles.
  - P3.2: content is made by its kind's best practice and refactored, or, as the user picks, by
    its check alone.
  - P3.3: remaking has a limit, and each finding left goes to the user as a proposal.
- P4: each role on its own work
  - P4.1: each role starts with only what its work needs.
  - P4.2: what a role makes stays in files, and roles hand each other short results.
  - P4.3: a step that has one right result is done the same way each time, without a role's
    judgment.
- P5: the shortest path
  - P5.1: the plan takes in each settled set of points, and each trial's result, as a whole.
  - P5.2: deliverables that rest on none still being made are made at the same time.
  - P5.3: work that a stop leaves alone goes on.
- P6: nothing lost on a stop
  - P6.1: the run's state lives in files, so that it goes on from any conversation.
- P7: only what the people can't reach their aim without
  - P7.1: each fact is weighed by one shared measure of the vital few, which alone states it.
  - P7.2: each part of the plan that a new one rests on is weighed again with it.
  - P7.3: the plan changes only by that weighing, or by a step that has one right result.

### Concept model

![rn's concepts](images/concept-model.svg)

- Design tree\
  Holds what to make, why, and how far the run got, for each review and each pick-up. It also
  holds rn's version, the languages, the steps, the issues, and the pull request. Its form is
  [the design tree best practice](../../plugins/rn/domain/best-practices/design-tree/best-practice.md)'s.
- Cut\
  A role's part of the design tree, so that each role starts with only the decisions its work needs.
- Best practice\
  The field's established way to make one kind of deliverable, and its conditions, which making
  and judging both stand on.
- Round\
  One making or refactoring of a deliverable, which its maker tries as its people would. Its judge
  tries content too. Its result, what each found, is weighed whole into the plan, whose decisions
  decide the next mend.

Strategies:

- Each design tree edit checked before its commit, on each condition of its best practice that
  code can check. [P1.1]\
  Intent: the work always rests on a design tree in form.
- The plan kept as the design tree's own deliverable, and each sign-off as its deliverable done.
  [P1.3]\
  Intent: the run's files alone say what waits for the user and what may start.
- Each point for the user kept as an open decision, and their answer, word for word, as its
  decision. [P6.1]\
  Intent: a point and the user's own words outlive the conversation that asked it, for each later
  judgment.
- The way to the goal kept as the design tree's steps, each saying whether the user checks it.
  [P1.3]\
  Intent: the run's files alone say which deliverables wait for the user, and where the run stands.
- Each deliverable's last Round marked as the end of its Rounds once it's put up. [P1.3]\
  Intent: a send-back gets Rounds of its own, so that the user's change is remade.
- The issues to close and to refer to written from the request, never asked. [P1.2]\
  Intent: the user isn't asked what their request already says.
- The pull request opened as a draft, which the user marks ready. [P2.3]\
  Intent: nobody reviews or merges the work before the user has seen it checked whole.
- A finding that the people would never meet dropped by holding its condition good. [P1.1]\
  Intent: the next mend holds only what the people fail without.
- Each done deliverable kept with its conditions and their decisions. [P7.2]\
  Intent: a later deliverable rests on what a done one decided, and the pruner weighs it again.
- Each Cut made from the design tree at each start of its role, never kept from an earlier start.
  [P4.1]\
  Intent: each change to the tree, such as a remedy written or a point cut, reaches the next
  maker.

### Components

![rn's components](images/components.svg)

- orchestrator (prompt)\
  Moves the run along its plan to the people's aim, as the user's one contact.
- pruner (prompt)\
  Keeps the plan to the vital few that bring the people to their aim.
- vital few (prompt)\
  Holds the one measure by which rn tells the vital few from the trivial many.
- generator (prompt)\
  Makes a deliverable with which its people reach their aim, by the design tree's decisions.
- evaluator (prompt)\
  Checks, as the people, whether a deliverable reaches their aim, for the pruner to weigh.
- scripts (script)\
  Does each step that has one right result.
- hook (hook)\
  Holds each role, on every call, to the writes and the deletes that are its own.

Strategies:

- Each command only an entry point, pointing to the orchestrator's steps for each event. [P1.1]\
  Intent: every event reaches the one role that hands it on, as no command checks its input.
- The main conversation as the orchestrator, which starts and stops each other role. [P3.1]\
  Intent: the user talks with one role through the run, and each judgment of the plan starts
  apart.
- Each fact that asks a judgment, and no other, handed to a pruner before it enters the
  design tree. [P7.1]\
  Intent: one role holding the stance alone weighs all the plan takes in, and no step waits on
  needless judgment.
- One shared prompt of the measure, read by the orchestrator and the pruner, each role's prompt
  holding only its part. [P7.1]\
  Intent: the two roles weigh by one measure, which changes in one place.
- Facts handed to a pruner a unit at a time: a settled set of decisions, or a judged Round.
  [P5.1]\
  Intent: the user waits on a weighing only once a set is settled, and linked facts are weighed
  together.
- A new pruner for each unit, given only the run's folder by absolute path, the user's words, and
  the unit. [P4.1]\
  Intent: each unit is weighed as an outsider would, and reaches the run's tree wherever the pruner
  starts.
- The pruner itself rewriting each node that its change touches, as a script lists them. [P5.1]\
  Intent: each unit costs one wait, and the role that made the change mends what it made false.
- The run's worktree and its design tree, with the goal open, made by a script at the request.
  [P4.3]\
  Intent: the run starts at once, as nothing is yet settled to weigh.
- The hearing held by the orchestrator with the user, handed to one pruner once the way is
  settled. [P5.1]\
  Intent: the hearing's only wait is the one weighing of all it settled.
- The orchestrator speaking only from the design tree and the user's words, the request among
  them. [P1.2]\
  Intent: the talk brings back nothing the pruner cut, such as an issue's means.
- Each message to the user opening with where the run stands on the way to the goal. [P1.2]\
  Intent: a user who knows nothing of rn's insides knows at each message what's done and what's
  next.
- The final check made by a plain subagent over the pull request's whole diff and its CI. [P2.3]\
  Intent: the diff stays out of the orchestrator's context, and a newcomer to the work reads it.
- One generator and one evaluator for each Round, the evaluator judging every condition from one
  trial. [P2.1]\
  Intent: the people's use is one act, so it's tried once and judged whole.
- A new generator for the refactoring once each condition is good, with no evaluator. [P3.2]\
  Intent: a new reader meets what the content's maker misses, and the checks and tests show the
  intent holds.
- The generator trying the deliverable as its people would, and going back to its decisions on a
  shortfall they meet. [P2.1]\
  Intent: the generator finds its own shortfall, and hands on only what it saw serve the people.
- Each role trying the deliverable outside the work's branch, and checking only its own files.
  [P4.3]\
  Intent: the pull request holds only the deliverables and the run's records.
- The generator mending by its Cut's decisions alone, never by an evaluator's findings. [P7.3]\
  Intent: only the remedy that the pruner weighed reaches the deliverable.
- The last Round's roles resumed within the same conversation, and started from its files in a new
  conversation. [P6.1]\
  Intent: each mend starts from what the last Round learned, wherever the run goes on.
- A point for the user, from the pruner or a generator, discussed until settled, then handed to
  one pruner. [P1.2]\
  Intent: the user settles the point in one talk, and the plan takes their own words in one
  weighing.
- Each step that has one right result done by a script that the role runs. [P4.3]\
  Intent: each role spends its judgment and its context only where a step needs them.
- Each deliverable's Rounds kept apart from the others', so that each deliverable due starts
  at once. [P5.2]\
  Intent: the user waits for the slowest deliverable, not for all of them in turn.
- Each maker's removal done by a script of exact paths, which a hook names to its deletes in Bash.
  [P4.3]\
  Intent: a maker's clean-up never waits on a permission prompt, and stays in the work and the
  temporary folder.
- Each design tree write by Write, Edit, or Bash refused by the hook, but the pruner's and
  scripts'. [P7.3]\
  Intent: the plan holds only what the pruner weighed, on every run, whatever a prompt forgets.
- Each step written as what it does, never tied to one OS's tools, such as Glob or Bash's
  `find`. [P4.3]\
  Intent: rn runs alike on each OS that Claude Code runs on.
- A script's refusal that only the user can mend stopping only the work it concerns. [P5.3]\
  Intent: the user mends one blocker while every other deliverable goes on.
- A pause or a cancel taken from the user's words. [S2]\
  Intent: the user stops a run without learning a command.
- A pause handing one pruner what the user settled unwritten, and stopping the rest once each
  pruner ends. [P6.1]\
  Intent: a pick-up reads a whole design tree, as a unit may live only in the conversation.
- A cancel confirmed once, removing the run here and its branch and pull request on GitHub. [S2]\
  Intent: nothing that can't be undone happens on one misread sentence, and no run is left to
  collide with.

### Sequences

#### S1: a deliverable made in rounds

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant P as pruner
  participant H as hook
  participant T as design tree
  participant S as scripts
  participant G as generator
  participant E as evaluator
  U->>O: /rn:on [S1]
  O->>U: asks what it can help with: an issue's number or a few words [S1]
  U->>O: what they want, in their own words [S1]
  O->>O: reads the issue it names and the repository [P1.2]
  O->>S: makes the run's worktree, and its design tree with the goal open, and the languages as the orchestrator puts them (Design tree) [P4.3]
  loop the hearing, until the way to the goal is settled [P5.1]
    O->>U: one point, whom the goal is for, then what they can do at it, then the goal in one summary, then its deliverables and steps and which steps the user checks, with why and a recommendation [P1.2]
    U->>O: answers [P1.2]
  end
  loop each event: the hearing's end, a point settled, a sign-off, a role's end, or a refusal [P1.1]
    opt a unit settled: the hearing's, a point the user settled, a judged Round, or the final check's findings [P5.1]
      O->>P: starts a new one with the run's folder as an absolute path, the user's words of the run, the request among them, and the unit (Design tree, Round) [P4.1]
      P->>P: weighs each element that the unit would add, change, or ask by the shared measure of the vital few [P7.1]
      P->>P: weighs again each element of the tree that one of them rests on, a done deliverable's decisions and the issue's among them [P7.2]
      P->>T: writes the vital few, from the goal and the plan down, cuts the rest, and leaves open each point that only the user can settle (Design tree) [P7.1]
      opt a Round's result with a trial's findings [P2.2]
        P->>T: writes the remedy that the measure keeps of each finding into the decision it comes from, and holds good each other condition (Design tree) [P7.1]
        P->>T: keeps each finding past two Rounds as an open decision of its condition (Design tree) [P3.3]
      end
      opt the final check's findings [P2.3]
        P->>T: sends each problem that the people fail without back to the deliverable whose file it is (Design tree) [P2.3]
      end
      P->>S: lists each node that its change touches (Design tree) [P5.1]
      P->>T: rewrites each node listed that the change made false (Design tree) [P1.1]
      P-->>O: ends, with what it changed, each point it left open, and each stray file [P4.2]
      opt a stray file [P2.3]
        O->>O: removes it [P2.3]
      end
    end
    opt a sign-off by /rn:ty [P1.3]
      O->>S: records it (Design tree) [P4.3]
    end
    opt a write to the design tree by any other role, by Write, Edit, or Bash [P7.3]
      H->>T: refuses the write, telling its writer to hand the fact to the pruner (Design tree) [P7.3]
    end
    O->>S: checks and commits the change (Design tree) [P6.1]
    opt a refusal that only the user can mend [P5.3]
      O->>U: the blocker, and what the user does, the other work going on [P5.3]
    end
    alt a point that only the user can settle: left open in the tree, brought by a generator, or a change asked by /rn:gm [P1.2]
      loop until the user settles it [P1.2]
        O->>U: where the run stands, and the point, from the design tree and the user's words, with why and a recommendation [P1.2]
        U->>O: answers [P1.2]
      end
      O->>O: takes what the user settled, in their words, as the next unit for one pruner [P1.2]
    else the plan written from the hearing, with no point open [P1.3]
      O->>S: records the plan's sign-off, with the steps that the user checks as they settled them (Design tree) [P1.3]
    else a deliverable whose Rounds are over [P1.3]
      O->>S: puts it up, committed and pushed in the pull request, which names the run's issues, and makes it done where its step isn't one the user checks (Design tree) [P4.3]
      opt at a step that the user checks [P1.3]
        O->>U: puts it up, with a link to each of its files as pushed, and each finding left as a proposal [P3.3]
        U->>O: /rn:ty, or /rn:gm with what to change [P1.3]
      end
    else each deliverable whose inputs are done, resting on none still being made [P5.2]
      par one for each such deliverable [P5.2]
        O->>S: writes the due role's Cut from the design tree as it stands (Cut) [P4.1]
        alt its Round of content, to make [P3.2]
          O->>G: starts it with its Cut, or resumes the last Round's with the user's words, as given (Cut) [P4.1]
          alt a point it can't settle [P1.2]
            G-->>O: the point, for the user to settle (Round) [P1.2]
          else
            G->>G: makes the content by its kind's best practice, or by its check alone, by the decisions of its Cut (Best practice, Cut) [P3.2]
            G->>G: tries it as its people would, and goes back to its decisions where a condition that they meet falls short [P2.1]
            G->>G: names what's good [P2.1]
            G->>S: runs the repository's checks on its files [P4.3]
            G-->>O: ends, with the Round written, for the evaluator to judge (Round) [P4.2]
          end
        else its Round of content, made, to judge [P2.1]
          O->>E: starts it with its Cut, or resumes the last Round's (Cut) [P4.1]
          E->>S: makes a folder of the people's starting state [P2.1]
          E->>E: tries it there as its people would [P2.1]
          E->>E: names, for each condition, what's good or what would make it good [P2.2]
          E-->>O: ends, with the Round written, its result for one pruner to weigh (Round) [P4.2]
        else each condition good, for a kind with a best practice [P3.2]
          O->>G: starts a new one with a Cut of the refactor best practice of code or of a document (Cut) [P3.2]
          G->>G: refactors it by that best practice, keeping its intent (Best practice) [P3.2]
          G->>G: runs the repository's tests as its developers run them [P3.2]
          G->>S: runs the repository's checks on its files [P4.3]
          G-->>O: ends, with the Round written, which ends the deliverable's Rounds (Round) [P4.2]
        end
      end
    end
    opt each deliverable done [P2.3]
      O->>O: starts a plain subagent with the goal, the pull request, and the points to check [P2.3]
      O->>S: pushes the work, and gives the pull request's whole diff, read by the subagent (Design tree) [P4.3]
      O->>S: waits for the pull request's CI, and gives its result to the subagent [P4.3]
      O->>O: takes the subagent's findings, the goal reached, the fit with the repository's files, nothing extra, and CI, as one unit for one pruner [P2.3]
    end
  end
  O->>U: the final check's results, each finding left as a proposal, and the merge proposed [P2.3]
  U->>U: marks the pull request ready, and merges [P2.3]
```

#### S2: a pause, a cancel, and a pick-up

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant P as pruner
  participant T as design tree
  participant S as scripts
  participant G as generator
  participant E as evaluator
  alt a cancel, in the user's words [S2]
    U->>O: asks to drop the run [S2]
    O->>U: asks once to confirm, as removing can't be undone [S2]
    U->>O: confirms [S2]
    O->>G: stops it [S2]
    O->>E: stops it [S2]
    O->>S: removes the run's worktree, its local branch, and its branch and pull request on GitHub (Design tree) [S2]
    O->>U: the run cancelled, and what it couldn't remove on GitHub, with why [S2]
  else a pause, by /rn:dn or in the user's words [S2]
    U->>O: /rn:dn, or asks to stop for now [S2]
    opt what the user has settled that no pruner holds yet, such as the hearing's so far [P6.1]
      O->>P: starts one with the run's folder as an absolute path, the user's words of the run, and that unit (Design tree) [P6.1]
    end
    O->>O: waits for each pruner at work to end, as its write stays whole [P6.1]
    O->>G: stops it [S2]
    O->>E: stops it [S2]
    O->>S: commits and pushes the run's folder (Design tree) [P6.1]
    O->>U: where it stopped, and the point or sign-off waiting [S2]
  end
  Note over U,O: Later, in any conversation, after a pause
  U->>O: /rn:up [S2]
  O->>S: finds the run to pick up from the runs' commits, here and as GitHub holds them (Design tree) [P6.1]
  opt no run found [S2]
    O->>U: asks which run to pick up [S2]
  end
  O->>T: reads where it stopped (Design tree) [P6.1]
  O->>U: where it picks up, and the point or sign-off waiting [S2]
  O->>G: starts the generator stopped again, from the Round's files and a fresh Cut (Round, Cut) [P6.1]
  O->>E: starts the evaluator stopped again, from the Round's files and a fresh Cut (Round, Cut) [P6.1]
```

### Deployment

![rn's deployment](images/deployment.svg)

The user installs rn as [the README](../../plugins/rn/README.md#installation) says, and types
`/rn:on` at their repository's root.

Strategies:

- rn's own git worktree for each run. [S2]\
  Intent: the user goes on with their work, and a pause leaves their side as it was.

### Directory structure

```text
plugins/rn/                        what Claude Code installs for the user
├── skills/                        /rn:on, /rn:up, /rn:dn, /rn:ty, and /rn:gm, each pointing to the orchestrator
├── agents/                        the pruner's, the generator's, and the evaluator's starts
├── hooks/                         the hook that turns a maker's delete to remove.py, and keeps the design tree to the pruner and the scripts
├── domain/
│   ├── orchestrator.md            the event's own step, then those that every event shares
│   ├── vital-few.md               the measure of the vital few, which the orchestrator and the pruner read
│   ├── pruner.md                  what the pruner does
│   ├── generator.md               what the generator does
│   ├── evaluator.md               what the evaluator does
│   ├── schemas/                   the form of each Cut and result
│   ├── tree/                      the code that checks the design tree
│   ├── check/                     the code that checks each role's result against its form
│   ├── rounds/                    the code that reads and writes the Rounds
│   ├── template/                  the code that holds a document to its kind's template
│   ├── repository/                the code that makes a run's worktree and puts a deliverable up
│   ├── remove/                    the code that removes what a maker made for itself
│   ├── hook/                      the code of the hook before each Bash command and each write
│   └── best-practices/            rn's own best practice of each kind
└── scripts/                       each step with one right result, as a role runs it

dev/rn/                            what only rn's developers use
└── tests/                         the test cases, from unit to integration

.claude/worktrees/                 rn's worktree of each run
└── rn-<yyyymmdd>-<slug>/          one run's worktree, on the work's branch

.rn/                               what rn writes on the work's branch
├── <yyyymmdd>-<slug>/             one run's folder
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
| Code coverage | Parts | Quality | During the work | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | During the work | 0 counterexamples of each invariant that rn's product vision, README, and this document state. |
| Integration testing | Architecture | Quality | During the work | Every case passes, with a double of each prompt, and each handoff gives the data the concept model names. |
| Contract testing | Architecture | Quality | Apart from the work | On each new version of gh, each recorded command gives what it recorded. |
| Traceability | Architecture | Quality | During the work | Every element tested, every case naming one level up, and each principle's case failing with its part broken. |
| Scenario testing | Product | Quality | Apart from the work | A walkthrough run of the README's request reaches its pull request with no stop that a fault caused. |
| Installation testing | Product | Quality | Apart from the work | Once ccpm's marketplace lists rn, it installs alone by the README's commands in a fresh home. |
| Configuration testing | Product | Quality | During the work | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | During the work | Claude Code's strict check of the plugin passes. |
