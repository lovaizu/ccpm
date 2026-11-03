# Lane UX

Lane's user is the developer AI, an AI that builds Claude Code plugins.

## OKRs

- O1: The developer AI has its subagents keep the rules of their steps, the sentences they must
  keep, on every run, with no check code of its own.
  - KR1.1: Of the subagents' tool calls and ends of their work, the share that goes wrong: a break
    of a rule that goes through, a break that is stopped and then done another way, or a call the
    rules allow that is stopped. Lower is better.
  - KR1.2: The lead time from the developer AI's first rule for a plugin to the first run in which
    its subagents keep the rules. Shorter is better.
- O2: The developer AI has its orchestrator, the subagent that starts the others, start them as its
  routes say on every run, with no script of its own for the order. A route, which the developer AI
  sets, names the subagent to start next after another one ends with a given result, a word such
  as `more`.
  - KR2.1: Of the plugin's runs, the share that goes wrong: a subagent is started that the routes do
    not name, or the orchestrator is stopped on a start the routes name. Lower is better.
  - KR2.2: The lead time from the developer AI's first routes for a plugin to the first run that
    keeps them. Shorter is better.

In each objective, the first key result comes first: the second is shortened only by a change
that keeps the first.

Key results have no target values. When a measure becomes a target, it stops being a good measure
(Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

Both scenarios run on `changelog`, the developer AI's plugin that writes a project's
`CHANGELOG.md`. The participants:

- developer AI (AI): builds `changelog`, and runs it itself to try it.
- `lay.py` (script): Lane's script that the developer AI runs.
- check script (script): the script that `lay.py` puts into `changelog` to check its subagents.
- result script (script): the script that `lay.py` puts into `changelog`, which a subagent runs to
  end with its result.
- `lead` (AI): the orchestrator of `changelog`.
- `writer` (AI): the subagent of `changelog` that writes the new entries into `CHANGELOG.md`.
- `reviewer` (AI): the subagent of `changelog` that compares the entries with the commits.

No step waits for a person.

Each subagent runs in the background, so the developer AI's conversation stays free while it runs.

### O1: The developer AI holds writer to two rules

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant W as writer (AI)
  A->>L: lay.py print, with two rules for writer:<br>run only git log --oneline on step 2, and write only CHANGELOG.md on step 3
  L-->>A: steps 2 and 3 as they will be, ending<br>"Run only `git log --oneline`." and "Write only `CHANGELOG.md`."
  A->>L: lay.py write, once it approves what print showed
  L-->>A: steps 2 and 3 written with the sentences,<br>and the check script put into changelog
  A->>W: asks changelog for an entry and a commit,<br>and changelog starts writer in the background
  W->>K: runs git log --oneline
  K-->>W: lets it through
  W->>K: writes CHANGELOG.md
  K-->>W: lets it through
  W-->>A: ends with CHANGELOG.md written and no commit,<br>keeping both rules
```

### O2: The developer AI has lead start writer and reviewer as its routes say

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant S as result script (script)
  participant O as lead (AI)
  participant W as writer (AI)
  participant R as reviewer (AI)
  A->>L: lay.py print, with the routes: lead starts writer first,<br>writer's `written` leads to reviewer,<br>reviewer's `more` leads back to writer, and its `good` to the end
  L-->>A: the routes, and the steps of lead, writer and reviewer<br>as they will be with their sentences
  A->>L: lay.py write, once it approves what print showed
  L-->>A: the steps written with the sentences,<br>and the check script and the result script put into changelog
  A->>O: asks changelog to update CHANGELOG.md for the next release,<br>and changelog starts lead in the background
  K-->>O: "changelog: Start `changelog:writer`."
  loop until reviewer ends with `good`
    O->>W: starts writer in the background
    K-->>O: "changelog: Wait for `changelog:writer` to end: you are told the next start once it has."
    W->>S: runs the result script with `written`
    W-->>O: ends with the entries it wrote, and Claude Code starts lead again to tell it
    K-->>O: "changelog: writer gave `written`. Start `changelog:reviewer`."
    O->>R: starts reviewer in the background
    R->>S: runs the result script with `more` while an entry needs writer again,<br>or with `good`
    R-->>O: ends with what it found, and Claude Code starts lead again to tell it
    alt reviewer gave `more`
      K-->>O: "changelog: reviewer gave `more`. Start `changelog:writer`."
    else reviewer gave `good`
      K-->>O: "changelog: reviewer gave `good`. Start no more subagents."
    end
  end
  O-->>A: ends with the reviewed entries
```
