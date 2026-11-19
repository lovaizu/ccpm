# Lane architecture

## User stories

- S1: a plugin, such as rn, wants its AI to notice when it writes a file that its step doesn't
  name.
- S2: a plugin wants its AI to notice when it reads a file that its step says never to read.
- S3: a plugin wants its AI to notice when it ends a step without reading whole a file that the
  step asks it to read whole.
- S4: a plugin wants its AI to notice when it runs a command other than those its step names.
- S5: a plugin wants its AI to notice when it skips a step, or ends before each step is done in
  order.
- S6: a plugin wants its AI to notice when it ends a step before each item of the step's checklist
  is done.
- S7: a plugin wants its run to move on only by the result its AI gives, never by what its reply
  says.
- S8: a plugin wants its AI to notice when it ends a step that the plugin's own check doesn't pass.
- S9: a plugin wants its main conversation to start each subagent that its order makes due, and
  only those, and not to end its turn while one is due.
- S10: a plugin wants a run that stopped to go on where it stopped, after `/compact` or in a new
  conversation.

## Solution strategy

### Principles

Lane gives an AI that leaves a step of its plugin the step's own sentence, so that it notices at
once.

- P1: the AI notices each step it leaves
  - P1.1: when Lane stops a call, it gives the AI the sentence of the step it left and what to do
    instead. Where it can't check a call, it says why and who fixes that.
  - P1.2: a step, an item, a read, or a result counts only from the AI's own call, never from its
    reply.
- P2: any plugin alike
  - P2.1: Lane names no plugin. A plugin gives Lane its rules, in the form Lane defines, in a file
    of its own folder.
  - P2.2: what only the plugin knows, such as a subagent's start text, a step's checklist, or the
    results it keeps, Lane asks of the plugin's adapters. Lane defines what each adapter takes and
    gives.
  - P2.3: Lane checks only a run of a skill of a plugin that gives it rules, from the skill's call
    until its routes end, and leaves other work alone.

### Data model

![Lane's data](images/data-model.svg)

- Rules\
  What a plugin gives Lane: each step's rules, each of one type with its values, and the routes.
- Route\
  The moves after a role's result, or after a command that the person types, which make starts
  due.
- Run\
  One run of a plugin's skill in a conversation, from its call until its routes start no more,
  with each start, read, mark, and result in it.
- Kept results\
  The results that a plugin keeps, from which a run goes on in a new conversation.

Strategies:

- A run's record that only grows, holding only what no later move gives again. [S10]\
  Intent: moves checked at the same moment lose nothing of one another's.

### Components

![Lane's components](images/components.svg)

- guard (hook)\
  Holds each move of a run to its plugin's rules and order.
- rule types (module)\
  Make each rule's check and the sentence it gives one, so that what the AI reads is what holds.
- reporters (command)\
  Carry a step, an item, or a result done to the guard as the AI's own call.

Strategies:

- The plugin's folder found from the base directory of its skill, which Claude Code writes into
  the conversation as the skill starts, as
  [the research](../../.rn/20261107-rn/research/how-lane-finds-a-plugins-folder.md) found. [P2.1]\
  Intent: Lane serves a plugin that it never names, as Claude Code gives the folder either way.
- The reporters as commands that Claude Code puts on the AI's path. [P1.2]\
  Intent: a plugin's step names a reporter without knowing where Lane lies.
- A rule of the paths a role writes that names a folder letting through each file under it. [S1]\
  Intent: a deliverable of several files, such as code with its tests, is written whole.
- Each move placed on its run and start by what Claude Code's events carry, as
  [its states](claude-code-states.md) list. [P2.3]\
  Intent: each move is held to the rules of its own start, and to no other run's.

### Sequences

#### S1 to S8: a move held to its step's rules

```mermaid
sequenceDiagram
  participant SA as the plugin's AI
  participant G as guard
  participant T as rule types
  participant A as the plugin's adapters and checks
  participant R as reporters
  participant RR as run record
  SA->>G: a call: a write, a read, or a command [S1]
  G->>T: checks it by each rule of its step (Rules) [S2]
  alt it breaks a rule [S4]
    G-->>SA: stops it, with the step's sentence and what it may do [P1.1]
  else a read of a file that a rule asks read whole [S3]
    G->>RR: adds the read (Run) [P1.2]
  end
  SA->>R: reports a step or an item done [S5]
  opt a rule of the step keeps a checklist [S6]
    G->>A: asks for the step's items [P2.2]
  end
  alt the step isn't due, or it lacks a read or an item that its rules ask [S5]
    G-->>SA: stops it, with what the step lacks [P1.1]
  else [P1.2]
    G->>RR: adds the mark (Run) [P1.2]
  end
  SA->>R: reports its result [S7]
  alt a result its role may give [S7]
    G->>RR: adds the result (Run) [P1.2]
  else [S7]
    R-->>SA: refuses it, with the results it may give [P1.1]
  end
  SA->>G: ends [S5]
  alt no result, or a step left unmarked [S7]
    G-->>SA: stops the end, with the step's sentence [P1.1]
  else a rule holds the end to the plugin's check [S8]
    G->>A: runs the check, with the result [S8]
    A-->>G: whether it passes, and the guard stops the end where it fails [P1.1]
  end
```

Strategies:

- A mark checked for the step due, then for the reads and the items that its rules ask. [S5]\
  Intent: a skipped step, item, or part of a file shows at the step skipped.
- An end checked for its result first, then its steps, then the plugin's own check. [S8]\
  Intent: a stop names the step left, as the plugin's check runs once the result and each step
  hold.

#### S9: starts held to the plugin's order

```mermaid
sequenceDiagram
  actor U as person
  participant M as the plugin's main conversation
  participant G as guard
  participant A as the plugin's adapters
  participant RR as run record
  U->>M: the plugin's command [S9]
  M->>G: calls the skill [P2.3]
  G->>RR: adds the run, as S10 draws where one stopped (Run) [S9]
  loop until the routes start no more [S9]
    opt the plugin gives a start's text of its own [P2.2]
      G->>A: asks for the text of each start due [P2.2]
    end
    G-->>M: the starts due, each with its text (Run) [S9]
    alt a start due [S9]
      M->>G: the start [S9]
      G->>RR: adds the start (Run) [S9]
    else any other start of the plugin's subagents [S9]
      G-->>M: stops it, with the starts due [P1.1]
    else the main conversation ends its turn while a start is due [S9]
      G-->>M: stops it, with the starts due [P1.1]
    else the person types a command that a route waits for [S9]
      U->>M: the command [S9]
      G->>RR: adds it, so that its route's starts are due (Route) [S9]
    end
    G-->>M: each result, and the starts that its route makes due (Route) [S7]
  end
```

Strategies:

- A typed command that a route goes after, its starts due in place of those before. [S9]\
  Intent: the person's pause or approval changes the order.

#### S10: a run picked up

```mermaid
sequenceDiagram
  actor U as person
  participant M as the plugin's main conversation
  participant G as guard
  participant RR as run record
  participant A as the plugin's adapter
  U->>M: the plugin's command, after /compact or in a new conversation [S10]
  M->>G: calls the skill, with the words typed after the command [S10]
  alt the run record holds the run, not ended [S10]
    G->>RR: reads where the run stands (Run) [S10]
  else the plugin gives an adapter of the results it keeps [P2.2]
    G->>A: asks for the kept results, with those words (Kept results) [P2.2]
    G->>RR: adds the run, with each result that follows the routes (Run) [S10]
  end
  G-->>M: where the run picks up, and the starts due [S10]
```

### Deployment

![Lane's deployment](images/deployment.svg)

A plugin names `lane` among the dependencies of its `plugin.json`, so that Claude Code installs
Lane beside it, and Lane's guard holds each run of the plugin's skills.

Strategies:

- Lane's code on Python 3.9 and its standard library alone. [P2.1]\
  Intent: the guard, started anew on each move, answers fast on each machine that runs a plugin.
- The plugin's adapters and checks run in the folder that the conversation works in. [P2.2]\
  Intent: each reads the run's checkout, in a worktree too.

### Directory structure

```text
plugins/lane/                     what Claude Code installs beside each plugin that depends on it
├── hooks/
│   ├── hooks.json                the guard's entries
│   └── lane/                     the guard, and lanes/, the rule types
├── bin/                          the reporters
├── docs/rules-and-adapters.md    what Lane takes in and gives out
└── README.md                     for a plugin's author

dev/lane/                         what only Lane's developers use
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, from unit to integration

<a plugin>/lane/                  what a plugin gives Lane
├── rules.json                    the rules and the routes
└── adapters/                     each adapter
```

## Test strategy

| Check | Test target | Kind | Exit criteria or measure |
|---|---|---|---|
| Lint | Parts | Quality | 0 findings. |
| Static analysis | Parts | Quality | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | Every case passes. |
| Code coverage | Parts | Quality | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | 0 counterexamples in reading the rules, each rule type's check, and the guard's placing of moves. |
| Mutation testing | Parts | Quality | 0 surviving mutants. |
| Integration testing | Architecture | Quality | Every case passes, each handoff giving the data the data model names. |
| Contract testing | Architecture | Quality | On each new Claude Code, each recorded state gives the double's events. |
| Traceability | Architecture | Quality | Every element tested, every case naming one level up, and each principle's case failing broken. |
| Configuration testing | Product | Quality | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | Claude Code's strict check of Lane's plugin passes. |
