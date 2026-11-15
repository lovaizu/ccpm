# Lane

Lane is a Claude Code plugin that keeps your plugin's skill and subagents on the steps and order you
wrote.

In development: the rebuild of Lane isn't released, and so far it holds subagents to their steps
and order.

Lane is for you when you build a Claude Code plugin whose skill and subagents must keep numbered
steps. With it, your plugin runs as you designed it, and you write no check.

## Non-goals

- Lane doesn't check work you do yourself in the conversation: it checks only a run of your plugin's
  skill.
- Lane isn't a security boundary: hold what must never happen with branch protection or Claude
  Code's permission rules.
- Lane doesn't judge a step's work: add a review subagent to your order, or end a step on your
  check.

## Requirements

- Claude Code 2.1.322 or later, where you build and run your plugin: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- A plugin that Claude Code takes as valid: `claude plugin validate <folder>` shows
  `✔ Validation passed`.
- The skill's and each subagent's steps as a numbered list under `## Steps`:
  `grep -rl '^## Steps' <folder>` shows each file.
- Each subagent's file setting `background: true`: `grep -L 'background: true' <folder>/agents/*`
  shows none.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

`claude plugin details lane@ccpm` then shows `lane 0.1.0`, with the skill `up` and six hooks.

## Walkthrough

At the end, Lane has held each step and each start of your plugin's first run.

Your plugin `changelog`, loaded by `claude --plugin-dir changelog` in the repository of `tally`, has
these files:

```markdown
<!-- changelog/skills/write/SKILL.md -->
---
name: write
description: Has the CHANGELOG.md entries written and reviewed.
---

## Steps

1. Have the entries written and reviewed.
```

```markdown
<!-- changelog/agents/writer.md -->
---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
background: true
---

## Steps

1. Read `CHANGELOG.md` to learn its last version and its form.
2. Read the commits since then with `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`.
4. Reply with the entries you wrote.
```

```markdown
<!-- changelog/agents/reviewer.md -->
---
name: reviewer
description: Reviews the CHANGELOG.md entries that writer wrote.
background: true
---

## Steps

1. Read the new entries in `CHANGELOG.md` against the commits they name.
2. Give `more` when an entry needs the writer again, and `good` when every entry is right.
```

You type:

```text
/lane:up changelog
```

Lane shows:

```text
Routes of write, laid on its step 1:
  first             start writer
  writer `written`  start reviewer
  reviewer `more`   start writer
  reviewer `good`   start no more

1. Have the entries written and reviewed. Start each subagent you are told to start, until you are told to start no more. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py write good`.

Lanes of writer, each checked only in writer:
  step 2  run:   Run only `git log --oneline`.  type run_only
  step 3  write: Write only `CHANGELOG.md`.     type write_only
  step 4  end:   End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`.
  commands: writer may run only `git log --oneline` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`

2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.
4. Reply with the entries you wrote. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`.

Lanes of reviewer, each checked only in reviewer:
  step 2  end: End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.

2. Give `more` when an entry needs the writer again, and `good` when every entry is right. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.

ID: b9fd8fd8
Reply yes to lay these into changelog, or say what to change.
```

You type:

```text
yes
```

Lane shows:

```text
Wrote step 1 of write into skills/write/SKILL.md.
Wrote steps 2, 3 and 4 of writer into agents/writer.md.
Wrote step 2 of reviewer into agents/reviewer.md.
Wrote the checks of write, writer and reviewer into hooks/hooks.json.
Wrote the lanes laid and the routes into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Type /reload-plugins, and the checks hold from your next prompt.
```

You type:

```text
/reload-plugins
```

You type:

```text
/changelog:write
```

Lane shows:

```text
changelog: Start `changelog:writer` with `Carry out your steps`.
```

When `writer` runs `git -C /home/you/tally log --oneline`, Lane shows:

```text
changelog: Run only `git log --oneline`.
The commands you may run, each word for word: `git log --oneline`, `python3 /home/you/tally/changelog/hooks/lane/result.py writer written`.
```

When `writer` gives `written`, Lane shows:

```text
changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`.
```

When `reviewer` tries to end without running its result script, Lane shows:

```text
changelog: End by running `python3 /home/you/tally/changelog/hooks/lane/result.py reviewer more` or `python3 /home/you/tally/changelog/hooks/lane/result.py reviewer good`.
```

When `reviewer` gives `more`, Lane shows:

```text
changelog: reviewer gave `more`. Start `changelog:writer` with `Carry out your steps`.
```

When `writer` gives `written` again, and the main conversation stops to ask you, Lane shows:

```text
Stop hook feedback:
changelog: Start `changelog:reviewer` with `Carry out your steps`.
```

When `reviewer` gives `good`, Lane shows:

```text
changelog: reviewer gave `good`. Start no more subagents.
```

## How it works

Lane holds your plugin's skill and subagents to the steps and order you wrote, on every run.

![How Lane works, from your steps to each run it holds](images/how-it-works.svg)

### "A hook that only refuses leaves the subagent to find another way."

When Lane stops a call, the subagent gets its own step's sentence, so it goes back to the step.

### "The next move comes from what a subagent wrote."

A result counts only from a run of the result script that Lane lays on the last step. A reply such
as "No more entries" never passes for `more`.

### "The skill forgets a start, starts the wrong one, or stops while one is due."

Lane gives the main conversation each start your routes make due, and stops any other. It holds the
main conversation's stop while a start is due.

### "Each check is code to write and test."

Lane proposes the rules and routes from your steps, shown as your steps read once laid. You approve
them, and Lane lays each rule's sentence and its check from one type.

### "A run that stops starts over."

Lane decides each move from a record of the run's starts and results, so a run goes on after
`/compact`. In a new conversation, it goes on from the results your plugin keeps, through an adapter.

### "Does it check other work in the same conversation?"

No. A run starts at a call of your skill and ends once a route starts no more.

### "Does whoever runs the plugin need Lane?"

No. `/lane:up` puts the checks into your plugin, and after an update of Lane brings them to the new
version.

## Documentation

- [Steps, routes, and adapters](docs/steps-routes-adapters.md): for you when your plugin's steps go
  beyond the walkthrough's, such as a subagent's own text.
- [Changelog](CHANGELOG.md): for you when you update Lane, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
