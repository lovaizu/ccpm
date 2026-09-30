# rn design

## The benefits, and the features that give them

Five features give the README's three benefits. Under each feature are the README stages where it
works.

```mermaid
flowchart LR
    F1["It works out the goal and the design with the user<br/>README 1, 3"]
    F3["An evaluator that did not make the work checks it<br/>README 4"]
    F2["It calls the user only for decisions that are theirs<br/>README 2, 4"]
    F4["A sign-off comes with a proposal and its grounds<br/>README 2, 6"]
    F5["Everything decided is pushed, so any conversation goes on<br/>README 5"]
    B1(["You get what you really want,<br/>without writing a careful prompt first"])
    B2(["Your time goes only to<br/>the decisions that are yours"])
    B3(["Work that takes days goes on<br/>from where it stopped"])
    F1 --> B1
    F3 --> B1
    F3 --> B2
    F2 --> B2
    F4 --> B2
    F5 --> B3
```

## Who does what, and what holds throughout

- The conductor is the main conversation with the user, and decides every next move.
- A generator makes one task's result.
- An evaluator checks one thing against the essential viewpoints and answers each with Good and More.

    An essential viewpoint is a question the thing must answer yes to. A Good is what serves it, and
    a More is what falls short.

- A fatal More is one the goal cannot be achieved without, and whose fix only the user can decide.
- `writ`, a plugin `rn` depends on, writes and checks the README and design document.
- Each decision is committed with a decision line that says what was decided and what comes next.

    The commit where `rn` stops for the user is the stop commit.

The whole session, from the inside:

```mermaid
flowchart TD
    ON(["/rn:on"])
    W["Work out the plan with the user"]
    P["Write the plan, evaluate it"]
    PS{{"Plan sign-off"}}
    D["Work out the design with the user;<br/>writ writes and checks the README<br/>and design document"]
    DS{{"Design sign-off"}}
    P2["Plan the tasks that make the deliverable,<br/>evaluate them"]
    T["Carry out the tasks one by one"]
    EV["Evaluate the deliverable"]
    T2["Carry out the added tasks"]
    FS{{"Deliverable sign-off"}}
    END(["Mark the pull request ready"])
    ON --> W --> P --> PS
    P -->|"a fatal More"| W
    PS -->|"/rn:gm"| W
    PS -->|"/rn:ty"| D
    D --> DS
    DS -->|"/rn:gm"| D
    DS -->|"/rn:ty"| P2
    P2 --> T
    T -->|"the design must change"| D
    T -->|"all tasks done"| EV
    EV -->|"tasks to add"| T2
    EV -->|"a fatal More"| D
    T2 --> FS
    EV -->|"no tasks to add"| FS
    FS -->|"/rn:gm, fixed within the design"| T2
    FS -->|"/rn:gm, changes what<br/>the product should be"| D
    FS -->|"/rn:ty"| END
```

Six policies hold across the features:

- Only the conductor decides what happens next.

    Decisions are made where the goal and the whole conversation are known, so a fix keeps what
    already serves the goal. An evaluator sees only the thing, and fixes decided by its words would
    rebuild what works.

- Only the conductor uses git.

    Every commit then records a decision someone actually made, so a later conversation goes on from
    real decisions, not from one nobody made.

- Everything is made and checked with the same essential viewpoints, and `rn` is improved by
  sharpening them, not by adding steps.

    A viewpoint asks what the work is for, so it fits situations no one foresaw and the user gets
    work that serves the goal. An added step is followed even where it misses.

- Every role is handed the paths of what it reads, never a summary of them.

    Each role then reads the thing itself, so what it makes or finds holds for the thing. A summary
    carries the summarizer's reading, and the role would work from that instead.

- Documents lead the work and hold only what holds now.

    A decision written down outlives a cleared conversation, and a document without history shows
    what holds at a glance, so the user never explains again what was already decided.

- `rn` decides what goes into the README and design document, and `writ` writes and checks them.

    The viewpoints for documents then live in one place, so the documents the user approves read as
    well as any `writ` writes, and improving `writ` improves them. Two copies would drift apart.

## It works out the goal and the design with the user

The conductor works out the plan before anything else, since what the user gets is what they meant
only when the goal is theirs (README, 1. Start). It makes the plan itself, not through a generator,
because the plan is worked out in the conversation it holds. It looks things up while talking
instead of finishing the research before asking, since the user's answers change where to look. The
plan has its own sign-off, because a design worked out on a wrong goal is wasted.

The design is worked out the same way, with what to test and what passes. What is agreed goes to
`writ`, which writes it into the README and design document and returns the final Good and More for
its viewpoints, for the Design sign-off. There is always a Design sign-off, even when the design
document does not change, since the user sees how it will be built and checked before anything is
built (README, 3. Work out the design). Tasks that make the deliverable are planned only once the
design is approved; tasks planned before the design would mostly be rewritten once it is.

After feedback at a sign-off, the session goes back to before it: a plan or a design is worked out
again with the user, taking the mismatch behind the feedback as the first point, since fixing only
what the words say leaves the mismatch in place. Feedback on the deliverable that changes what the
product should be goes back to working out the design, through a Design sign-off, since the README
and design document are what the user approved the product to be.

## It calls the user only for decisions that are theirs

The user is asked only what only the user can decide: taste, scope, effort against safety, whether to
wait for someone outside, what the product should be, another way when fixes keep falling short, and
whether the deliverable achieves the goal. Everything else is looked up or decided from the goal, so
the user's time goes only to what is theirs.

Whenever `rn` calls the user, at a question or a sign-off, it comes with what it proposes to do next
toward the goal, and why. A report of where things stand would leave the user to work out what to do
next, which is the work they left to `rn`.

A question is put so the user can answer it on the spot. When the work waits on someone outside,
what to do meanwhile is such a question, not a stop: a stop leaves the user unsure what `rn` is
waiting for.

Approving and giving feedback each stop, since that is where the user may clear the conversation.

Once approved, the goal, the README, and the design document go back through their sign-off only
when what the product should be, or how it is built, changes without the user having decided it.
Two kinds of change are written without stopping: a correction that changes neither, such as a line
number gone stale, and a change the user made by answering a question. The next proposal shows them
first, as changed since the last approval, so the user approves what they read without being
stopped for what they already decided.

## An evaluator that did not make the work checks it

```mermaid
flowchart TD
    U(["User"])
    C["Conductor in the main conversation"]
    G["Generator, one per task"]
    E["Evaluator, one per evaluation"]
    U -->|"conversation, commands"| C
    C -->|"proposals, with the final<br/>Good/More as grounds"| U
    C -->|"a task, a More to fix"| G
    G -->|"edits in the working tree"| C
    C -->|"a commit or document to evaluate"| E
    E -->|"evaluation"| C
```

The conductor stays the same conversation throughout the session, since what was talked through
stays with it. A fresh generator is started for each task, so its attention holds only that task,
and a fresh evaluator for each evaluation; each ends when done. A generator edits the working tree
and returns; the conductor checks the result against the task's purpose, commits, and has it
evaluated.

An evaluator receives only what the user agreed to and what the user said, never how the thing was
made or what it was changed to answer. Someone who did not make it, reading from the user's side,
sees where the user will struggle; whoever made it reads it along their own reasons.

Everything `rn` makes, such as a plan or a task's result, has a purpose, stated as what whoever
receives it can then do. For a plan, that is "can the conductor carry the work to the goal by it",
not "does it list tasks". Whether it was done can be met by following steps; whether it serves its
purpose can be answered only by looking at the real thing. Making and checking read the same
viewpoints, so they do not drift apart.

Good and More carry the same weight. Both point to a place in the real thing and say why. A Good
adds what the user gains from it, which a fix must not take away; a More adds what the user will
struggle with because of it. How to fix it is left to the conductor: a fix written into the
evaluation would pull that decision toward the evaluator's first idea.

```mermaid
flowchart TD
    M["The generator makes a task's result"]
    K{"The conductor checks it<br/>against the purpose"}
    V["An evaluator evaluates once"]
    KE{"The conductor checks the evaluation"}
    D{"The conductor decides<br/>each More in turn"}
    F["The generator fixes"]
    J{"The conductor checks the final<br/>Good/More for each viewpoint"}
    N["On to the next task,<br/>or to the sign-off"]
    U["Back to working out the design,<br/>or the plan for a plan"]
    M --> K
    K -->|"purpose not fulfilled"| M
    K -->|"purpose fulfilled"| V
    V --> KE
    KE -->|"no grounds, off the purpose"| V
    KE -->|"sound"| D
    D -->|"fix"| F
    F -->|"checked against the purpose"| D
    D -->|"let go, or all decided"| J
    D -->|"cannot go on"| U
    J -->|"no fatal More"| N
    J -->|"a fatal More"| U
```

Each Good's grounds are checked as a More's are, since a wrong Good has the fix keep what should
change. Then the conductor decides each More in turn:

- A More whose fix brings the work closer to its purpose, and keeps the Goods, is fixed.
- A More whose fix would not bring the work closer is let go, with the reason.

    Its cost, or that the fix needs the README, the design document, or the user, is never that
    reason.

Because the conductor decides, the repetition always ends as either settled or cannot go on. It
cannot go on when the same More keeps coming back, when each fix brings a new More, or when a fix
needs the README or the design document changed.

Fixes after the evaluation are checked by the conductor against the purpose, not by a fresh
evaluator. An evaluation is not repeated, since each AI evaluation raises new points that are not
essential, and repeating never settles; for the same reason the whole deliverable is evaluated once,
when the tasks planned after the last Design sign-off are done. The user can check every final Good
and More at its place, and ask with `/rn:gm` for anything, another evaluation included.

When Mores contradict each other, `rn` does not pick one. They are a sign that something is
undecided in the goal, the essential viewpoints, or a document, so that is what gets decided.

A plan follows the same flow, with the conductor making and fixing it.

## A sign-off comes with a proposal and its grounds

```mermaid
flowchart TD
    J{"Final Good/More<br/>for each viewpoint"}
    U["Back to working things out,<br/>that More first"]
    R["The proposal, committed<br/>as the body of the stop commit"]
    P(["The user reads it"])
    L(["/rn:up in a later conversation<br/>gives the same body"])
    J -->|"a fatal More,<br/>or cannot go on"| U
    J -->|"otherwise"| R
    R --> P
    R --> L
```

When every More is decided, the conductor checks the final Good and More for each question of the
essential viewpoints. A fatal More, or work that cannot go on, goes back to working things out with
the user instead of to the sign-off, since having the user approve something that is no use until
fixed only spends their time.

Otherwise `rn` gives the proposal: what it wants to do next, such as building on this design, and
why that serves the goal. Then, as its grounds, it gives under every question, put in the user's
language, the final Good and More, each at its place in the real thing and with its grounds, claiming
no more than that place shows. The points and fixes along the way are left out: the user approves the
final state, and with those they would have to work out where each applies now.

The user is given the body of the stop commit word for word, so what the user read and what a later
conversation gives never differ.

## Everything decided is pushed, so any conversation goes on

```mermaid
flowchart TD
    U(["User"])
    C["Conductor"]
    E["Evaluator"]
    G["Generator"]
    UP(["/rn:up"])
    S["steering.md:<br/>how the work goes"]
    RD["README and design document:<br/>what the product should be, and how it is built"]
    O["open/:<br/>items not yet settled"]
    M["Commit messages:<br/>the decision line, and settled items"]
    C -->|"writes"| S
    C -->|"what is agreed with the user, via writ"| RD
    E -->|"evaluation"| O
    U -->|"words given with /rn:gm"| O
    C -->|"notes left by /rn:dn"| O
    O -->|"the conductor decides and settles"| M
    S -.->|"reads"| G
    RD -.->|"reads"| G
    RD -.->|"reads the parts agreed"| E
    S -.->|"reads"| UP
    O -.->|"reads"| UP
    M -.->|"reads the last decision line"| UP
```

Every decision is committed and pushed as it is made. A fresh conversation, on `/rn:up`, reads
`steering.md`, `open/`, and the last decision line, and takes up the next move, in the language that
line is written in. For a session started under an older version of `rn`, `/rn:up` works the goal
out again from the old record and stops at a new Plan sign-off.

A session works on its own branch with a draft pull request, so the user's default branch changes
only when they merge. The user reads everything on the pull request, where diffs, long documents,
and diagrams render, and the record stays with the code.

What is not yet settled goes in `open/`, as it was received: an evaluator's evaluation, the user's
words received with `/rn:gm`, and the notes `/rn:dn` leaves, with an unfinished task's edits
committed beside them, so nothing needed to resume is only in the working tree. A file is named
`{NN}-{kind}-{about}.md`: the number keeps the order they came in, and the kind, `evaluation`,
`feedback`, or `notes`, says who wrote it and so how it is settled. A settled item leaves `open/` in
the commit that settles it, copied whole into that commit's message with the decision on each More,
so the record lives in git and leaves no file behind in the repository. `open/` is always empty when
the session stops at a sign-off.

A settled evaluation looks like this in its commit message:

```
rn: settle the evaluation of #3 move src/cart

- src/cart/price.ts:12 still takes `any` for the quantity; last quarter's cart bug would ship
  → fixed: typed the quantity as number

● #3 move src/cart ── decided: purpose fulfilled → #4
```

- The evaluation is copied whole.

    The Goods to keep and the Mores stay readable after `open/` is emptied.

- Each More ends with `→ fixed:`, `→ let go:`, or `→ to the user:`.

    The user and a later conversation see what became of each.

- The decision line comes last.

    `/rn:up` finds the next move by `●`, `──`, `→`, and `waiting for #{id} {sign-off name}`, which
    stay as written. The rest is in the user's language, which a later conversation takes from it.

### A session has one directory under .rn/

```
repository/
├── README.md                   what the product should be, to whoever uses it
├── docs/
│   └── design.md               how it is built
└── .rn/
    └── {yyyymmdd}-{slug}/      one session
        ├── steering.md         how the work goes
        └── open/               items not yet settled
```

The README and design document are where they are shown when nothing else is specified; another
place can be agreed with the user while working out the plan. The agreed place stays in the `ux`
and `design` fields of `steering.md`. The layout under `.rn/` cannot be changed, since `/rn:up` finds
the session by it.

A session leaves behind only this directory and the deliverable. The README and design document
belong to the product: they stay after the session ends, and the next session starts from them.

### steering.md holds the goal and the plan in one place

Any role, even after a fresh conversation, can read this and work from the same goal and plan. For
the move to TypeScript, `steering.md` right after the Design sign-off looks like this:

```markdown
---
rn: 0.9.0
pr: https://github.com/you/repo/pull/42
status: running
ux: README.md
design: docs/design.md
---

# Goal

Stop the production bugs from last quarter caused by a value of the wrong type before they ship.
A wrong type fails the build.

# Goal achieved when

- Code reproducing each of the three bugs fails the build, all three
- Every file is .ts

# Assumptions

- **Fact** (checked in the bug records): the three bugs are in src/cart and src/checkout
- **Fact** (the user decided): type checks are strict from the start
- **Assumption**: the build runs tsc in CI

# Rules

- Tests sit next to the code they test, as `*.test.ts`

# Tasks

### [x] #1: Plan sign-off
### [x] #2: Design sign-off
### [ ] #3: move src/cart

**Purpose**: in the cart's price calculation, a wrong type fails the build

**Purpose achieved when**:

- Code reproducing the cart bug fails the build

### [ ] #4: move src/checkout
### [ ] #5: move src/account
### [ ] #6: Deliverable sign-off
```

- `rn` tells a session started under an older version.

    `/rn:up` can then bring it to the current form.

- `pr` keeps the place where the user reads everything.

    It is not lost when the conversation changes.

- `status` is `running` or `finished`.

    Every command then judges the same way whether the session has ended.

- `ux` and `design` fix the one README and the one design document.

    Every role reads the same documents across conversations.

- Goal is what the user wants and why, as agreed with them.

    It is the basis of every decision.

- Goal achieved when is what the Deliverable sign-off judges the goal by.
- Assumptions keep checked facts apart from unchecked assumptions.

    A decision resting on an assumption can then be told.

- Rules hold what a generator cannot tell from the goal, such as the repository's conventions.
- Each task holds its purpose and how to tell it is fulfilled.

    The conductor checks against the purpose. Sign-offs are tasks too, and make the map of tasks
    shown at the head of every stop.

## How to check that the user gets each benefit

`rn` is made of prompts, so the same input does not behave the same way every time, and no test can
compare it against a fixed answer. So before writing the prompts, for each benefit in the README, it
is set what the user struggles with if it fails, in which scene it is checked, and what passes; after
writing them, they are checked in two ways.

- Running: `rn` is run with `claude -p --plugin-dir` on a practice repository on GitHub holding a
  small JavaScript app, with cases planted where a benefit would visibly be lost.

    A stand-in for the user answers one turn at a time, carrying the conversation over, and knows
    only what a real user would. An evaluator that did not make it evaluates the conversation,
    `steering.md`, `open/`, the commits, the pull request, and the deliverable against the pass
    criteria below. Prompts that read as correct do not guarantee an AI behaves that way.

- Reading: an evaluator that did not write the prompts reads them against the essential viewpoints
  for prompts and this design document.

    From every command, it traces end to end who writes what and who reads it, looking for something
    read that nothing writes, or something written that nothing reads. Running may not pass through
    branches that are hard to trigger, so those are checked by reading.

The benefits come first, and what the user takes for granted after: an `rn` that is only correct
gives no reason to use it (README, the line on other agents). A run is judged first on the benefits,
and while one fails, what the user takes for granted is not what is fixed first, since those failures
are the easiest to see and would leave the benefits never measured.

### You get what you really want, without writing a careful prompt first

If this fails, the user has to write a careful prompt, as with other agents, or gets what they said
instead of what they wanted.

- A rough goal whose words, taken as they are, would build the wrong thing, such as a partner's list
  whose short entries could be read two ways.

    Passes when the approved goal differs from the first words where those would have gone wrong,
    and the evaluator can name what each difference prevented.

- Feedback at the Plan sign-off whose words point at a symptom of a deeper mismatch.

    Passes when the next plan fixes the mismatch, not only what the words said.

- A decision only the user can make while working out the design, such as how strict the type
  checks start.

    Passes when the user decides from the question alone, and the approved design holds the answer.

- A goal set up so that a More comes up whose fix the goal does not determine.

    Passes when the user is asked about that More before the Deliverable sign-off, not at it.

- The deliverable at the Deliverable sign-off.

    Passes when it meets Goal achieved when in `steering.md` beyond its letter: in the TypeScript
    example, code reproducing each of the three bugs fails the build, all three.

### Your time goes only to the decisions that are yours

If this fails, the user babysits the work, or re-reads all of it at each sign-off, which is what `rn`
is chosen to spare them.

- A whole session, from `/rn:on` to the Deliverable sign-off.

    Passes when every time the user is called is a sign-off or a question only they can decide, and
    the evaluator agrees for each one.

- The work waits on someone outside, such as a partner's answer.

    Passes when the user is asked what to do meanwhile, and is never left waiting without knowing
    why.

- A correction to the approved README that changes neither what the product should be nor how it is
  built.

    Passes when it does not stop, and a stand-in reading only the next proposal can tell what changed
    since the last approval.

- Each of the three sign-offs.

    Passes when a stand-in for the user who reads only the proposal decides yes or no, and the
    evaluator, reading the real thing, finds the same decision right.

### Work that takes days goes on from where it stopped

If this fails, the user cannot hand over work that does not fit in one conversation, or explains it
all again each time.

- `/rn:dn` in the middle of a task, then `/rn:up` in a fresh conversation.

    Passes when it starts from the same task, does not redo finished ones, speaks the user's
    language, and asks nothing already decided.

- `/rn:up` at a sign-off in a fresh conversation.

    Passes when a stand-in decides from what it gives as from the first proposal.

### What the user takes for granted

If these fail, the user loses what an upgrade carried, approves on a claim that does not hold, or
cannot tell why things came out as they did.

- `/rn:up` on a session started under 0.8.0.

    Passes when a `steering.md` in the current form, carrying over what was done, is made, and it
    stops at the Plan sign-off.

- `/rn:gm` at the Deliverable sign-off, fixable within the design.

    Passes when tasks are added and carried out, and it stops at the Deliverable sign-off again.

- `/rn:gm` at the Deliverable sign-off, changing what the product should be.

    Passes when it works out the design with the user, stops at a Design sign-off, and then at the
    Deliverable sign-off again.

- Each of the three sign-offs.

    Passes when every Good and More in the proposal holds when the evaluator checks it at its place.

- Every scene.

    Passes when the evaluations, and the decision on each More, are in the commit messages, whole;
    `open/` is empty at every sign-off; and each stop's message is its commit's body.

What a script can decide, such as `open/` being empty at a stop or a stop's message matching its
commit, is checked by a script over the run's commits, not by the evaluator: it is faster, gives the
same answer every time, and leaves the evaluator's attention for whether the user gets the benefits.

Each scene is run once. A run takes time and money, so measuring the spread over many runs is given
up, and reading makes up for it. That only the conductor uses git, and which role reads what, are hard
to tell from a run's conversation, so they are checked by reading only. Sessions that last days,
large repositories, and differences between models are not checked here.
