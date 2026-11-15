# rn architecture

## User stories

- S1: the user wants to ask in their own words, so that they get what they mean unspecified.
- S2: the user wants to decide only their own points, one at a time, so that their time goes there.
- S3: the user wants to approve or ask a change at each sign-off, so that nothing rests on a
  misreading.
- S4: the user wants to pause a run at any moment, so that they lose neither time nor work.
- S5: the user wants to resume a paused run in any conversation, so that it goes on where it stopped.
- S6: the user wants one pull request with rn's decisions and lessons, so that they merge knowing
  its content.
- S7: each of rn's developers wants each signed-off lesson in rn's issues, so that they improve rn.

## Solution strategy

rn keeps the vital few of each deliverable as decisions in a design tree, asking the user only
theirs. A generator makes each deliverable from its decisions until evaluators with only its people's
view find it good. rn builds on [the plugin guide](../plugin-development-guide.md), and every view
keeps these rules.

### Drawn out along the design tree

Each role starts with only the cut that `tree.py` gave for it, and the guard stops any other start.

*Why*: a role that reads decisions not its own makes what the user didn't mean, which raises KR1.1.

### Every step by best practice

Each role works by its kind's best practice, a generator finishes by the refactor one, and Lane
holds the steps.

*Why*: an AI that skipped a step once skips it again, so the deliverable misses what it makes,
raising KR1.1.

### Every item handled

Each role reads all it starts with, records each step and practice, and names each item its result
carries.

*Why*: an item dropped takes from the deliverable what the item holds, which raises KR1.1.

### Judged by the people it's for

An evaluator gets only what the deliverable's people have.

*Why*: an evaluator that knows what the maker meant judges the making, not what the people get,
raising KR1.1.

### Signed off before it's built on

`tree.py` gives work resting on a sign-off its turn only after `/rn:ty`, and other work its turn at
once.

*Why*: a misreading found late remakes everything resting on it, raising KR1.1, and idle waiting
adds to KR1.2.

### Back to the design tree on a problem

A `more` or a `/rn:gm` changes the decision it comes from, and `tree.py` keeps a `more` only then.

*Why*: a fix beside the design rests on no decision, so the next round loses or breaks it, raising
KR1.1.

### The design tree revised on each run

What a run finds changes the design tree before the next deliverable, and a best practice once
taken.

*Why*: a design tree or best practice kept as first laid out makes the same miss again, raising
KR1.1.

### Tried in a throwaway copy

A deliverable's commands run only through `throwaway.py`, in a throwaway copy and home, as the
guard holds.

*Why*: a command run as its people run it would change the user's files, and mending them adds to
KR1.2.

### The repository holds the work

The run's state lives only in its folder on the work's branch, which `tree.py` commits at each step
and pause.

*Why*: work kept only in a conversation that ends makes the user answer or wait again, adding to
KR1.2.

## Components

![rn's components](images/components.svg)

- user\
  Gives the goal and each point, sign-off, and lesson that's theirs, pauses the run, and merges.
- rn's developers\
  Change rn's own best practices by each lesson that reaches rn's repository.
- orchestrator\
  Judges whose each point is, settles the rest, plans, and checks each result before taking it.
- tree-keeper\
  Writes each decision into the design tree, and checks that each node it touches agrees.
- generator\
  Makes the deliverable from its cut, and hands back with `asks` each point it can't settle.
- evaluator\
  Judges whether the deliverable meets each condition of its group for its people.
- tree.py\
  Keeps the tree's form, finds each deliverable's turn and cut, and holds the run's files and branch.
- repository\
  Runs each git and gh command for `tree.py`, and reads what they print.
- record.py\
  Checks each record, result, and deliverable against its steps, practices, and template.
- throwaway.py\
  Runs a deliverable's commands in a throwaway copy and home.
- guard\
  Holds each call to its steps and throwaway copy, each end to rn's check, and each sign-off.
- adapters\
  Give Lane each start's text and the results kept, and separate a start from a pick-up.

Strategies:

- One generator for each deliverable\
  Several side by side take about that many times as long for no gain shown, keeping KR1.2 short.
- The orchestrator judging every point\
  The user talks with the one that decides, and no one rewords an answer, keeping KR1.2 short.
- `tree.py` finding the work that waits\
  Code holds it every run, so no work starts early or idles, keeping KR1.1 low and KR1.2 short.
- A tree-keeper writing the design tree\
  The orchestrator checks each change as another's, catching the slips a writer misses, keeping
  KR1.1 low.
- One evaluator for each group of necessary conditions\
  Each judges its group in its own context, side by side, keeping KR1.1 low and KR1.2 short.
- Evaluators by the refactor best practice beside the kind's\
  Judged as one, each round's additions break the structure unseen, so its people misread it, raising
  KR1.1.
- rn's check holding each deliverable to its template\
  Each sentence beyond the vital few buries what the people need, which evaluators pass, raising
  KR1.1.
- Rounds until every necessary condition is good\
  A limit would hand over a deliverable its people can't use, and KR1.1 comes before KR1.2.
- The adapters picking up the one run left from the repository's root\
  At the root, where [Lane's S7](../lane/architecture.md#s7-a-run-picked-up) asks them, no role starts
  over, keeping KR1.2 short.

## Data model

![rn's data](images/data-model.svg)

- Cut\
  The part of the design tree that a role starts with.
- Design tree\
  The goal, its decisions, and the plan of deliverables, in
  [the design tree best practice](../../plugins/rn/domain/best-practices/design-tree/best-practice.md)'s
  form.
- Point\
  A question put to the user with its recommendation: an open decision, the goal drafted, or a lack.
- Sign-off\
  The plan, a deliverable, a lesson, or the pull request, put up for `/rn:ty` or `/rn:gm`.
- Made\
  What a generator made: where it carries out each decision and More kept, and each point it settled.
- Place\
  The step each role of a round stands at, with its work, kept at each step's end and a pause.
- Answers\
  An evaluator's answer to each necessary condition of its group, apart from the user's answer to a
  Point.
- More kept\
  An evaluator's `more` that the orchestrator judged the people fall short by, for the next round's
  generator.
- Record\
  What one start of a role, or the orchestrator, carried out, apart from a Try record of commands
  tried.

Strategies:

- The design tree as JSON written through `tree.py`\
  Deliverables rest on one another many to many by path, which no nested list holds, keeping KR1.1
  low.

## Sequences

### S1: a request, and a deliverable made in rounds

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant K as tree-keeper
  participant T as tree.py
  participant G as generator
  participant W as throwaway.py
  participant E as evaluator
  participant GD as guard
  participant A as adapters
  participant R as record.py
  participant F as Run's folder
  U->>O: /rn:up with what they want
  GD->>A: asks for the results kept, as /rn:up loads, with the words typed after it
  A-->>GD: none, as words after /rn:up are a request, which starts a new run whatever runs are left
  GD->>A: asks for the text of the tree-keeper's start, the run's first move
  A-->>GD: fails, as the folder lies in no run's worktree yet
  GD-->>O: the run started anew, with the tree-keeper's start due and why its text can't be given yet
  Note over O,A: A run of /rn:up that the conversation held before ends, as Lane's guard ends it at a run started anew.
  O->>T: makes the run's worktree
  O->>O: enters it
  O->>K: starts it, with the text that the adapters give in the run's worktree, as the loop below draws for the generator (Cut)
  K->>K: reads its part, the design tree best practice, and the design tree
  K-->>O: done
  O->>O: drafts the goal, and plans the deliverables
  O->>K: resumes it, with the goal drafted and the plan (Decision, Deliverable)
  K->>T: writes them, and commits (Design tree)
  T-->>K: what changed, and each node they touch
  K->>K: checks that each node touched agrees with them
  K-->>O: what changed, and each node checked
  O->>O: checks it against the design tree best practice
  O->>U: the goal, to confirm, once the tree holds it (Point)
  U->>O: answers
  Note over U,O: The orchestrator has the goal written as the user confirmed it, and settles each other point, as S2 draws, and puts up the plan, as S3 draws.
  loop each deliverable whose turn has come, as it rests on no open point and on nothing not signed off
    GD->>A: asks for the text of the generator's start, with each start that runs
    A->>T: gets each deliverable doing, and the Cut of the first that no start that runs holds, with the path of a new Record for the start (Cut)
    A-->>GD: that start's text and run values in Lane's form, or none where no work waits
    GD-->>O: the generator's start due, with its text
    O->>G: starts it, with that text (Cut, More kept)
    Note over O,A: The guard lets a start through only with the text the adapters gave for its role, and stops any other. Each start of the tree-keeper and of each evaluator goes the same way.
    G->>G: makes the deliverable from the design, and checks it by the best practice
    G->>R: records each step and practice as it takes it (Record)
    G->>T: commits its work at the end of each step (Place)
    G->>W: tries it (Try record)
    G->>F: writes what it made, with each point it settled without asking (Made)
    alt the design leaves a point open
      G-->>O: asks, naming it
      Note over O,G: The orchestrator settles it, as S2 draws, and the rounds of each other deliverable go on meanwhile.
      O->>G: resumes it once the tree holds the decision, with its ground, and the user's words word for word where they answered
    else something outside the work stops it, such as a missing tool
      G-->>O: lacks, naming it
      O->>U: what it lacks (Point)
      U->>O: clears it
      O->>G: resumes it
    else done
      G->>GD: ends, with done
      GD->>R: checks its record, its result, and the deliverable (Record)
      R-->>GD: each step, practice, or item they lack, and each place where the deliverable leaves its kind's template, or none, keeping the result in the record
      opt they lack one
        GD-->>G: holds its end, with what they lack
        Note over G,R: The generator carries out what they lack, and ends again. The guard holds each role's end, and each end of the orchestrator's turn, in the same way.
      end
      GD-->>O: done
      O->>O: checks it against the cut and the best practice
      alt it falls short
        O->>G: sends it back, with the ground
      else
        par one for each group of necessary conditions, of the kind's best practice and of the refactor one
          O->>E: starts it (Cut)
          E->>T: commits its work at the end of each step (Place)
          E->>F: writes each necessary condition in good, with its lines, or in more, with its good_when (Answers)
          E-->>O: done
        end
        O->>T: gets the round (Answers, Made)
        T-->>O: each evaluator's Answers, and what the generator made (Answers, Made)
        O->>O: judges each more by the purpose and the best practices
        alt a more the people fall short by
          O->>K: the decision it changes, and the more to keep (Decision, More kept)
          K->>T: writes the decision, and keeps the more (Design tree, More kept)
          alt no decision that answers the more's necessary condition changed since the round's cut
            T-->>K: refuses the more, naming its necessary condition
            K-->>O: that tree.py refused it, and why
            Note over O,K: The orchestrator takes the more back to the decision it comes from, as a fix beside the design rests on no decision.
          else
            T-->>K: what changed, and the More kept
            Note over O,G: The next round starts from the design.
          end
        else every necessary condition is good
          Note over U,O: The orchestrator puts up the deliverable, with each decision under it that the user didn't settle and each point that its Made names, as S3 draws.
        end
      end
    end
  end
```

### S2: a point settled

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant K as tree-keeper
  participant T as tree.py
  loop each point open
    alt it's the user's
      O->>K: the point, as a decision still open (Decision)
      K->>T: writes it, and commits
      K-->>O: what changed
      par
        O->>U: the point, with a recommendation, once no point or sign-off before it waits (Point)
        U->>O: answers
      and
        Note over O,K: Meanwhile, the orchestrator settles each other point, and the rounds of each deliverable whose turn has come go on, as S1 draws.
      end
    else the purpose or a best practice settles it
      O->>O: settles it
    end
    O->>K: the decision, with its ground, and the plan where the decision changes it (Decision, Deliverable)
    K->>T: writes it, and commits it with each deliverable whose turn has come marked doing (Design tree)
    T-->>K: what changed, each node it touches, and each deliverable marked doing
    K->>K: checks that the path up and each node touched agree with it
    K-->>O: what changed, each node checked, and each deliverable marked doing
    alt the change falls short
      O->>K: sends it back, with the ground
    else
      Note over O,K: The rounds of each deliverable marked doing start, as S1 draws.
    end
  end
```

### S3: a sign-off

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant K as tree-keeper
  participant T as tree.py
  participant RP as repository
  participant GH as GitHub
  participant GD as guard
  O->>T: pushes the work
  T->>RP: pushes, and opens or keeps the draft pull request
  alt git or gh can't push, such as with no login
    RP-->>T: what's missing
    T-->>O: what's missing
    O->>U: asks for it (Point)
  else
    RP->>GH: pushes, and opens or keeps the draft pull request
  end
  O->>T: puts it up (Sign-off)
  O->>U: the plan or the deliverable, with what the people can do with it, the decisions taken without asking, and its changes, once no point or sign-off before it waits (Sign-off)
  Note over U,O: Meanwhile, the rounds of each deliverable whose turn has come go on, as S1 draws, and each that rests on this sign-off waits, as tree.py gives it no turn.
  opt the orchestrator moves past the sign-off itself
    O->>GD: a call of /rn:ty or /rn:gm by the Skill tool, or a start of work that rests on the sign-off
    GD-->>O: stops it, as only the user's own /rn:ty or /rn:gm decides a sign-off, and work that tree.py gave no turn has no start
  end
  alt the user approves
    U->>O: /rn:ty
    O->>T: approves the sign-off waiting, as /rn:ty loads (Sign-off)
    O->>O: plans the rest again from what the user signed off
    O->>K: it's signed off, with the plan where it changed (Sign-off, Deliverable)
    K->>T: writes it, and commits it with each deliverable whose turn has come marked doing (Design tree)
    T-->>K: what changed, each node it touches, and each deliverable marked doing
    K->>K: checks that each node touched agrees with it
    K-->>O: what changed, each node checked, and each deliverable marked doing
    O->>O: checks it against the design tree best practice, and takes it or sends it back
    opt no deliverable is left
      Note over U,O: The work is handed over, as S6 draws.
    end
  else the user sends it back
    U->>O: /rn:gm with what to change, or alone
    O->>T: sends the sign-off waiting back, as /rn:gm loads (Sign-off)
    opt alone
      O->>T: gets the user's comments since the sign-off
      T->>RP: gets them
      RP->>GH: reads them
      RP-->>T: the comments (Comment)
      T-->>O: the comments (Comment)
    end
    O->>O: judges each by the purpose and the best practices, for the decision it changes
    O->>K: each decision it changes (Decision)
    Note over O,K: The rounds start again from the design, as S1 draws.
  end
```

### S4: a pause

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant G as generator
  participant E as evaluator
  participant T as tree.py
  participant RP as repository
  participant GH as GitHub
  U->>O: /rn:dn
  O->>G: stops each one still running
  O->>E: stops each one still running
  O->>T: commits and pushes each role's work so far, with the step it stood at (Place)
  T->>RP: commits, and pushes
  alt git or gh can't push
    RP-->>T: what's missing
    T-->>O: what's missing
    O->>U: Paused, committed but not pushed, and what's missing
  else
    RP->>GH: pushes
    O->>U: Paused, where it stopped, what comes next, and the point or sign-off waiting
  end
```

### S5: picking up

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant GD as guard
  participant A as adapters
  participant R as record.py
  participant T as tree.py
  participant K as tree-keeper
  participant G as generator
  participant E as evaluator
  U->>O: /rn:up, alone, in a new conversation at the root of the repository
  GD->>A: asks for the results kept, as /rn:up loads, with the words typed after it, none, in the folder the conversation works in
  Note over GD,A: Where words follow /rn:up, they're a request, so the adapters give none, and a new run starts, as S1 draws.
  A->>T: gets the run of the worktree that holds the folder, or else the runs left, and each Record of the run in the order of its starts (Record)
  A->>R: gets the result kept in each of those records (Record)
  alt the folder lies in a run's worktree, or exactly one run is left
    A-->>GD: those results in Lane's form
    GD-->>O: where the run picks up, and the start due
  else no run is left, or more than one
    A-->>GD: none
    GD->>A: asks for the text of the tree-keeper's start, the run's first move
    A-->>GD: fails, as the folder lies in no run's worktree
    GD-->>O: the run started anew, with the tree-keeper's start due and why its text can't be given yet
  end
  O->>T: lists the runs left
  alt no run is left
    O->>GD: gives the skill's result none, by Lane's result script, a move of the route at the run's start
    GD-->>O: ends the run that Lane began at /rn:up, and gives no start
    O->>U: says that no run is left to pick up, and starts no role
    Note over U,GD: The turn ends outside any run, so the guard holds nothing that the user does next, and rn's check, which holds a turn of a run, doesn't run.
  else
    opt more than one is left
      O->>U: which one (Point)
      U->>O: answers
    end
    O->>O: enters the run's worktree
    O->>U: Picking up, where it stopped, and the point or sign-off waiting
    O->>K: starts it, on the run picked up (Cut)
    O->>G: starts each that stood in a step, at that step (Cut, Place)
    O->>E: starts each that stood in a step, at that step (Cut, Place)
    Note over O,E: Each start goes through the guard and the adapters in the run's worktree, the tree-keeper's first where the guard started the run anew, and the work goes on, as S1, S2, or S3 draws.
  end
```

### S6, S7: the work handed over, and each lesson sent to rn's repository

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant K as tree-keeper
  participant T as tree.py
  participant RP as repository
  participant GH as GitHub
  actor D as rn's developers
  O->>O: finds each change to a best practice and each general lesson in what the run's evaluators put in more
  loop each change to a best practice found
    O->>U: the change, with a recommendation (Point)
    U->>O: answers
    opt the user takes it
      O->>K: adds it as a deliverable (Deliverable)
      Note over O,K: It's made and signed off, as S1 and S3 draw.
    end
  end
  par
    loop each general lesson found
      O->>T: puts it up for the user's sign-off
      O->>U: the lesson, word for word, with a recommendation (Sign-off)
      alt the user approves
        U->>O: /rn:ty
        Note over U,T: The user's /rn:ty has tree.py open it, as no AI may send what leaves their project.
        T->>RP: opens the issue on rn's repository (Sign-off)
        RP->>GH: opens the issue, with the lesson's words
        D->>GH: reads the issue (Sign-off)
        Note over GH,D: Apart from the run, rn's developers change rn's own best practices from it.
      else the user sends it back
        U->>O: /rn:gm, to turn it down or with what to change
        Note over U,T: The user's /rn:gm has tree.py drop it, and the orchestrator puts up again a lesson changed.
      end
    end
  and
    O->>O: reads the whole pull request at once against the goal, by its part
    opt it finds one
      O->>K: the decision it changes (Decision)
      Note over O,K: The rounds start again from the design, as S1 draws, and S6 starts again once they end.
    end
  end
  O->>T: marks the pull request ready
  T->>RP: marks it ready
  RP->>GH: marks it ready
  T-->>O: its URL, with the pull request handed over put up (Sign-off)
  O->>U: Done, with the pull request
  alt the user sends it back
    U->>O: /rn:gm with what to change, or alone
    O->>T: sends the pull request handed over back, as /rn:gm loads (Sign-off)
    T->>RP: marks it a draft again
    RP->>GH: marks it a draft
    Note over U,O: The work goes on, as S3 draws after a sign-off sent back, and the pull request is marked ready again only at the next Done.
  else the user takes it
    opt the user approves it
      U->>O: /rn:ty
      O->>T: approves the pull request handed over, as /rn:ty loads (Sign-off)
      T-->>O: the pull request signed off, left ready
      Note over U,T: Nothing of the run waits for the user any more, and tree.py merges nothing, as the merge stays the user's.
    end
    U->>GH: merges the pull request
  end
```

## Deployment

![rn's deployment](images/deployment.svg)

The user installs rn as [the README](../../plugins/rn/README.md#installation) says, which installs
Lane, and types `/rn:up` at their repository's root.

Strategies:

- rn's own git worktree for each run\
  The user goes on with their work, and a pause leaves nothing of theirs to set right, keeping KR1.2
  short.
- A best practice made on a run in `.rn/best-practices/<kind>/`\
  Every later run finds it and takes it over rn's own of its kind, keeping KR1.1 low.

## Directory structure

rn's folder holds what Claude Code installs for the user. `dev/rn/` holds what only rn's developers
use. `.claude/worktrees/` holds rn's worktree of each run. `.rn/` holds what rn writes on the work's
branch: [the run's folder](../plugin-development-guide.md#where-a-plugin-writes-its-files) and each best practice made on a run.

```text
plugins/rn/
├── .claude-plugin/
│   └── plugin.json                rn's manifest, naming Lane in its dependencies
├── skills/
│   ├── up/
│   │   └── SKILL.md               /rn:up, which makes the main conversation the orchestrator
│   ├── dn/
│   │   └── SKILL.md               /rn:dn, which pauses the run
│   ├── ty/
│   │   └── SKILL.md               /rn:ty, which approves the sign-off waiting
│   └── gm/
│       └── SKILL.md               /rn:gm, which sends the sign-off waiting back
├── agents/
│   ├── tree-keeper.md             starts the tree-keeper
│   ├── generator.md               starts the generator
│   └── evaluator.md               starts the evaluator
├── domain/
│   ├── orchestrator.md            what the orchestrator does
│   ├── tree-keeper.md             what the tree-keeper does
│   ├── generator.md               what the generator does
│   ├── evaluator.md               what the evaluator does
│   ├── tree-keeper-in.schema.json   the form of the tree-keeper's Cut and of each resume
│   ├── tree-keeper-out.schema.json  the form of what the tree-keeper gives
│   ├── generator-in.schema.json   the form of the generator's Cut and of each resume
│   ├── generator-out.schema.json  the form of what the generator gives, its Made among it
│   ├── evaluator-in.schema.json   the form of the evaluator's Cut
│   ├── evaluator-out.schema.json  the form of what the evaluator gives, its Answers among it
│   ├── tree/                      the code of tree.py, a module for each decision it makes
│   ├── sign-off.schema.json       the form of a Sign-off, which tree.py decides
│   ├── repository/                the code of repository, a module for each tool it runs
│   ├── record/                    the code of record.py, a module for each decision it makes
│   ├── record.schema.json         the form of a Record, which record.py decides
│   ├── fault.py                   how tree.py, record.py, throwaway.py, repository, and the
│   │                              adapters say why they stopped, and how each command ends
│   ├── throwaway.py               the code of throwaway.py
│   └── best-practices/            rn's own best practice of each kind
├── scripts/
│   ├── tree.py                    runs the code of tree.py
│   ├── record.py                  runs the code of record.py
│   └── throwaway.py               runs the code of throwaway.py
├── hooks/
│   ├── hooks.json                 starts the guard on each call
│   ├── lanes.json                 the steps the guard holds each role to
│   ├── lane/                      the guard: Lane's code, copied in by Lane
│   └── adapters/                  give the guard each start's text from its Cut, and the results
│                                  kept
└── README.md                      for rn's users

dev/rn/
├── product-vision.md              rn's product vision
├── architecture.md                this document
├── README.md                      for rn's developers
└── tests/                         the test cases, in unit/, properties/, prompts/, integration/,
    │                              and e2e/, with the E2E test files that dev/scripts/e2e.py runs
    └── gh/                        the double of gh, the records of gh it gives from in recorded/,
                                   and compatibility.py, which compares a new gh with them

.claude/worktrees/
└── rn-<yyyymmdd>-<goal>/          rn's worktree of one run, on the work's branch

.rn/
├── <yyyymmdd>-<goal>/             one run
│   ├── design-tree.json           the design tree
│   ├── sign-offs.json             what waits for /rn:ty, and what the user signed off
│   ├── rounds/                    each round's Try record, Made, Answers, More kept, and Place
│   └── records/                   the record of each start of a role, and the orchestrator's
└── best-practices/                each best practice made on a run
```

## Test strategy

Each test case lies in `dev/rn/tests/`, written as Given, When, and Then before anyone builds a part.
`dev/scripts/trace.py` checks that each names an element or a case one level up.

| Check | Test target | Kind | Exit criteria or measure |
|---|---|---|---|
| Lint | Parts | Quality | ruff: 0 findings. |
| Static analysis | Parts | Quality | pyrefly, and pylint's duplicate-code and cyclic-import checks: 0 findings. |
| Complexity analysis | Parts | Quality | complexipy and ruff: per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | pytest, with the double of Claude Code: every case passes. |
| Unit testing | Parts that hold a prompt | Benchmark | `claude -p` on Opus: each prompt's share of right runs, read by code, against the last version's. Precision and recall for the points put to the user and the `more` judged short. Runs per case: added until one more moves no share. |
| Code coverage | Parts | Quality | coverage: 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | hypothesis: 0 counterexamples in reading the design tree, the records, and the adapters' input. |
| Mutation testing | Parts | Quality | cosmic-ray: 0 surviving mutants. |
| Integration testing | Architecture | Quality | pytest, with the double of Claude Code: every case passes, each handoff giving the data the data model names. |
| Contract testing | Architecture | Quality | `dev/rn/tests/gh/compatibility.py` on each new gh: each recorded command gives what its line shows. Claude Code's is Lane's test. |
| Traceability | Architecture | Quality | `dev/scripts/trace.py`: every element tested, every case naming one level up, each rule's case failing broken. |
| Scenario testing | Product | Benchmark | `dev/scripts/e2e.py` on the walkthrough, judged on Opus: the key results KR1.1, then KR1.2, against the last runs. Runs: added until one more moves no mean by a step. |
| Installation testing | Product | Quality | `dev/scripts/e2e.py`: rn installs by the README's commands in a fresh home, and `/rn:up` answers. |
| Configuration testing | Product | Quality | CI's Tests on Python 3.9 and the newest Python: every case passes on each. |
| Conformance and compliance testing | Product | Quality | `claude plugin validate --strict`: passes. |
