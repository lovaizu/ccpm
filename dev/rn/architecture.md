# `rn` architecture

This document says how the parts of rn give what [its README](../../plugins/rn/README.md)
promises. rn builds up only the vital few of each deliverable, what its people can't do without, as
decisions in a design tree: the orchestrator, the main conversation, settles them, asking the user
only the points that are theirs, and a tree-keeper keeps them. A generator makes each deliverable
from its decisions, round after round, until evaluators that have only what its people have find
every necessary condition met, and the user signs it off before anything rests on it, while the
work that rests on no point or sign-off still waiting goes on. The orchestrator checks every result
before it takes it, and a lack changes the decision it comes from, not the deliverable.

## User stories

- S1: the user wants to type `/rn:up` with what they want, in their own words, so that they get the
  deliverable they mean without writing a specification. It carries the walkthrough's first
  `/rn:up`, the goal put to the user, and each deliverable made in rounds.
- S2: the user wants to answer each point rn puts to them, one at a time, while rn goes on with the
  work that rests on no open point, so that they spend their time only on what's theirs to decide,
  and the run waits for them only where the work needs their answer. It carries the answer
  `each file`.
- S3: the user wants to sign off the plan and each deliverable with `/rn:ty`, or send it back with
  `/rn:gm`, so that nothing rests on what they didn't mean, and nothing else waits for it. It
  carries the plan and each deliverable put up for sign-off, each `/rn:ty`, and `/rn:gm` with what
  to change or with their comments on the pull request.
- S4: the user wants to type `/rn:dn` and stop the run at any moment, so that they lose neither
  their time nor the work so far. It carries the walkthrough's `/rn:dn` and `Paused`.
- S5: the user wants to type `/rn:up` alone in a new conversation and have rn go on where it
  stopped, so that they never answer a point twice or wait for work made again. It carries the
  walkthrough's second `/rn:up` and `Picking up`.
- S6: the user wants one pull request, the decisions rn took without asking, and the lessons of the
  run, so that they check the work and merge it themselves. It carries the walkthrough's `Done`,
  each change to a best practice that rn proposes there, each lesson that it puts up for their
  sign-off, the whole pull request read before it's ready, and the merge.

## Components

![rn's components](images/components.svg)

What each decides alone:

- user\
  The goal, each point the purpose and the best practices leave open, each sign-off, each change to
  a best practice, each lesson sent to rn's repository, when to pause, and whether to merge.
- orchestrator\
  Whether a point is the user's, and each other point that the design tree holds, from the purpose
  and the best practices: the deliverables and their plan, each decision of a necessary condition,
  each point that a role hands back, which point or sign-off to put to the user next, whether to
  take each role's result or send it back, which lacks the people fall short by, the decisions that
  each sign-off shows as taken without asking, whether the whole pull request holds together, and
  what to propose at Done.
- tree-keeper\
  How each decision of the orchestrator's goes into the design tree, and whether each node that the
  change touches still agrees with it.
- generator\
  The deliverable, and each point that lies within it alone: one that its cut, the goal, and its
  best practice settle one way, and whose answer changes no decision of its cut and nothing of
  another deliverable, such as typing amounts as Decimal where the code already computes with
  Decimal. It hands each other point back with `asks`, as only the orchestrator sees the whole
  design tree.
- evaluator\
  Where the deliverable meets each necessary condition of its group for its people, and, where it
  doesn't, what they still lack.
- tree.py\
  The tree's form and which nodes a change touches; each deliverable whose turn has come to be
  doing, which is each one that rests on no open point and on no plan or deliverable not yet signed
  off; each role's cut, with each best practice the role works by; where each start's Record
  lies, a new file of the run's `records/` for each start, and the order of the starts; where each
  round keeps its Try record, Made, Answers, Lack kept, and Place, and their form; whether a lack
  is kept, only once a decision that answers its necessary condition changed since the round's
  cut; what waits for the user's sign-off, the pull request handed over among them, and what they
  signed off; the run's name, worktree, and branch; the runs left, and where each stopped; and when
  the run's work reaches its branch and its pull request: each commit, each push, the user's
  comments since a sign-off, the pull request marked ready, and a draft again when the user sends
  it back, and the issue of each lesson that the user signs off.
- repository\
  Each git and gh command that tree.py runs, and how it reads what they print: the worktree, each
  commit and push, the draft pull request, its comments, marking it ready and a draft again, and
  the issue.
- record.py\
  A record's form, and rn's check: whether a role's record holds each step of its part and each
  practice of each best practice of its cut where the step takes it, and whether its result names
  each item of each list it carries, and the result it accepted, kept in the record.
- throwaway.py\
  Where a deliverable's commands run.
- guard\
  Whether a role's call keeps its steps, whether rn's check accepts a role's record and result at
  its end, whether a deliverable's command runs only through throwaway.py, and whether the run
  passes a sign-off only after the user's `/rn:ty`, by the lanes that rn lays in
  [Lane](../lane/architecture.md), and, as Lane's guard decides them, which start is due and where
  a run picks up.
- adapters\
  How the Cut of a role's start, and the result that each record kept, read in the form Lane reads;
  which run's results a conversation picks up: the run of the worktree it works in, or, from
  anywhere else in the repository, the one run left; and which work of each role waits for a start
  beside the starts that run, as [Lane's adapter](../lane/architecture.md#data-model) decides it.

The choices made, and why:

- One generator for each deliverable over several side by side\
  Three generators would take about three times as long for a gain in KR1.1 that no end-to-end test has shown,
  which adds to KR1.2. The cost: a lack in a best practice shows only when its developers run several
  generators to check it.
- The orchestrator judging every point over a role of its own that settles them\
  The user talks with the one that decides, and no answer passes through a role that rewords it, which keeps KR1.2 short. The cost: the main conversation holds every judgment of the run.
- tree.py finding the work that waits on a point or a sign-off over the orchestrator judging it\
  A rule held in code holds on every run, so no work starts on an open point or on what the user
  didn't sign off, which keeps KR1.1 low, and no work waits that rests on neither, which keeps KR1.2
  short. The cost: each point waits for the tree-keeper to write it into the design tree before the
  user sees it.
- The adapter of the results kept picking up the one run left from the root of the repository over
  picking up only in a run's worktree\
  The user types `/rn:up` at the root, as the README's walkthrough shows, and Lane asks the adapter
  only as the skill is called, in the folder the conversation works in, as
  [Lane's S7](../lane/architecture.md#s7-a-run-picked-up) draws, so the guard picks the run up
  where it stopped, and no role starts its work over, which keeps KR1.2 short. The cost: with more
  than one run left, the adapter can't tell which one the user picks, so the guard starts its
  run anew, and the run's starts pass through the routes from their first move, the tree-keeper's
  start first.

## Data model

![rn's data](images/data-model.svg)

- Cut\
  The part of the design tree that a role starts with.
- Point\
  A question put to the user, with its recommendation, while its decision is open.
- Sign-off\
  The plan, a deliverable, a lesson for rn's repository, or the pull request handed over, put to
  the user for `/rn:ty` or `/rn:gm`, with what the people can do with it, the decisions taken
  without asking, and its changes, or with the lesson's words. The decisions taken without asking
  are each decision under it in the design tree that the user didn't settle, and, for a
  deliverable, each point that its last round's Made names.
- Made\
  What a generator made, as it ends with `done`: where the deliverable carries out each decision of
  its cut and meets each Lack kept, and each point it settled without asking, with its ground.
- Place\
  The step that each role of a round stands at, with the work it has made, kept at the end of each
  step and at a pause.
- Lack kept\
  A lack an evaluator named that the orchestrator judged the people fall short by, which the next
  round's generator gets.
- Record\
  What one start of a role, or the orchestrator in a run, carried out: each step and practice in the
  order taken, and the result that rn's check accepted, one for each start. A Try record is another
  thing: the commands that a generator tried in a throwaway copy.

## Principles

rn builds on [the plugin guide](../plugin-development-guide.md), and adds these rules,
which every part keeps. They change none of the guide's: the orchestrator resumes a role that
ends on a point with the decision, and with the user's words word for word where they answered, as
its [Messages](../plugin-development-guide.md#messages) says, as a new start would give the role
the tree-keeper's words for what the user meant, while the design tree keeps the decision for each
later round.

### Drawn out along the design tree

Each role starts with its own cut of the design tree alone, and the guard lets it start only with
the cut that `tree.py` gave for that role.

*Why*: a role that reads decisions not its own makes what the user didn't mean, which raises KR1.1.

### Every step by best practice

Each role works by the best practice of its kind of work, a generator finishes a document by the
refactor-doc best practice and code by the refactor-code one, and Lane holds it to the steps.

*Why*: an AI that skipped a step once skips it again, and the deliverable misses what the step makes
sound, which raises KR1.1.

### Every item handled

Each role reads in full what it starts with and each best practice its part names. It records each
step and each practice item it takes at the time each names, as
[the plugin guide](../plugin-development-guide.md#a-record-of-each-step-and-practice) says. Its result
names each item of each other list it carries: each decision of its cut it checked, each necessary
condition it judged, and each lack and comment it judged. Lane holds each read by its trace, and
the guard runs rn's check of the record and the result against the whole list at the role's end,
and at the end of the orchestrator's turn that puts work up for the user, as the guide says.

*Why*: an item dropped takes from the deliverable what the item holds, which raises KR1.1.

### Judged by the people it's for

An evaluator gets only what the deliverable's people have.

*Why*: an evaluator that knows what the maker meant judges the making, not what the people get, which
raises KR1.1.

### Signed off before it's built on

The plan and each deliverable reach the work that rests on them, and the pull request becomes ready,
only after the user's `/rn:ty`, which the guard holds the run to, and meanwhile each part goes on
with the work that `tree.py` gives its turn, as it rests on no sign-off or point still waiting.

*Why*: a wrong reading of what the user means, found only at the end, makes everything that rests
on it made again, which raises KR1.1 and adds to KR1.2, and a run that held all its work for each
point and sign-off would add the user's time away to the run's, which adds to KR1.2.

### Back to the design tree on a problem

A lack, or what the user sends back with `/rn:gm`, changes the decision it comes from, and the next
round makes the deliverable from the design, never with a fix beside it.

*Why*: a fix beside the design rests on no decision, so the next round, made from the design, loses
it or breaks another necessary condition with it, which raises KR1.1.

### The design tree revised on each run

What a run finds changes the design tree before the next deliverable, and the best practice before
the next run, once the user takes the change, which the orchestrator proposes before the merge.

*Why*: a design tree or a best practice kept as first laid out makes the same miss again, which raises
KR1.1 and adds to KR1.2.

### Tried in a throwaway copy

A deliverable's commands run only in a throwaway copy of the repository, with a throwaway home,
and a lane of Lane holds each role to it.

*Why*: a command run as the people run it would otherwise change the user's own files, and the
user would spend their time setting them right, which adds to KR1.2.

### The repository holds the work

Every part keeps the run's state only in the run's folder and the deliverables on the work's own
branch, in rn's own worktree, and `tree.py` commits them at the end of each step and at a pause.

*Why*: work kept only in a conversation that ends, or left uncommitted at a pause, makes the user
answer or wait for it again, which adds to KR1.2.

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
  O->>T: makes the run's worktree
  O->>O: enters it
  O->>K: starts it (Cut)
  K->>K: reads its part, the design tree best practice, and the design tree
  K-->>O: done
  O->>O: drafts the goal, and plans the deliverables
  O->>U: the goal, to confirm (Point)
  U->>O: answers
  O->>K: resumes it, with the goal and the plan (Decision)
  K->>T: writes them, and commits
  T-->>K: what changed, and each node they touch
  K->>K: checks that each node touched agrees with them
  K-->>O: what changed, and each node checked
  O->>O: checks it against the design tree best practice
  Note over U,O: The orchestrator settles each point, as S2 draws, and puts up the plan, as S3 draws.
  loop each deliverable whose turn has come, as it rests on no open point and on nothing not signed off
    GD->>A: asks for the text of the generator's start, with each start that runs
    A->>T: gets each deliverable doing, and the Cut of the first that no start that runs holds, with the path of a new Record for the start (Cut)
    A-->>GD: that start's text and run values in Lane's form, or none where no work waits
    GD-->>O: the generator's start due, with its text
    O->>G: starts it, with that text (Cut, Lack kept)
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
      GD->>R: checks its record and its result (Record)
      R-->>GD: each step, practice, or item they lack, or none, keeping the result in the record
      opt they lack one
        GD-->>G: holds its end, with what they lack
        Note over G,R: The generator carries out what they lack, and ends again. The guard holds each role's end, and the end of each turn of the orchestrator's that puts work up for the user, in the same way.
      end
      GD-->>O: done
      O->>O: checks it against the cut and the best practice
      alt it falls short
        O->>G: sends it back, with the ground
      else
        par one for each group of necessary conditions
          O->>E: starts it (Cut)
          E->>F: writes each necessary condition met, or what the people lack (Answers)
          E-->>O: done
        end
        O->>T: gets the round (Answers, Made)
        T-->>O: each evaluator's Answers, and what the generator made (Answers, Made)
        O->>O: judges each lack by the purpose and the best practices
        alt a lack the people fall short by
          O->>K: the decision it changes, and the lack kept (Decision, Lack kept)
          K->>T: writes the decision, and keeps the lack (Lack kept)
          alt no decision that answers the lack's necessary condition changed since the round's cut
            T-->>K: refuses the lack, naming its necessary condition
            K-->>O: what it lacks
            Note over O,K: The orchestrator takes the lack back to the decision it comes from, as a fix beside the design rests on no decision.
          else
            T-->>K: what changed, and the lack kept
            Note over O,G: The next round starts from the design.
          end
        else every necessary condition is met
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
    O->>K: the decision, with its ground, and the plan where the decision changes it (Decision)
    K->>T: writes it, and commits it with each deliverable whose turn has come marked doing
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
    O->>K: it's signed off, with the plan where it changed (Decision)
    K->>T: writes it, and commits it with each deliverable whose turn has come marked doing
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
  U->>O: /rn:up, alone, in a new conversation at the root of the repository
  GD->>A: asks for the results kept, as /rn:up loads, in the folder the conversation works in
  A->>T: gets the run of the worktree that holds the folder, or else the runs left, and each Record of the run in the order of its starts (Record)
  A->>R: gets the result kept in each of those records (Record)
  alt the folder lies in a run's worktree, or exactly one run is left
    A-->>GD: those results in Lane's form
    GD-->>O: where the run picks up, and the start due
  else no run is left, or more than one
    A-->>GD: none
    GD-->>O: the run started anew, and its first start due
  end
  O->>T: lists the runs left
  alt no run is left
    O->>U: says so
  else more than one is left
    O->>U: which one (Point)
    U->>O: answers
  end
  O->>O: enters the run's worktree
  O->>U: Picking up, where it stopped, and the point or sign-off waiting
  O->>K: starts it, on the run picked up (Cut)
  O->>G: starts each that stood in a step, at that step (Cut, Place)
  Note over O,G: Each start goes through the guard and the adapters in the run's worktree, the tree-keeper's first where the guard started the run anew, and the work goes on, as S1, S2, or S3 draws.
```

### S6: the work handed over

```mermaid
sequenceDiagram
  actor U as user
  participant O as orchestrator
  participant K as tree-keeper
  participant T as tree.py
  participant RP as repository
  participant GH as GitHub
  O->>O: finds each change to a best practice and each general lesson in the run's lacks
  loop each change to a best practice found
    O->>U: the change, with a recommendation (Point)
    U->>O: answers
    opt the user takes it
      O->>K: adds it as a deliverable (Decision)
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
        T->>GH: opens the issue on rn's repository
      else the user sends it back
        U->>O: /rn:gm, to turn it down or with what to change
        Note over U,T: The user's /rn:gm has tree.py drop it, and the orchestrator puts up again a lesson changed.
      end
    end
  and
    O->>O: reads the whole pull request at once, for each clash between deliverables and each part the goal doesn't need
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
Lane with it, and types `/rn:up` in Claude Code at the root of their repository.

- rn's own git worktree for each run, over the user's checkout\
  The user goes on with their own work while rn runs, and a pause leaves nothing of theirs to set right, which keeps KR1.2 short. The cost: a worktree on disk for each run until its merge.
- A best practice made on a run in `.rn/best-practices/` over the run's folder\
  Every later run in the repository finds it, and takes it over rn's own of the same kind, which keeps
  KR1.1 low. The cost: a later run misses what rn's own gains after it.

## Directory structure

rn's folder holds what Claude Code installs for the user. `dev/rn/` holds what only rn's developers
use. `.claude/worktrees/` holds rn's worktree of each run, and `.rn/` is what rn writes on the work's
branch.

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
│   ├── tree/                      the code of tree.py, a module for each decision it makes
│   ├── repository/                the code of repository, a module for each tool it runs
│   ├── record/                    the code of record.py, a module for each decision it makes
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
│   └── adapters/                  give the guard rn's best practices and design tree
└── README.md                      for rn's users

dev/rn/
├── product-vision.md              rn's product vision
├── architecture.md                this document
├── README.md                      for rn's developers
└── tests/                         the test cases, in unit/, properties/, prompts/, integration/,
                                   and e2e/, with the E2E test files that dev/scripts/e2e.py runs

.claude/worktrees/
└── rn-<yyyymmdd>-<goal>/          rn's worktree of one run, on the work's branch

.rn/
├── <yyyymmdd>-<goal>/             one run
│   ├── design-tree.json           the design tree
│   ├── sign-offs.json             what waits for /rn:ty, and what the user signed off
│   ├── rounds/                    each round's Try record, Made, Answers, Lack kept, and Place
│   └── records/                   the record of each start of a role, and the orchestrator's
└── best-practices/                each best practice made on a run
```

## Test strategy

rn tests by [the plugin guide](../plugin-development-guide.md#test), in unit tests, integration
tests, and end-to-end (E2E) tests. Its test cases lie in `dev/rn/tests/`, and `dev/scripts/trace.py`
checks that each names an element or a case one level up.

### Unit tests

- Tries: `tree.py`, repository, `record.py`, `throwaway.py`, and the adapters, each against its
  contract, and the prompts of the orchestrator, the tree-keeper, the generator, and the evaluator,
  each against what its line in Components and its steps in the sequences ask of it.
- Runs real: the part, with git in a temporary folder. A bare repository stands in for the remote,
  and a double of `gh` gives what [the manual of `gh`](https://cli.github.com/manual/) shows. A
  prompt's role runs alone on Opus in a throwaway copy of a repository that the test sets up, with
  `tree.py`, `record.py`, and `throwaway.py` real.
- Tools: pytest, coverage, cosmic-ray, hypothesis, ruff, complexipy, pyrefly, pylint's
  duplicate-code and cyclic-import checks, and `claude -p` on Opus for the prompts.
- Passes when: line and branch coverage of 100%; 0 surviving mutants; 0 counterexamples from the
  property-based tests of `tree.py`'s reading and writing of the design tree and its list of the
  nodes that a change touches, `record.py`'s check of a record against a prompt's steps and its best
  practices' practices, and each adapter's reading of a Cut or a record into Lane's form; for each
  function, McCabe complexity of 10 at most, cognitive complexity of 15 at most, and at most 6
  returns, 12 branches, 5 arguments, and 50 statements; 0 findings from pyrefly, ruff, and pylint's
  checks; and each case of a prompt passing on all of its k = 3 runs.
- Runs: the code's tests with their coverage and static analysis before each push and on each push
  in CI; mutation testing and the property-based tests in CI over the lines that a push changed on
  each push, and over the whole each night; and a prompt's tests before a change of the prompt is
  taken.

### Integration tests

- Tries: each path through the sequences of S1 to S6, each principle, where the parts keep it and
  where one breaks it, each decision of each component in Components, each handoff between parts
  with the data it passes, and each kind of data in the data model.
- Runs real: `tree.py`, repository, `record.py`, `throwaway.py`, the adapters, the guard as Lane
  lays it, and rn's lanes. The double of Claude Code in `dev/tests/` stands in for Claude Code, and
  sends each event as the recorded runs in `dev/tests/recorded/` show. A test plays the user, the
  orchestrator, and each role by the calls it makes on the double, and each role gives only results
  in the form of its part's output, which the role's unit tests show the real prompt giving. GitHub
  is the bare repository and the double of `gh` of the unit tests.
- Tools: pytest, the double of Claude Code, `claude plugin validate --strict`, and
  `dev/scripts/trace.py`.
- Passes when: every story, principle, component, and kind of data of this document has an
  integration test that names it; every test names an element or a case one level up that exists;
  every unit case names an integration case; each test of a principle fails where its fixture
  `broken` takes out the part that holds the principle, which `trace.py` runs; and each result of a
  double comes from a line of a record that names the recorded run or the page of the documentation
  that shows it, which `trace.py doubles` checks, and each such page still shows its words, which
  `trace.py sources` checks.
- Runs: with the unit tests of the code before each push and on each push in CI, and the check of
  the pages in CI with the checks of the tests, as a page changes apart from any push.

### E2E tests

- Tries: the key results KR1.1 and KR1.2, by the README's walkthrough at its real size: type hints
  for a library the size of invoicer, with the plan of its two deliverables, two points answered,
  each sign-off, and a pause and a pick-up in a new conversation.
- Runs real: rn and Lane, installed as the README says, on the real Claude Code on Opus, in a fresh
  clone of [lovaizu/playground](https://github.com/lovaizu/playground) that holds the library. An
  AI on Opus in the user's place holds an intent that rn never receives, and reads only what the
  screen shows, as `dev/scripts/e2e.py` runs it.
- Tools: pytest, `dev/scripts/e2e.py`, and a judge on Opus for KR1.1.
- Passes when: the key results, KR1.1, the share of the deliverables handed over that the judge
  finds their people can't use, and KR1.2, the time from the request to the deliverable, the
  stand-in's own time answering included, each taken from the records of every run; a change kept
  only where it improves a key result and leaves none before it worse than in the last runs, as the
  product vision orders them; the judge used only once it's right on each kept record whose answer
  is known; and 3 runs of the walkthrough after each change.
- Runs: once every unit and integration test passes, started by the developer.

- k = 3 runs of each case of a prompt over 1 or 5\
  A prompt that slips on 3 runs in 10 fails 3 runs of 3 about two times in three, so most slips
  that would make a deliverable unusable show before the E2E tests, which keeps KR1.1 low. The cost:
  each change of a prompt waits on 3 runs of each of its cases, and a slip rarer than 1 run in 5
  passes them more often than not.
- 3 runs of the walkthrough over 1\
  KR1.1 is a share, and one run hands over too few deliverables to show it move, which keeps a
  change that raised KR1.1 unseen. The cost: each change waits on 3 whole runs on Opus.
- Property-based tests of `tree.py`'s reading of the design tree and `record.py`'s check of a
  record over cases drawn by hand alone\
  An AI writes the tree and each record, so they take forms that no developer foresees, and a fault
  there hands a role another's cut or passes a record that skipped a practice, which raises KR1.1.
  The cost: each night's run of every input.
