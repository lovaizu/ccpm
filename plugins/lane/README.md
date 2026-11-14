# Lane

Lane is a Claude Code plugin that keeps the skill and the subagents of your own plugin on the steps
you wrote for them, in the order you set, on every run.

Lane is a work in progress: version 0.1.0 isn't released yet. If you install it today, its main use
works as the walkthrough's recorded run shows. An adapter, a program of yours that gives Lane what
your plugin keeps in a form of its own, has passed only Lane's tests: no recorded run shows one yet.

Lane is for you when you build a Claude Code plugin whose skill and subagents work in numbered
steps, and some step must hold on every run. With it, your plugin runs as you designed it, and you
write no check and no code for the order.

## Non-goals

- Lane doesn't check the work you do yourself in the same conversation. It checks only a run of
  your plugin's skill.
- Lane isn't a security boundary. Hold what must never happen, such as a merge, with GitHub's
  branch protection or Claude Code's permission rules.
- Lane doesn't judge whether the work of a step is good, such as whether a changelog entry reads
  well. It checks only the tool calls and how a subagent ends. To judge the work, put a review
  subagent in your order, and Lane holds that subagent to its steps too. Or have a step end only
  once a command of your own gives 0, such as a check of a record that the subagent keeps. Lane
  then runs it as the subagent ends, or as your skill ends its turn, with `{result}` in it standing
  for the result given, and holds the end until it gives 0.

## Requirements

- Claude Code 2.1.322 or later, where you build your plugin and where it runs: `claude --version`
  shows it.
- Python 3.9 or later, run as `python3`, on the same computers: `python3 --version` shows it.
- A plugin that Claude Code takes as valid: `claude plugin validate <your plugin's folder>` ends
  with `✔ Validation passed`.
- In your plugin, the steps of the skill and of each subagent as a numbered list under `## Steps`,
  in its own file or in a file of your plugin that its body names by `${CLAUDE_PLUGIN_ROOT}/`, and
  each subagent's file setting `background: true`, as in the walkthrough. The skill's steps may
  lie in both, and in the `SKILL.md` of each command that a route waits for or goes after, such
  as an approval, and Lane holds them all as the steps of one conversation. Such a command's
  `SKILL.md` sets `disable-model-invocation: true`, so that only the person runs it.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

`claude plugin details lane@ccpm` then shows `lane 0.1.0`, with the skill `up` and six hooks:

```text
Component inventory
  Skills (1)  up
  Agents (0)
  Hooks (6)  UserPromptExpansion, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStop  (harness-only — no model context cost)
```

## Walkthrough

At the end, your plugin `changelog` has written the `CHANGELOG.md` entries of a project, and its
reviewer has passed them. On each run, Lane held each subagent to the rules you approved and started
the subagents in the order you set. You typed `/lane:up changelog`, `yes`, `/reload-plugins`, and
`/changelog:write` to reach the first such run, in under five minutes, and wrote no check or code.

This is a recorded run of Lane 0.1.0 on Claude Code 2.1.322, except for `/reload-plugins` and
Lane's line that asks for it, which that run lacks. The walkthrough adds them because recorded runs
of Claude Code 2.1.323 and 2.1.325 show that a plugin's hooks written during a session hold only
after `/reload-plugins`. `<repo>` stands for the folder of the repository.

`changelog` writes a project's `CHANGELOG.md`, and lives in the folder `changelog/` of the git
repository of `tally`, a small Python tool, whose last version is 0.1.0. Its skill `write`, in
`changelog/skills/write/SKILL.md`, starts the subagents:

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

Its subagent `reviewer`, in `changelog/agents/reviewer.md`, reviews them:

```markdown
---
name: reviewer
description: Reviews the CHANGELOG.md entries that writer wrote.
background: true
---

## Steps

1. Read the new entries in `CHANGELOG.md` against the commits they name.
2. Give `more` when an entry needs the writer again, and `good` when every entry is right.
```

You want `writer` to run no command but `git log --oneline`, so it can't commit, and to write no
file but `CHANGELOG.md`. You started Claude Code at the root of the repository with
`claude --plugin-dir changelog`, so that it loads your plugin. Once you've built the plugin, you
type:

```text
/lane:up changelog
```

Lane reads the steps of `write`, `writer`, and `reviewer`, and proposes rules and an order from
them alone. From a step that runs a command, such as step 2 of `writer`, Lane proposes a rule to
run only that command, and from a step that writes a file, a rule to write only that file. The order
comes from the skill's step and from the results that the steps name, `more` and `good`. Where a
subagent's steps name no result, as those of `writer` don't, Lane names one, here `written`. Lane
shows each step as it'll read once laid. Its output calls a rule a lane, and the order its routes:

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

Lane ends each step that ends a role with a command of `result.py`, its result script, by which the
role gives its result, since Lane takes a result only from that script. The `commands` line lists
each command that `writer` may run, as it has a run_only rule. The check stops any other. The steps
of `reviewer` name no command, so Lane holds only how it ends, and says so beside the proposal.
Where a step names in backticks a command that its subagent may not run, Lane says so beside that
step's number.

You reply `yes`, and Lane lays them into the plugin:

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

In `hooks/hooks.json`, Lane adds its hook entries beside any of your own, and keeps yours
unchanged. When it lays again, it replaces only the entries it laid before.

Where a rule or a route isn't as you meant it, you say what to change, and Lane proposes again.
Where an AI builds the plugin, it reads the proposal and approves it in the same way, with no
person's reply.

Claude Code loads a plugin's hooks as a session starts, and during a session only once you type
`/reload-plugins`, so you type it:

```text
/reload-plugins
```

Claude Code lets no conversation reload its own plugins, so where an AI builds the plugin, it asks
whoever gives the conversation its prompts, you or a program of yours, to type `/reload-plugins`.

From the next prompt on, Lane's checks hold your plugin. In the same session, you type:

```text
/changelog:write
```

The run of `write` starts, and Lane adds to the main conversation:

```text
changelog: Start `changelog:writer` with `Carry out your steps`.
```

The main conversation starts `writer` in the background. `writer` reads `CHANGELOG.md`, and then
tries to run `git -C <repo> log --oneline`, which isn't word for word the command of its step 2.
Lane stops that call and shows `writer` the sentence of its step 2, and on the next line the
commands it may run:

```text
changelog: Run only `git log --oneline`.
The commands you may run, each word for word: `git log --oneline`, `python3 <repo>/changelog/hooks/lane/result.py writer written`.
```

`writer` runs `git log --oneline`, writes the entries into `CHANGELOG.md`, and ends by running the
command its step 4 now names, which gives the result `written`. As its end reaches the main
conversation, Lane adds beside it:

```text
changelog: writer gave `written`. Start `changelog:reviewer` with `Carry out your steps`.
```

`reviewer` runs `result.py` at the end of a longer command, which records no result, and tries to
end. Lane holds its end, and shows it the sentence of its last step:

```text
changelog: End by running `python3 <repo>/changelog/hooks/lane/result.py reviewer more` or `python3 <repo>/changelog/hooks/lane/result.py reviewer good`.
```

`reviewer` runs the command on its own, and gives `more`, as an entry for a change in what
`tally FILE` prints is missing. Lane adds:

```text
changelog: reviewer gave `more`. Start `changelog:writer` with `Carry out your steps`.
```

`writer` reads only the subjects of the commits, as `git log --oneline` gives them, finds nothing
to add, and gives `written` again. Lane names `reviewer` as the next start. The main conversation
expects the two to loop with no end, and stops to ask you what to do. Lane holds the stop, as a
start is due, and you see:

```text
Stop hook feedback:
changelog: Start `changelog:reviewer` with `Carry out your steps`.
```

The main conversation starts `reviewer`, which gives `good` this time. Lane says:

```text
changelog: reviewer gave `good`. Start no more subagents.
```

The main conversation runs the command its step 1 now names, which gives `write` the result `good`,
and the run ends there. Lane held each step of the run, yet the entries still lack the change: the
steps of `writer` let it read only the subjects of the commits, and those of `reviewer` name no way
to check an entry. Lane doesn't judge the entries, as [Non-goals](#non-goals) says, so you mend the
steps. Step 2 of `writer` now reads:

```markdown
2. Read the commits since then with `git log --oneline`, and then read each one with `git show {commit}`.
```

Step 1 of `reviewer` now reads:

```markdown
1. Read the new entries in `CHANGELOG.md` against the commits since its last version: list them with `git log --oneline`, and read each one with `git show {commit}`.
```

After you change the steps, you run `/lane:up changelog` again, and Lane proposes from the steps as
they now read, in place of what it laid before. Of what it shows, the lanes now read:

```text
Lanes of writer, each checked only in writer:
  step 2  run:   Run only `git log --oneline` or `git show {commit}`.  type run_only
  step 3  write: Write only `CHANGELOG.md`.                            type write_only
  step 4  end:   End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`.
  commands: writer may run only `git log --oneline` or `git show {commit}` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`

Lanes of reviewer, each checked only in reviewer:
  step 1  run: Run only `git log --oneline` or `git show {commit}`.  type run_only
  step 2  end: End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.
  commands: reviewer may run only `git log --oneline` or `git show {commit}` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`
```

You reply `yes`, and Lane lays them as before, with `Wrote steps 1 and 2 of reviewer into
agents/reviewer.md.` in place of its line on step 2.

You type `/reload-plugins`, and then `/changelog:write` again. By the same lines as before, Lane
starts `writer`, then `reviewer`, which gives `more` for the missing entry, then `writer`, which adds
it from the diff, then `reviewer`, which gives `good`. Lane stops six calls on the way, each a command not word for
word in the steps, such as
`git show d417d74 && git show 7a84e02 && git show 0192711 && git show 8aba605`, and each time the
subagent goes back to its step and runs each command as the step names it. The run ends with this
new section in `CHANGELOG.md`:

```markdown
## [Unreleased]

### Added

- `tally --lines FILE` prints the number of lines in FILE.
- `tally --chars FILE` prints the number of characters in FILE.
- `tally` reads standard input when no file is given.
- `tally FILE...` counts several files and prints their total.
- README.md documents `--lines`, `--chars`, standard input, the total line,
  and exit code 2.

### Changed

- `tally FILE` now prints the file's name after its count.

### Fixed

- Words split by tabs and newlines are now counted apart.
- On a file that can't be read, `tally` now says why and exits with 2.
```

What you ask next in the same conversation is your own work, and Lane checks none of it.

## How it works

Lane holds your plugin's skill and subagents to the steps and the order you wrote, by checks it lays
into your plugin from them.

![How Lane works: you approve the rules and routes that /lane:up proposes from your steps, and it lays the checks into your plugin, and on a run the guard gives the main conversation only the start due, gives a subagent that leaves its steps the step's own sentence, counts a result only from the result script, and picks a run up from what your plugin kept](images/how-it-works.svg)

### "A hook that only refuses leaves the subagent to find another way."

When Lane stops a call, the subagent gets the sentence of its own step, so it goes back to the step
instead of seeking another way.

### "The next move comes from what a subagent wrote."

A result counts only from a run of the result script, which Lane lays on the subagent's last step,
so a reply such as "No more entries" never passes for `more`. Lane holds the end of a subagent that
hasn't run the script, and shows it the sentence of its last step.

### "The skill forgets a start, starts the wrong one, or stops while one is due."

Lane gives the main conversation each start due by your routes, and stops any other, a subagent's
start of another among them. While a start is due and no subagent runs, Lane holds the main
conversation's stop. A start goes with Lane's text, `Carry out your steps`, and the words typed after
your command, which name no command for the subagent to run. So a subagent gets nothing of the talk
that started it, and reads what it needs by its steps. Where your plugin gives a subagent a text of
its own, put an adapter in your plugin's `hooks/adapters/`: an executable program that Lane runs in
the folder that the conversation works in, which is the root of your repository until the
conversation enters a worktree, with the subagent's name as its one argument, and that prints
`{"text": "<the text>"}`. `/lane:up` proposes each adapter it finds there, and the start goes with
that text in place of Lane's. Where your steps name a run value in braces, such as
`` Write only `{deliverable}`. ``, the adapter can give the subagent's values beside its text, as
`{"text": "<the text>", "values": {"deliverable": "<the value>"}}`. Lane then holds each name that
the values give to its value alone, so the subagent writes only the deliverable it was started for.
A name that they don't give stands for any value. Your skill's steps can start subagents side by
side, and Lane then lets a start through beside those that run where your adapter gives it a text
other than theirs, holds each subagent to the values of its own start, and keeps the moves after
each result due until your steps make them. Lane gives your adapter each start that runs on
stdin, as `{"running": [{"role": "<subagent>", "text": "<its text>", "values": {...}}, ...]}`,
so that it gives the text of work that none of them holds. A route can wait until the person who
uses your plugin types the command you name, such as an approval. A route can also go after a
command that they type at any moment, such as a pause: the route's moves are then due in place
of those due before, while each subagent that runs goes on, and its result moves the run by its
route. Where your skill's steps choose
the next move after a result by their own judgment, the route lists each move they choose among:
start a subagent, resume one by SendMessage, wait for the person's reply, or start no more by the
skill's own result. Lane lets through only those moves, and holds the main conversation's stop
unless one of them waits for the person.

### "Each check is code to write and test."

Lane proposes the rules and the routes from your steps. You see your steps as they'll read with
their rules, and approve them. Lane makes each rule's sentence and its check from one type, and
lays both into your plugin. Where a step already says a rule, as its sentence word for word, or by
naming the command of your own that checks how it ends, Lane adds the sentence there no more, so
the subagent reads each rule once, with the reason you give it.

### "A run that stops starts over."

Lane keeps each run's starts, calls, and results in a record in the system's temporary folder, and
decides each move from that record, not from the conversation. So a run goes on where it stopped
in the same conversation, even after `/compact`. A new conversation goes on from the results that
your plugin keeps, through your adapter of them in `hooks/adapters/`, which prints
`{"results": [{"role": "<subagent>", "result": "<result>"}, ...]}` in the order the run gave them.
Without one, a run in a new conversation starts over.

### "Does it check other work in the same conversation?"

No. A run starts at a call of your skill and ends once a route starts no more. Lane checks nothing
outside it.

### "Does whoever runs the plugin need Lane?"

No. `/lane:up` puts the checks into your plugin, and they run from there. After an update of
Lane, `/lane:up` brings them to the new version.

## Documentation

- [Changelog](CHANGELOG.md): for you when you update Lane, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): for you when you need help or find a fault,
  where you ask or report it.

## License

[MIT](LICENSE)
