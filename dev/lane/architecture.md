# Lane architecture

## User stories

- S1: the user wants their roles to notice at once when they leave the steps or order, writing no
  check.
- S2: the user wants a run that stopped to go on where it stopped, in the order they designed.

## Solution strategy

### Principles

Lane turns the user's steps into checks once, and judges each move of a run by them.

- P1: the steps as the one source
  - P1.1: a proposal comes from the steps alone, and each change asked goes into the steps.
  - P1.2: each rule's sentence, its check, and the steps it suits come from one definition.
- P2: laid only as the user read it
  - P2.1: only a proposal shown is laid, while the steps read as shown.
  - P2.2: what Lane laid is replaced whole, and every other part of the plugin stays as it stands.
- P3: facts, never a role's claim
  - P3.1: a run moves only on a result that its role reported, never on its reply.
  - P3.2: a step or an item counts as done only from the role's own report, checked as it reports.
- P4: the order the user set
  - P4.1: only the main conversation starts the roles, each as a start due.
  - P4.2: each stop gives the step's sentence and what to do, or why it can't check and who fixes
    it.
- P5: nothing lost on a stop
  - P5.1: each run's state comes from what was kept, worked out by one code alone.
- P6: only the plugin's run
  - P6.1: moves are checked only within a run of the plugin's skill.
  - P6.2: the laid plugin needs only its own folder and what each machine running it has, naming
    no plugin.

### Data model

![Lane's data](images/data-model.svg)

- Step\
  One numbered item of a role's steps, as the user writes it.
- Rule\
  A check of one type on one step, with its values, such as the plugin's check. It gives the
  sentence that the role gets where it leaves the step.
- Route\
  The moves after a role's result, or after a command that the person types, which make starts and
  resumes due.
- Proposal\
  The rules and routes put to the user, kept by its ID with the steps as they read when shown.
- Item\
  One item of a step's checklist, which only the user's plugin knows.
- Run\
  One run of the plugin's skill in a conversation, from its call until its routes start no more.
  It holds each command typed in it.
- Start\
  One start or resume of a role in a run, with the values that its rules hold it to.
- Read\
  A role's read of the lines of a file that a rule asks read whole.
- Mark\
  A role's report that a step or an item is done.
- Result\
  What a role reports at its end, by which the run moves.
- Kept results\
  The results that the user's plugin keeps, from which a run goes on in a new conversation.

Strategies:

- A run's record that only grows, holding only what no later move gives again. [P5.1]\
  Intent: moves checked at the same moment lose nothing of one another's.

### Components

![Lane's components](images/components.svg)

- proposer (prompt)\
  Turns the user's steps into the rules and routes that the user would lay.
- layer (script)\
  Lays into the plugin only what the user approved, as they read it.
- rule types (module)\
  Make each rule's sentence and its check one, so that what the user reads is what holds.
- guard (hook)\
  Holds each move of a run to the user's steps and order.
- reporters (script)\
  Carry a role's result and each step or item done to the guard as facts.

Strategies:

- A proposal from what the steps mean, by a prompt. [P1.1]\
  Intent: a step that names no subagent still gets its routes.
- Each skill as one role, its steps lying in several files, such as a command a route waits for.
  [S1]\
  Intent: the skill's steps hold across each command of the run, though nothing marks where one
  ends.
- A start's text, a step's checklist, and the kept results asked of the plugin's own adapters.
  [P6.2]\
  Intent: Lane names no plugin, and each plugin gives what it alone knows.
- An end held to the plugin's own check where a step ends on one. [S1]\
  Intent: a role that leaves its steps still meets the check that only the plugin knows.
- A rule's sentence left out of a step that already says it. [P1.2]\
  Intent: the role reads each rule once, and keeps its attention on its step.
- The form of the laid Rules and Routes decided by the guard's code, which the layer writes
  through. [P6.2]\
  Intent: a laid plugin runs by its laid copy alone.
- Each move placed on its run and start by what Claude Code's events carry, as
  [its states](claude-code-states.md) list. [P6.1]\
  Intent: each move is held to the rules of its own start, and to no other run's.

### Sequences

#### S1: a run held to the user's steps and order

```mermaid
sequenceDiagram
  actor U as user
  participant P as proposer
  participant L as layer
  participant T as rule types
  participant ST as steps
  participant CC as Claude Code
  participant M as the plugin's main conversation
  participant SA as the plugin's subagent
  participant G as guard
  participant A as the plugin's adapters and checks
  participant R as reporters
  participant RR as run record
  U->>P: asks for the checks of their plugin [S1]
  P->>L: asks for the rule types (Rule) [P1.2]
  L->>T: reads each type, its sentence, and the Steps it suits (Rule) [P1.2]
  P->>L: asks for the Steps, without what Lane laid before (Step) [P1.1]
  loop until the layer takes the Proposal [P2.1]
    P->>L: the Rules and Routes that the Steps mean (Proposal) [P1.1]
    L->>T: checks each Rule, and makes its sentence (Rule) [P1.2]
    alt the Proposal can't stand [P2.1]
      L-->>P: what's wrong, which the proposer mends [P4.2]
    else a file of the plugin can't carry it [P2.1]
      L-->>P: what's wrong in the file [P4.2]
      P-->>U: what to fix in their plugin, and stops [P4.2]
    end
  end
  L-->>P: each Step as it'll read, the Routes, and the Proposal's ID (Proposal) [P2.1]
  P->>U: shows them, and asks for yes or a change [P2.1]
  alt a change [P1.1]
    U->>P: the change [P1.1]
    P->>ST: writes it into its Step, and proposes again (Step) [P1.1]
  else yes [P2.1]
    U->>P: yes [P2.1]
    P->>L: lays the Proposal of the ID (Proposal) [P2.1]
    alt no such Proposal, or the Steps changed since it was shown [P2.1]
      L-->>P: refused, with why, and the proposer proposes again [P4.2]
    else [P2.1]
      L->>ST: replaces what Lane laid with each Rule's sentence, its check, and the Routes (Rule, Route) [P2.2]
      L->>ST: copies the guard, the rule types, and the reporters into the plugin [P6.2]
      L->>CC: checks the plugin [S1]
      alt the check fails [P2.2]
        L->>ST: puts back each file it changed [P2.2]
        L-->>P: what failed [P4.2]
      else [S1]
        L-->>P: each file written [S1]
        P-->>U: what Lane wrote, and to reload the plugin [S1]
      end
    end
  end
  Note over U,RR: Later, the user runs their plugin.
  U->>M: the plugin's command [S1]
  M->>G: calls the skill [P6.1]
  G->>RR: adds the Run, as S2 draws where one stopped (Run) [P5.1]
  loop until the Routes start no more [S1]
    opt the plugin gives a start's text of its own [P6.2]
      G->>A: asks for the text of each start due, with each Start that runs (Start) [P6.2]
      alt it gives none, as no work waits for that start [S1]
        A-->>G: why, which the guard gives in place of that start [S1]
      else it fails [P4.2]
        A-->>G: why, which the guard gives with who fixes it [P4.2]
      end
    end
    G-->>M: the starts and resumes due, each with its text (Start) [P4.1]
    alt the main conversation starts or resumes a subagent [P4.1]
      M->>G: the start (Start) [P4.1]
      alt a start due [P4.1]
        G->>RR: adds the Start (Start) [P5.1]
      else any other start of the plugin's roles [P4.1]
        G-->>M: stops it, with the starts due [P4.2]
      end
    else the main conversation ends its turn [S1]
      M->>G: the end [S1]
      alt a start is due [P4.1]
        G-->>M: stops it, with the starts due [P4.2]
      else a Rule of the skill holds the end to the plugin's check [S1]
        G->>A: runs the check, with the Result filled in [S1]
        A-->>G: whether it passes [S1]
      end
    else the person types a command that a Route waits for or goes after [S1]
      U->>M: the command [S1]
      M->>G: the command, as typed [S1]
      G->>RR: adds it, so that the Route's starts are due (Run) [S1]
    end
    loop each move of the subagent [S1]
      SA->>G: a move [S1]
      G->>T: checks it by each Rule of its role (Rule) [S1]
      alt it breaks a Rule [S1]
        G-->>SA: stops it, with the Step's sentence and what it may do (Step) [P4.2]
      else a Read of a file that a Rule asks read whole [P3.2]
        G->>RR: adds the Read (Read) [P5.1]
      else a run of the reporter of a Step or an Item done [P3.2]
        opt a Rule of the Step keeps a checklist [P6.2]
          G->>A: asks for the Step's Items, with the Start's values (Item) [P6.2]
        end
        alt the Step isn't due, or it lacks a Read or an Item that its Rules ask [P3.2]
          G-->>SA: stops it, with the Rule's sentence and what the Step lacks [P4.2]
        else [P3.2]
          SA->>R: reports the Mark (Mark) [P3.2]
          G->>RR: adds the Mark, once the report ran (Mark) [P5.1]
        end
      end
    end
    SA->>R: reports its Result (Result) [P3.1]
    R->>RR: reads, by the guard's code, which Results the role may give (Run) [P5.1]
    alt a Result its role may give [P3.1]
      G->>RR: adds the Result, once the report ran (Result) [P5.1]
    else [P3.1]
      R-->>SA: refuses it, with the Results it may give [P4.2]
    end
    SA->>G: ends [S1]
    alt no Result, or a Step left unmarked [P3.1]
      G-->>SA: stops the end, with the Rule's sentence [P4.2]
    else a Rule holds the end to the plugin's check [S1]
      G->>A: runs the check, with the Start's values and the Result filled in [S1]
      A-->>G: whether it passes, and the guard stops the end with the Rule's sentence where it fails [P4.2]
    end
    G-->>M: the Result, and the starts that its Route makes due (Route) [P3.1]
  end
  M->>R: reports the skill's Result (Result) [P3.1]
  R->>RR: reads, by the guard's code, which Results the skill may give (Run) [P5.1]
  G->>RR: adds it, which ends the Run (Run) [P5.1]
```

Strategies:

- A start judged by the Routes, and any other start stopped with the starts due. [P4.1]\
  Intent: the skill notices at once a start it forgot, or one out of order.
- A typed command that a Route goes after, its starts due in place of those before. [S1]\
  Intent: the person's pause or approval changes the order.
- A Mark checked for the Step due, then for the reads and the Items that its Rules ask. [P3.2]\
  Intent: a skipped step, item, or part of a file shows at the step skipped.
- A role's end checked for its Result first, then its Steps, then the plugin's own check. [P4.2]\
  Intent: a stop names the step left, as the plugin's check runs once the Result and each Step
  hold.

#### S2: a run picked up

```mermaid
sequenceDiagram
  actor U as user
  participant M as the plugin's main conversation
  participant G as guard
  participant RR as run record
  participant A as the plugin's adapter
  U->>M: the plugin's command, after the conversation is compacted or in a new one [S2]
  M->>G: calls the skill, with the words typed after the command [S2]
  alt the run record holds the Run, not ended [P5.1]
    G->>RR: reads where the Run stands (Run) [P5.1]
  else the plugin names an adapter of the results it keeps [P5.1]
    G->>A: asks for the Kept results, with those words (Kept results) [P5.1]
    alt results that follow the Routes [S2]
      G->>RR: adds the Run, with each Result (Run, Result) [P5.1]
    else none, or results that reach a Route that starts no more [S2]
      G->>RR: adds a new Run (Run) [P5.1]
    else results that don't follow the Routes, or it fails [P4.2]
      G-->>M: stops the command, with why and who fixes it, for the user [P4.2]
    end
  else [S2]
    G->>RR: adds a new Run (Run) [P5.1]
  end
  G-->>M: where the Run picks up, and the starts due (Start) [S2]
```

Strategies:

- A Run placed by the run record first, then by the plugin's Kept results. [P5.1]\
  Intent: a run goes on in the same conversation and in a new one.

### Deployment

![Lane's deployment](images/deployment.svg)

The user installs Lane by [the README](../../plugins/lane/README.md#installation) and lays it by
`/lane:up`, and the reloaded plugin runs the guard.

Strategies:

- Lane's code copied into the user's plugin. [P6.2]\
  Intent: whoever runs the plugin needs no Lane, and the guard runs the code that Lane's tests ran.
- Lane's code on Python 3.9 and its standard library alone. [P6.2]\
  Intent: the guard, started anew on each move, answers fast on each machine that runs the plugin.
- The plugin's adapters and checks run in the folder that the conversation works in. [S1]\
  Intent: each reads the run's checkout, in a worktree too.

### Directory structure

```text
plugins/lane/                     what Claude Code installs for the user
├── skills/up/SKILL.md            /lane:up
├── domain/up.md                  the proposer
├── domain/lay/                   the layer's code
├── scripts/lay.py                runs the layer
├── hooks/lane/                   Lane's code, copied whole into each plugin
│   ├── hook.py                   the guard
│   ├── result.py                 the reporter of a Result
│   ├── step.py                   the reporter of a Step done
│   ├── item.py                   the reporter of an Item done
│   └── domain/                   the guard's code, and lanes/, the rule types
└── README.md                     for Lane's users

dev/lane/                         what only Lane's developers use
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, from unit to integration

dev/tests/                        what the developers of Lane and rn share for their tests
├── claude_code.py                the double of Claude Code
└── recorded/                     the records of Claude Code that the double gives from

<the user's plugin>/              what Lane writes into, beside the user's own
├── skills/, agents/              the Steps, with the Rules' sentences
└── hooks/
    ├── hooks.json                the guard's entries, beside the user's own
    ├── lanes.json                the Rules, the Routes, and what Lane laid
    ├── lane/                     the copy of Lane's code
    └── adapters/                 each adapter, the user's own

<system temporary folder>/        what Lane keeps only for a run
├── lane/<yyyymmdd>-<plugin>/     each Proposal, by its ID
└── <plugin>/<yyyymmdd>-<id>/     the run record of one conversation
```

Strategies:

- In the user's plugin, only the sentences in the steps and the files under `hooks/` written by
  Lane. [P2.2]\
  Intent: every other part of the plugin stays the user's.
- The rule types inside `hooks/lane/`, which the layer imports. [P1.2]\
  Intent: the sentence that the user reads and the check that the guard runs come from one copy.

## Test strategy

| Check | Test target | Kind | Exit criteria or measure |
|---|---|---|---|
| Lint | Parts | Quality | 0 findings. |
| Static analysis | Parts | Quality | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | Every case passes. |
| Unit testing | Parts that hold a prompt | Benchmark | The proposer's Proposal for each case's steps, each case's results over runs added until one more changes no case's count. |
| Code coverage | Parts | Quality | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | 0 counterexamples in reading Steps and Proposals, each rule type's check, and the guard's placing of moves. |
| Mutation testing | Parts | Quality | 0 surviving mutants. |
| Integration testing | Architecture | Quality | Every case passes, each handoff giving the data the data model names. |
| Integration testing | Architecture | Benchmark | KR1.1: the share of the guard's answers that the cases hold right. |
| Contract testing | Architecture | Quality | On each new Claude Code, each recorded state gives the double's events. |
| Traceability | Architecture | Quality | Every element tested, every case naming one level up, and each principle's case failing broken. |
| Configuration testing | Product | Quality | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | Claude Code's strict check of each laid plugin passes. |
| Performance testing | Architecture | Benchmark | KR1.2: each move's time to the guard's answer. |
