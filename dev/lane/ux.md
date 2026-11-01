# lane UX

## OKRs

- O1: The developer AI, an AI that builds a Claude Code plugin, wants the subagents of its plugin to
  keep the rules written in their numbered steps on every run, without writing the code that checks
  them.
  - KR1.1: The share of tool calls and ends of work that break a rule and still go through. Lower is
    better.
  - KR1.2: The share of tool calls and ends of work that the rules allow but that are stopped. Lower
    is better.
  - KR1.3: The share of stopped breaks after which the subagent still does not keep the rule, for
    example because it tries another way. Lower is better.
  - KR1.4: The lines of code that the developer AI writes by hand so that its subagents keep the
    rules. Fewer is better.
  - KR1.5: The time from the developer AI's first rule to the first run in which the subagents keep
    the rules. Shorter is better.
- O2: The developer AI wants the orchestrator of its plugin, the subagent that starts the others, to
  start them in the order that the developer AI set, its flow, on every run, without writing a
  script for it.
  - KR2.1: The share of runs in which the orchestrator leaves the flow. Lower is better.
  - KR2.2: The share of the orchestrator's tool calls and ends of work that the flow allows but that
    are stopped. Lower is better.
  - KR2.3: The lines of code that the developer AI writes by hand so that the orchestrator keeps the
    flow. Fewer is better.
  - KR2.4: The time from the developer AI's first flow to the first run that keeps it. Shorter is
    better.

Key results have no target values. When a measure becomes a target, it stops being a good measure
(Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

The developer AI is an AI. `lay.py` of the lane plugin is a script, and so is the check script that
`lay.py` puts into the developer AI's plugin. The operator runs that plugin, and is a person or an
AI. The example plugin `changelog` has three subagents, each an AI. `lead` is the orchestrator, and
the check script tells it each move, the next subagent to start. `writer` writes new entries into
`CHANGELOG.md`. `reviewer` compares the entries with the commits.

### O1: A rule on writer's step stops a commit

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant U as operator (person or AI)
  participant W as writer (AI)
  A->>L: lay.py print: two rules for step 3 of writer,<br>write only CHANGELOG.md, do not run git commit or git push
  L-->>A: step 3 with the sentence of each rule
  A->>L: lay.py write, once it approves what print showed
  L-->>A: writes the sentences into step 3,<br>puts the check script into changelog
  U->>W: runs changelog, asking for an entry and a commit
  W->>K: writes CHANGELOG.md
  K-->>W: lets it through
  W->>K: runs git commit
  K-->>W: stops it: "changelog: Do not run `git commit` or `git push`."
  W-->>U: ends with CHANGELOG.md written and no commit
```

### O2: The orchestrator starts writer and reviewer by the flow

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant U as operator (person or AI)
  participant O as lead (AI)
  participant W as writer (AI)
  participant R as reviewer (AI)
  A->>L: lay.py print: the flow writer, reviewer,<br>back to writer when reviewer answers `more`
  L-->>A: the flow, and its sentence on step 1 of lead
  A->>L: lay.py write
  L-->>A: writes the sentence into step 1,<br>puts the check script into changelog
  U->>O: runs changelog
  K-->>O: "changelog: The next move of the flow is move 1: start `changelog:writer`."
  O->>W: starts writer
  W-->>O: ends with the entries
  O->>K: tries to end its work
  K-->>O: stops it: "changelog: Take each move lane tells you, until it tells none.<br>The next move of the flow is move 2: start `changelog:reviewer`."
  O->>R: starts reviewer
  R-->>O: ends with `more` on a line by itself
  K-->>O: "changelog: reviewer answered `more`. The next move of the flow is move 1: start `changelog:writer`."
  Note over O,R: writer and reviewer again, until reviewer does not answer `more`
  K-->>O: "changelog: The flow is done: lane tells no more moves."
  O-->>U: ends with the reviewed entries
```
