# Lane architecture

## User stories

- S1: a plugin wants its AI to notice when it writes a file that its step doesn't name.
- S2: a plugin wants its AI to notice when it reads a file that its step says never to read.
- S3: a plugin wants its AI to notice ending a step before reading whole a file the step names.
- S4: a plugin wants its AI to notice when it runs a command other than those its step names.
- S5: a plugin wants its AI to notice when it skips a step, or ends with a step undone.
- S6: a plugin wants its AI to notice when it ends a step with an item of its checklist undone.
- S7: a plugin wants its run to move on by the result its AI gives, never by its reply.
- S8: a plugin wants its AI to notice when it ends a step that the plugin's own check doesn't pass.
- S9: a plugin wants its main conversation to start only the subagents due, ending no turn while one
  is due.
- S10: a plugin wants a stopped run to go on where it stopped, after `/compact` or in a new
  conversation.
- S11: a plugin wants its main conversation to take, at each turn, the steps of that turn's event.
- S12: a plugin wants its AI to go back to an earlier step and take each step from there again.

## Solution strategy

### Principles

Lane gives an AI that leaves its plugin's step the step's own sentence, so that it notices at once.

- P1: the AI notices each step it leaves
  - P1.1: a stopped call gets its step's sentence and what to do; an unchecked call goes on,
    saying why.
  - P1.2: a step, item, read, or result counts only from the AI's own call, never its reply.
- P2: one way for any plugin, applied by adapters alone
  - P2.1: each thing Lane can make an AI notice is one rule type, which a plugin's author picks.
  - P2.2: Lane defines what it takes in and gives out, holds every check, and names no plugin.
  - P2.3: a plugin gives its steps and order in a file where fixed, and by adapters where decided
    later.
  - P2.4: the plugin's order says which subagents start when, and Lane holds the AI to it.
  - P2.5: Lane checks only runs of a plugin that gives it rules, and leaves other work alone.

### Concept model

![Lane's concepts](images/concept-model.svg)

- Rules\
  What a plugin gives Lane: each step's rules, fixed or given per start or turn, and any routes.
- Route\
  A fixed order: the roles to start after a role's result, or after a command of the plugin.
- Run\
  One run of a plugin's skill in a conversation, from its call until its order ends it. It holds
  each command, turn, start with its prompt, read, mark, and result.
- Starts due\
  What the plugin's order gives for a run: each role to start now and how many, or the run's end.

Strategies:

- The starts due asked of the plugin's order at each move, with the run as it stands. [P2.4]\
  Intent: Lane holds the AI to an order that the plugin fixes or decides as it runs, without
  deciding it.
- Each start kept with its prompt, which the plugin's adapters are given. [P2.3]\
  Intent: the plugin tells its starts of one role apart by what it wrote for each.
- A step's rules given at each start and resume by the plugin's adapter, where its file fixes none.
  [P2.3]\
  Intent: a role is held to its deliverable's rules, as they stand once an answer changes them.
- The main conversation's steps given at each turn by the plugin's adapter, where the file gives
  none. [S11]\
  Intent: a main conversation that answers each event in its own turn starts each turn's steps
  afresh.
- Each earlier turn's role and prompt given with a turn. [S11]\
  Intent: a turn's event can rest on the turn before it, such as an answer to its question.
- A checklist's items given by the plugin's command at the mark, where the step's work decides
  them. [S6]\
  Intent: a checklist holds the items that the step's own work brings, such as each part a change
  reaches.
- A run's end given by the plugin's order, not by the run having no start due. [S9]\
  Intent: a run that waits, such as for the person's answer, goes on.
- A run with no order held to its skill's steps alone, ending at the turn's end they let through.
  [P2.5]\
  Intent: a skill with steps and no subagents takes Lane with its rules alone.
- A run's record that only grows, holding only what no later move gives again. [S10]\
  Intent: moves checked at the same moment lose nothing of one another's.
- A run's record kept for its conversation alone, a run in a new conversation going on from the
  plugin's files. [S10]\
  Intent: what a run has done past its conversation lies only where the plugin keeps it.

### Components

![Lane's components](images/components.svg)

- guard (hook)\
  Holds each move of a run to its plugin's rules and to the starts due.
- rule types (module)\
  Make each rule's check and the sentence it gives one, so that what the AI reads is what holds.
- reporters (command)\
  Carry each step, item, result, or step gone back to, to the guard as the AI's own call.
- route adapter (module)\
  Gives the starts due of a plugin that fixes its order, from its routes.

Strategies:

- The plugin's folder found from its skill's base directory in the conversation, as
  [Claude Code's states](claude-code-states.md#where-the-guard-finds-the-plugin-it-serves) say.
  [P2.2]\
  Intent: Lane serves a plugin that it never names, as Claude Code gives the folder either way.
- The plugin's adapter of the starts due, run on its own, else Lane's route adapter inside the
  guard. [P2.3]\
  Intent: a fixed order needs no code of the plugin's, and a decided one gives only its answer.
- The reporters as commands that Claude Code puts on the AI's path. [P1.2]\
  Intent: a plugin's step names a reporter without knowing where Lane lies.
- A folder named in a rule of the paths that a role writes letting through each file under it.
  [S1]\
  Intent: a deliverable of several files, such as code with its tests, is written whole.
- Each move placed on its run and start by what Claude Code's events carry, as
  [its states](claude-code-states.md) list. [P2.5]\
  Intent: each move is held to the rules of its own start, and to no other run's.
- Each rule type judging its own call, mark, or end, and the guard stopping a breach with its
  sentence. [P2.1, S2, S3, S4, S6]\
  Intent: the check and the sentence that the AI reads change together, in the rule type's own
  module.
- A result that a step's rules name as ending the start, letting the start end at that step.
  [S5, S7]\
  Intent: a role that can't go on, such as on the person's point, ends with its result.
- A step gone back to undoing its marks and those of each later step. [S12]\
  Intent: a role whose later step shows an earlier one short mends it there, skipping no step.
- A mark checked for the steps before its step, then for the reads and items its step's rules
  ask. [S5]\
  Intent: a skipped step, item, or part of a file shows at the step skipped.
- An end checked for its result, its steps, the plugin's check, and, for a turn, the starts due.
  [S5, S8, S9]\
  Intent: a stop names the step left, as the plugin's check runs once the result and each step
  hold.

### Sequences

#### S9: starts held to the plugin's order

```mermaid
sequenceDiagram
  actor U as person
  participant M as the plugin's main conversation
  participant G as guard
  participant O as the plugin's order
  participant A as the plugin's adapter of the rules
  participant RR as run record
  U->>M: the plugin's command [S9]
  M->>G: calls the skill [P2.5]
  G->>RR: adds the run, as S10 draws where one stands (Run) [S9]
  loop until the order says the run ends [S9]
    G->>O: asks for the starts due, with the run (Run) [P2.4]
    O-->>G: each role to start now, and how many (Starts due) [P2.4]
    alt a start of a role due [S9]
      M->>G: the start, with its prompt [S9]
      G->>RR: adds the start with its prompt (Run) [S9]
      opt the plugin gives an adapter of the rules [P2.3]
        G->>A: asks for the start's rules, with its prompt, at the start and at each resume (Rules) [P2.3]
      end
    else any other start of the plugin's subagents [S9]
      G-->>M: stops it, with the starts due [P1.1]
    else the main conversation ends its turn while a start is due [S9]
      G-->>M: stops it, with the starts due [P1.1]
    else a result, or a command of the plugin, typed or called by the Skill tool [S7]
      G->>RR: adds it (Run) [S7]
    end
  end
```

#### S11: steps given at each turn

```mermaid
sequenceDiagram
  actor U as person
  participant M as the plugin's main conversation
  participant G as guard
  participant A as the plugin's adapter of the rules
  participant RR as run record
  U->>M: a prompt, or a subagent's end that reaches it [S11]
  M->>G: the turn's first move [S11]
  G->>A: asks for the turn's steps, with the run and the turn's prompt (Run) [S11]
  G->>RR: adds the turn, with its steps (Run) [S11]
  loop each call and mark of the turn [S11]
    M->>G: the call or the mark [S11]
    alt it breaks a rule of the step at hand [P1.1]
      G-->>M: stops it, with the step's sentence [P1.1]
    end
  end
  M->>G: ends the turn [S11]
  alt a step of the turn isn't done [S5]
    G-->>M: stops it, with the step's sentence [P1.1]
  end
```

#### S10: a run picked up

```mermaid
sequenceDiagram
  actor U as person
  participant M as the plugin's main conversation
  participant G as guard
  participant O as the plugin's order
  participant RR as run record
  U->>M: the plugin's command, after /compact or in a new conversation [S10]
  M->>G: calls the skill, with the words typed after the command [S10]
  alt the run record holds the run, not ended [S10]
    G->>RR: reads where the run stands (Run) [S10]
  else
    G->>RR: adds the run, with those words (Run) [S10]
  end
  G->>O: asks for the starts due, with the run (Run) [P2.4]
  O-->>G: each role to start now, from where the plugin's own files say the run stands (Starts due) [S10]
```

### Deployment

![Lane's deployment](images/deployment.svg)

A plugin names `lane` among its `plugin.json` dependencies, so that Claude Code installs Lane beside
it.

Strategies:

- Lane's code on Python 3.9 and its standard library alone. [P2.2]\
  Intent: the guard, started anew on each move, answers fast on each machine that runs a plugin.
- The plugin's adapters and checks run in the folder that the conversation works in. [P2.3]\
  Intent: each reads the run's checkout, in a worktree too.

### Directory structure

```text
plugins/lane/                     what Claude Code installs beside each plugin that depends on it
├── hooks/
│   ├── hooks.json                the guard's entries
│   └── lane/                     the guard, the route adapter, and rule_types/
├── bin/                          the reporters
├── docs/rules-and-adapters.md    what Lane takes in and gives out
└── README.md                     for a plugin's author

dev/lane/                         what only Lane's developers use
├── claude-code-states.md         each state of Claude Code that the guard meets, with its records
└── tests/                        the test cases, from unit to integration

<a plugin>/lane/                  what a plugin gives Lane
├── rules.json                    the rules, and the routes of a fixed order
└── adapters/                     each adapter: the starts due of an order decided as it runs, and
                                  the rules of each start
```

## Test strategy

| Check | Test target | Kind | When | Exit criteria or measure |
|---|---|---|---|---|
| Lint | Parts | Quality | During the work | 0 findings. |
| Static analysis | Parts | Quality | During the work | 0 findings of mismatched types, copied code, or import cycles. |
| Complexity analysis | Parts | Quality | During the work | Per function, McCabe 10, cognitive 15, 6 returns, 12 branches, 5 arguments, 50 statements at most. |
| Unit testing | Parts | Quality | During the work | Every case passes. |
| Code coverage | Parts | Quality | During the work | 100% statement (C0) and branch (C1) coverage. |
| Property-based testing | Parts | Quality | During the work | 0 counterexamples in reading the rules, each rule type's check, and the guard's placing of moves. |
| Integration testing | Architecture | Quality | During the work | Every case passes, each handoff giving the data the concept model names. |
| Contract testing | Architecture | Quality | Apart from the work | On each new Claude Code, each recorded state gives the double's events. |
| Traceability | Architecture | Quality | During the work | Every element tested, every case naming one level up, and each principle's case failing with its part broken. |
| Configuration testing | Product | Quality | During the work | Every case passes on Python 3.9 and on the newest Python. |
| Conformance and compliance testing | Product | Quality | During the work | Claude Code's strict check of Lane's plugin passes. |
