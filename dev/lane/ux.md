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
- O2: The developer AI has its orchestrator, the subagent that starts the others, start them in the
  order of its flow, the order the developer AI sets, on every run, with no script of its own for
  the order.
  - KR2.1: Of the plugin's runs, the share that goes wrong: the subagents are not started in the
    order of the flow, or the orchestrator is stopped on a call the flow allows. Lower is better.
  - KR2.2: The lead time from the developer AI's first flow for a plugin to the first run that keeps
    it. Shorter is better.

In each objective, the first key result comes first: the second is shortened only by a change
that keeps the first.

Key results have no target values. When a measure becomes a target, it stops being a good measure
(Goodhart's law). Use the key results to judge how close the objective is.

## Scenarios

Both scenarios run on `changelog`, the developer AI's plugin that writes a project's
`CHANGELOG.md`. The participants:

- developer AI (AI): builds `changelog`, and runs it itself to try it.
- `lay.py` (script): Lane's script that the developer AI runs.
- check script (script): the script that `lay.py` puts into `changelog`.
- `lead` (AI): the orchestrator of `changelog`.
- `writer` (AI): the subagent of `changelog` that writes the new entries into `CHANGELOG.md`.
- `reviewer` (AI): the subagent of `changelog` that compares the entries with the commits.

No step waits for a person.

### O1: The developer AI holds writer to two rules of its step

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant W as writer (AI)
  A->>L: lay.py print, with two rules for step 3 of writer:<br>write only CHANGELOG.md, and do not run git commit or git push
  L-->>A: step 3 as it will be, ending<br>"Write only `CHANGELOG.md`. Do not run `git commit` or `git push`."
  A->>L: lay.py write, once it approves what print showed
  L-->>A: step 3 written with the sentences,<br>and the check script put into changelog
  A->>W: asks changelog for an entry and a commit, and changelog starts writer
  W->>K: writes CHANGELOG.md
  K-->>W: lets it through
  W-->>A: ends with CHANGELOG.md written and no commit,<br>keeping both rules of step 3
```

### O2: The developer AI has lead start writer and reviewer in its flow's order

```mermaid
sequenceDiagram
  participant A as developer AI (AI)
  participant L as lay.py (script)
  participant K as check script (script)
  participant O as lead (AI)
  participant W as writer (AI)
  participant R as reviewer (AI)
  A->>L: lay.py print, with the flow on step 1 of lead:<br>writer, then reviewer, back to writer while reviewer answers `more`
  L-->>A: the flow in order, and step 1 of lead ending<br>"Take each move lane tells you, until it tells none."
  A->>L: lay.py write, once it approves what print showed
  L-->>A: step 1 written with the sentence,<br>and the check script put into changelog
  A->>O: asks changelog to update CHANGELOG.md for the next release,<br>and changelog starts lead
  K-->>O: "changelog: The next move of the flow is move 1: start `changelog:writer`."
  loop until reviewer ends without `more`
    O->>W: starts writer
    W-->>O: ends with the entries it wrote
    K-->>O: "changelog: The next move of the flow is move 2: start `changelog:reviewer`."
    O->>R: starts reviewer
    R-->>O: ends with what it found, and `more` on a line of its own<br>while an entry needs writer again
    alt reviewer answered `more`
      K-->>O: "changelog: reviewer answered `more`. The next move of the flow is move 1: start `changelog:writer`."
    else reviewer ended without `more`
      K-->>O: "changelog: The flow is done: lane tells no more moves."
    end
  end
  O-->>A: ends with the reviewed entries
```
