# Lane

Lane is a Claude Code plugin that holds the skill and the subagents of the plugin you build to the
steps you wrote and the order you set, on every run.

Lane 0.1.0 is still in development and not yet released. The walkthrough below shows what Lane sets
out to do. It isn't the output of a recorded run yet.

Lane is for you when you build a Claude Code plugin whose skill and subagents work in numbered
steps, and some step must hold on every run. With it, your plugin runs as you designed it, and you
write no check and no code for the order.

## Non-goals

- Lane doesn't check the work you do yourself in the same conversation. It checks only a run of
  your plugin's skill.
- Lane isn't a security boundary. Hold what must never happen, such as a merge, with GitHub's
  branch protection or Claude Code's permission rules.
- Lane doesn't judge the work or a subagent's thoughts. It checks only the tool calls and how a
  subagent ends.

## Requirements

- Claude Code 2.1.319 or later, where you build your plugin and where it runs: `claude --version`
  shows it.
- Python 3.9 or later, run as `python3`, on the same computers: `python3 --version` shows it.
- A plugin that Claude Code takes as valid: `claude plugin validate <your plugin's folder>` passes.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

`claude plugin list --json` then shows `lane@ccpm` with its `installPath`. Lane is ready when
`lay.py` shows its usage:

```console
$ python3 <installPath>/scripts/lay.py
usage: lay.py print <proposal>
       lay.py write <proposal>
       lay.py up <plugin>
```

## Walkthrough

At the end, your plugin `changelog` has run once with its subagent held to two rules and its
subagents started in the order you set. You wrote no check or code for it.

`changelog` writes a project's `CHANGELOG.md`, and lives in the folder `changelog/` of a git
repository. Its skill `write`, in `changelog/skills/write/SKILL.md`, starts the subagents:

```markdown
---
name: write
description: Has the CHANGELOG.md entries written and reviewed.
---

## Steps

1. Have the entries written and reviewed.
```

Its subagent `writer`, in `changelog/agents/writer.md`, writes the entries:

```markdown
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

Its subagent `reviewer`, in `changelog/agents/reviewer.md`, also sets `background: true`. Its last
step says ``Give `more` when an entry needs the writer again, and `good` when every entry is
right.``

`writer` must run no command but `git log --oneline`, so it can't commit, and must write no file
but `CHANGELOG.md`. You write these two rules and the routes in a proposal, the JSON file
`.lane/20261106-changelog/changelog.json` at the root of the repository. Lane's files and output
call a rule a lane:

```json
{"plugin": "changelog",
 "subagents": [{"name": "writer", "steps": [
  {"step": 2, "lanes": [{"lane": "run_only", "takes": ["git log --oneline"]}]},
  {"step": 3, "lanes": [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]}]}],
 "routes": {"orchestrator": "write", "step": 1, "routes": [
  {"from": "write", "to": "writer"},
  {"from": "writer", "on": "written", "to": "reviewer"},
  {"from": "reviewer", "on": "more", "to": "writer"},
  {"from": "reviewer", "on": "good"}]}}
```

`lane` names the type of each rule, and `takes` its values. `orchestrator` names the skill that
starts the subagents, and `step` the step of it that Lane lays the routes on. At the root of the
repository, `lay.py print` shows the routes and the rules, and the steps as they read once laid:

```console
$ python3 <installPath>/scripts/lay.py print .lane/20261106-changelog/changelog.json
Routes of write, laid on its step 1:
  first             start writer
  writer `written`  start reviewer
  reviewer `more`   start writer
  reviewer `good`   start no more

1. Have the entries written and reviewed. Start each subagent you are told to start, until you are told to start no more. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py write good`. ...

Lanes of writer, each checked only in writer:
  step 2  run:   Run only `git log --oneline`.  type run_only
  step 3  write: Write only `CHANGELOG.md`.     type write_only
  step 4  end:   End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`. ...
  commands: writer may run only `git log --oneline` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`

2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.
4. Reply with the entries you wrote. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`. ...
...
```

The `commands` line lists each command that `writer` may run, as it has a run_only rule. The check
stops any other. Where a step names in backticks a command that its subagent may not run,
`lay.py print` says so beside that step's number.

Once you approve it, `lay.py write` writes it into the plugin:

```console
$ python3 <installPath>/scripts/lay.py write .lane/20261106-changelog/changelog.json
Wrote steps 2, 3 and 4 of writer into agents/writer.md.
Wrote step 1 of write into skills/write/SKILL.md.
Wrote step 2 of reviewer into agents/reviewer.md.
Wrote the checks of writer, write and reviewer into hooks/hooks.json.
Wrote the lanes laid and the routes into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Removed the proposal .lane/20261106-changelog/changelog.json.
Removed its folder <the repository>/.lane/20261106-changelog.
```

You start Claude Code at the root of the repository with `claude --plugin-dir changelog`, and
type:

```text
/changelog:write
```

The run of `write` starts, and Lane says to the main conversation:

```text
changelog: Start `changelog:writer`.
```

The main conversation starts `writer` in the background. `writer` runs `git log --oneline` and
writes `CHANGELOG.md`, and Lane lets both through. `writer` then tries to run `git commit`. Lane
stops that call and shows `writer` the sentence of its step 2, and on the next line the commands
it may run:

```text
changelog: Run only `git log --oneline`.
The commands you may run, each word for word: `git log --oneline`, `python3 <changelog's folder>/hooks/lane/result.py writer written`.
```

`writer` goes back to its steps and makes no commit. It ends by running the command its step 4
now names, which gives the result `written`. As its end reaches the main conversation, Lane adds
beside it:

```text
changelog: writer gave `written`. Start `changelog:reviewer`.
```

`reviewer` finds an entry to write again and gives `more`. Lane says to the main conversation:

```text
changelog: reviewer gave `more`. Start `changelog:writer`.
```

`writer` writes the entry again, and `reviewer` then gives `good`. Lane says to the main
conversation:

```text
changelog: reviewer gave `good`. Start no more subagents.
```

The run ends there, with `CHANGELOG.md` written and reviewed. What you ask next in the same
conversation is your own work, and Lane checks none of it.

## How it works

Lane holds your plugin's skill and subagents to the steps and the order you wrote, by checks it lays
into your plugin from them.

![How Lane works: you approve your rules and routes, lay.py lays the checks into your plugin, and on a run the guard gives the main conversation only the start due, gives a subagent that leaves its steps the step's own sentence, counts a result only from the result script, and picks a run up from what your plugin kept](images/how-it-works.svg)

### "A hook that only refuses leaves the subagent to find another way."

When Lane stops a call, the subagent gets the sentence of its own step, so it goes back to the step
instead of seeking another way.

### "The next move comes from what a subagent wrote."

A result counts only from a run of the result script, which Lane lays on the subagent's last step,
so a reply such as "No more entries" never passes for `more`.

### "The skill forgets a start, or starts the wrong one."

Lane gives the main conversation each start due by your routes, and stops any other. A start goes
with only the text your plugin gives it, and a route can wait until the person types the command
you name, such as an approval.

### "Each check is code to write and test."

You see your steps as they'll read with their rules, and approve them. Lane makes each rule's
sentence and its check from one type, and lays both into your plugin.

### "A run that stops starts over."

Where your plugin keeps the results of a run, Lane reads them at the next call of its skill, and holds
the run on from there, even in a new conversation.

### "Does it check other work in the same conversation?"

No. A run starts at a call of your skill and ends once a route starts no more. Lane checks nothing
outside it.

### "Does whoever runs the plugin need Lane?"

No. `lay.py write` puts the checks into your plugin, and they run from there. After an update of
Lane, `lay.py up` brings them to the new version.

## Documentation

- [The lanes](docs/lanes.md): for you as you write rules: each type of rule with its sentence and
  what it stops, and the proposal.
- [The routes](docs/routes.md): for you as you write routes: how to write them, and what the skill
  gets.
- [Changelog](CHANGELOG.md): the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](../../LICENSE)
