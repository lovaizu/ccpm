# Lane UX

Lane's user is the developer AI, an AI that builds a Claude Code plugin whose subagents work in
numbered steps.

## OKRs

- O1: The developer AI has its plugin's subagents keep the rules of their steps on every run,
  without writing checks.
  - A rule is a sentence in a step that the subagent must keep, such as "Run only
    `git log --oneline`."
  - KR1.1: Of the subagents' tool calls and ends of their work, the share that goes wrong. A call
    goes wrong when it breaks a rule and goes through, when it breaks a rule, is stopped and is
    then done another way, or when the rules allow it and it is stopped. Lower is better.
  - KR1.2: The lead time from the developer AI's first rule for a plugin to the first run whose
    subagents keep the rules. Shorter is better.
- O2: The developer AI has its plugin's subagents started in the order it set, on every run,
  without writing code for the order.
  - KR2.1: Of the plugin's runs, the share that goes wrong. A run goes wrong when a subagent starts
    that the order does not name, or when a start that the order names is stopped. Lower is better.
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
- **`lay.py`** (script): Lane's script, which the developer AI runs.
- **check script** (script): a script that `lay.py` puts into `changelog`. It checks each call of
  the subagents, and tells `lead` each next start.
- **result script** (script): a script that `lay.py` puts into `changelog`. A subagent runs it to
  end with its result, a word such as `more`.
- **`lead`** (AI): the subagent of `changelog` that starts the others.
- **`writer`** (AI): the subagent of `changelog` that writes the new entries into `CHANGELOG.md`.
- **`reviewer`** (AI): the subagent of `changelog` that compares the entries with the commits.

No step waits for a person. Each subagent runs in the background, so the developer AI's
conversation stays free while it runs.

### O1: The developer AI holds writer to two rules

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant W as writer (AI)
  A->>L: lay.py print, with two rules for writer:<br>on step 2, run only git log --oneline;<br>on step 3, write only CHANGELOG.md
  L-->>A: steps 2 and 3 as they will read, ending<br>"Run only `git log --oneline`." and "Write only `CHANGELOG.md`."
  A->>L: lay.py write, once it approves what print showed
  L-->>A: steps 2 and 3 written,<br>and the check script put into changelog
  A->>W: starts writer in the background, for the entry of one commit
  W->>K: runs git log --oneline
  K-->>W: lets it through
  W->>K: writes CHANGELOG.md
  K-->>W: lets it through
  W-->>A: ends with CHANGELOG.md written and no commit,<br>both rules kept
```

### O2: The developer AI has lead start writer and reviewer in its order

The order the developer AI sets is its routes. A route names the subagent that `lead` starts next
after another one ends with a given result.

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant S as result script (script)
  participant O as lead (AI)
  participant W as writer (AI)
  participant R as reviewer (AI)
  A->>L: lay.py print, with the routes: lead starts writer first;<br>writer's `written` leads to reviewer;<br>reviewer's `more` leads back to writer, and its `good` to the end
  L-->>A: the routes, and the steps of lead, writer and reviewer as they will read
  A->>L: lay.py write, once it approves what print showed
  L-->>A: the steps written,<br>and the check script and the result script put into changelog
  A->>O: starts lead in the background, to update CHANGELOG.md for the next release
  K-->>O: "changelog: Start `changelog:writer`."
  loop until reviewer ends with `good`
    O->>W: starts writer in the background
    K-->>O: "changelog: Wait for `changelog:writer` to end: you are told the next start once it has."
    W->>S: runs the result script with `written`
    W-->>O: ends with the entries it wrote
    K-->>O: "changelog: writer gave `written`. Start `changelog:reviewer`."
    O->>R: starts reviewer in the background
    R->>S: runs the result script with `more` while an entry needs writer again,<br>or with `good`
    R-->>O: ends with what it found
    alt reviewer gave `more`
      K-->>O: "changelog: reviewer gave `more`. Start `changelog:writer`."
    else reviewer gave `good`
      K-->>O: "changelog: reviewer gave `good`. Start no more subagents."
    end
  end
  O-->>A: ends with the reviewed entries
```
