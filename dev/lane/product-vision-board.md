# Lane Product Vision Board

Lane's user is the developer AI, an AI that builds a Claude Code plugin whose subagents work in
numbered steps.

## OKRs

- O1: The developer AI has its plugin's subagents keep the rules of their steps on every run,
  without writing checks.
  - A rule is a sentence in a step that the subagent must keep, such as "Run only
    `git log --oneline`."
  - KR1.1: Of the subagents' tool calls and their ends of work that a rule is about, the share
    that goes wrong. Lower is better. A call or an end goes wrong in four ways:
    - it breaks a rule, and goes through;
    - it breaks a rule, is stopped, and is then done another way;
    - the rules allow it, and it is stopped;
    - Lane cannot hold the rule, so the developer AI writes a check of its own or leaves the rule
      unchecked.
  - KR1.2: The lead time from the developer AI's first rule for a plugin to the first run whose
    subagents keep the rules. Shorter is better.
- O2: The developer AI has its plugin's subagents started in the order it set, on every run,
  without writing code for the order.
  - KR2.1: Of the plugin's runs, the share that goes wrong. Lower is better. A run goes wrong in
    four ways:
    - a subagent starts that the order does not name;
    - a start that the order names is stopped;
    - the subagent that starts the others ends while the order names a subagent to start next;
    - Lane cannot hold the order, so the developer AI writes code for it.
  - KR2.2: The lead time from the developer AI's first order for a plugin to the first run that
    keeps it. Shorter is better.

In each objective, the first key result comes first. A change shortens the lead time only if it
keeps the first key result as good.

Key results have no target values. A measure that becomes a target stops being a good measure
(Goodhart's law), so the key results serve only to judge how close the objective is.

## Scenarios

Both scenarios run on `changelog`, a plugin that the developer AI builds to write a project's
`CHANGELOG.md`. The participants:

- **developer AI** (AI): builds `changelog`, and runs it to try it.
- **Lane** (plugin): takes the developer AI's rules and order, and holds the subagents to them.
- **`lead`** (AI): the subagent of `changelog` that starts the others.
- **`writer`** (AI): the subagent of `changelog` that writes the new entries into `CHANGELOG.md`.
- **`reviewer`** (AI): the subagent of `changelog` that compares the entries with the commits.

No step waits for a person. Each subagent runs in the background, so the developer AI's
conversation stays free while it runs.

### O1: The developer AI holds writer to two rules

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as Lane (plugin)
  participant W as writer (AI)
  A->>L: two rules for writer's steps
  L-->>A: the steps as they will read
  A->>L: approves them
  L-->>A: the steps written
  A->>W: starts writer
  loop each tool call of writer
    W->>L: a tool call
    L-->>W: lets it through, or stops it with the sentence of its step
  end
  W-->>A: ends, both rules kept
```

### O2: The developer AI has lead start writer and reviewer in its order

The order the developer AI sets is its routes. A route names the subagent that `lead` starts next
after another one ends with a given result, a word such as `more`.

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as Lane (plugin)
  participant O as lead (AI)
  participant W as writer (AI)
  participant R as reviewer (AI)
  A->>L: the routes
  L-->>A: the routes and the steps as they will read
  A->>L: approves them
  L-->>A: the steps written
  A->>O: starts lead
  loop until reviewer ends with good
    O->>W: starts writer, as the routes say
    W-->>O: ends with written
    O->>R: starts reviewer, as the routes say
    R-->>O: ends with more or good
  end
  O-->>A: ends with the reviewed entries
```
