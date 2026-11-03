# Lane

Lane is a Claude Code plugin that checks the subagents of your plugin, so that they keep the rules
of their steps and start one another in the order that you set.

Lane is for you, an AI that builds a Claude Code plugin whose subagents work in numbered steps. With
Lane, your subagents keep the rules of their steps on every run. Your orchestrator, the subagent
that starts the others, starts them in your order, which you write as a flow. You write no code for
the checks and no script for the order.

A rule is a sentence in a step, such as ``Do not run `git commit` or `git push`.``, with a check of
it. When a subagent breaks the rule, the check stops the tool call and shows the subagent the same
sentence, headed by your plugin's name. A hook that only refuses a call leaves the subagent to look
for another way. A subagent that sees the sentence of its own step goes back to the step.

**Non-goals**

- Lane checks only subagents that have rules. It does not check the main conversation or a skill,
  so the orchestrator of a flow must be a subagent.
- Lane is not a security boundary. Block what must never happen, such as a merge, with the branch
  protection of GitHub or the permission rules of Claude Code.
- Lane sees tool calls and ends of work, not what a subagent thinks. "Compare each option" cannot
  have a rule.
- Lane does not read every form of a shell command. It stops a command that names a file in a way
  it cannot follow, such as `$d/out.csv`, and asks for the plain path.
- Lane does not choose the next subagent from a run's results. A flow is a fixed order that goes
  back only on an answer you name, such as `more`.
- Lane reads the texts your plugin writes, such as a list of items to answer, in one format only.
  For another format, you write an adapter, a Python script that turns your format into Lane's, as
  [The lanes](docs/lanes.md#the-ports) says.

## Requirements

- Claude Code 2.1.309 or later, where you build your plugin and where it runs.
- Python 3.9 or later, run as `python3`, on the same computers. Without it, each tool call that a
  rule is about is stopped, and the subagent and whoever runs your plugin are told to install Python.
- A plugin that passes `claude plugin validate`, whose subagents have their steps as a numbered
  list under `## Steps`.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

`claude plugin list --json` then shows `lane@ccpm` with its `installPath`. Each version installs in
a new folder, so read `installPath` again after an update. Lane is ready when `lay.py` shows its
usage:

```console
$ python3 <installPath>/scripts/lay.py
usage: lay.py print <proposal>
       lay.py write <proposal>
       lay.py up <plugin>
```

After an update, run `lay.py up <your plugin's folder>`. It puts Lane's new checks into your
plugin and lists the rules your plugin has.

## Walkthrough

At the end, a subagent of your plugin keeps two rules of its step on a run, with no code of yours.

The plugin `changelog` writes a project's `CHANGELOG.md`, and lives in the folder `changelog/` of
a git repository. It has two files. `changelog/.claude-plugin/plugin.json` names it:

```json
{"name": "changelog", "description": "Writes a project's CHANGELOG.md.", "version": "0.1.0"}
```

`changelog/agents/writer.md` is its subagent `writer`, whose step 3 writes the entries:

```markdown
---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
---

## Steps

1. Read `CHANGELOG.md` to learn its last version and its form.
2. Read the commits since then with `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`.
4. Reply with the entries you wrote.
```

`writer` must write no other file and must not commit. You write these two rules in a proposal,
the JSON file `.lane/20261102-changelog/changelog.json` at the root of that repository:

```json
{"plugin": "changelog",
 "subagents": [{"name": "writer", "steps": [{"step": 3, "lanes": [
  {"lane": "write_only", "takes": ["CHANGELOG.md"]},
  {"lane": "hands_off", "takes": ["git commit", "git push"]}]}]}]}
```

`lane` names the type of each rule, and `takes` its values. Lane's output and documents call a
rule a lane, and its check a hook. You run `lay.py print` at the root of the repository, and it
shows the step as it will be:

```console
$ python3 <installPath>/scripts/lay.py print .lane/20261102-changelog/changelog.json
Lanes on step 3 of writer, each hook acting in writer alone:
  write: Write only `CHANGELOG.md`.              hook write_only
  run:   Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`. Do not run `git commit` or `git push`.
```

Once you approve it, `lay.py write` writes it into the plugin:

```console
$ python3 <installPath>/scripts/lay.py write .lane/20261102-changelog/changelog.json
Wrote step 3 of writer into agents/writer.md.
Wrote the hooks of writer into hooks/hooks.json.
Wrote the lanes laid into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Removed the proposal .lane/20261102-changelog/changelog.json.
Removed its folder <the repository>/.lane/20261102-changelog.
```

Step 3 in `changelog/agents/writer.md` now reads as `lay.py print` showed it.

The rest of this walkthrough is not yet from a real run: no run of `changelog` in Claude Code is
recorded. You start Claude Code at the root of the repository with `claude --plugin-dir changelog`,
and ask for an entry and a commit. Claude Code starts `writer`. `writer` writes
`CHANGELOG.md`, and the check lets the write through. `writer` reads the new sentences in step 3,
and ends with `CHANGELOG.md` written and no commit made.

A flow is laid the same way, from the proposal's `flow`, as [The flow](docs/flow.md) says.

## How it works

![How Lane works](images/how-it-works.svg)

Lane puts its checks into your plugin as one script, the check script, in `hooks/lane/`. It runs
from there, so whoever runs your plugin does not need Lane.

## Documentation

- [The lanes](docs/lanes.md): each type of rule, its sentence and what it stops; the proposal;
  adapters; and a subagent whose steps lie in another file.
- [The flow](docs/flow.md): how to write a flow, and what the orchestrator is told.
- [The changelog](CHANGELOG.md): the changes in each version.

## Development

[Lane's development folder](../../dev/lane/README.md) holds its UX, its architecture and its tests.

## License

[MIT License](../../LICENSE)
