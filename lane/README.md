# lane

lane lets an AI notice when it drifts from the steps your plugin gives it, and tells it the right
way, so it finds its way back at full speed with no one watching each move. A lane is laid on a
step the AI may drift from, a step being one numbered item of what a subagent, an AI your plugin
starts for one job, is told to do. The lane is a sentence of the step together with a hook that notices a
drift from it and tells the AI the sentence again.

lane is a Claude Code plugin for you if you have an AI build your plugin, one whose work an AI does
in several steps. While building it, your AI calls lane, answers its points from what it knows of
your plugin and approves the lanes itself; lane asks you nothing. lane lays the lanes on your plugin's
subagents, and on every run lane's code lets each subagent notice its drift and tells it the step
again.

## Example

In your plugin `notes`, the skill `/notes:changelog` makes the conversation it is typed in the
orchestrator, the AI that holds the run and decides each move. The orchestrator starts a subagent,
`changelog-writer`, that writes a project's changelog. One of its steps says:

```markdown
3. Write the new entries into `CHANGELOG.md`.
```

While building `notes`, your AI starts lane's subagent `lane:up`, which reads the plugin's skills
and subagents. It sends your AI, all in one reply, each point they do not settle and each fact it found
that its proposal rests on, and your AI answers them from what it knows of your plugin:

```
Step 3 of changelog-writer writes `CHANGELOG.md`. Is it the only file it writes, and who commits it?
```

Your AI answers that it is the only one, and that the orchestrator commits it once you have read it
and said OK. Once every point is settled, `lane:up` proposes the lanes on the steps that alone are
not sure to hold, each under the action it watches: begin, read, write, run, test, hand on, follow,
wait or end; with its hook, and the step as it would read:

```
Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  write: Write only `CHANGELOG.md`.              hook write_only
  run:   Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`. Do not run `git commit` or `git push`.
```

Your AI approves them. `lane:up` writes the step into `agents/changelog-writer.md`, the lanes into
`hooks/lanes.json` and the hooks into `hooks/hooks.json`, and puts lane's code, which runs the
hooks, in `hooks/lane/`.

Then you run `/notes:changelog`. When `changelog-writer` runs `git commit -m notes`, Claude Code
does not run it, and the subagent reads:

```
notes: Do not run `git commit` or `git push`.
```

The run goes on as its steps say, and ends with the changelog committed once you have said OK.

## Why lane

lane gives a plugin's run what steps and hooks written on their own do not.

- A refusal leads the AI back to its step, not only away from what it tried.

  A hook that only refuses leaves the AI to find another way to what it was doing, such as an AI
  refused a commit splitting the word `git` to get past the check. Told the step's own sentence, the
  AI goes back to the step.
- Each check is written and tested once, in lane.

  Your plugin takes no misreadings of a command of its own.
- Lanes are laid only where a step alone is not sure to hold, and a check reads the forms the steps
  tell and the AI writes, not every way the shell has.

  The hooks stay few and small. What must hold whatever the AI writes is held where it holds, such
  as GitHub's branch protection, Claude Code's sandbox or its permission rules, as Claude Code's own
  docs say a check on the command text is not a security boundary.
- Each lane acts only in its subagent.

  Claude Code reads no hooks from a plugin subagent's own file, so lane writes them into the
  plugin's `hooks/hooks.json`, each naming its subagent. A hook written into a skill instead goes on
  running for the rest of the session once the skill has started, and is not told which skill runs,
  so it acts on work outside the skill too. So lane lays lanes on subagents alone, and a step to
  keep goes into a subagent the skill starts.

## Requirements

- Claude Code, where your plugin runs and lane is installed.
- Python 3.9 or later, run as `python3`, on the machines the plugin runs on.

  Without it, the hooks stop the tool calls they watch, each asking for Python to be installed.

## Installation

lane comes from ccpm, a marketplace of Claude Code plugins on GitHub. Add it, then install lane:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

Then, as in the example, your AI calls `lane:up` while it builds your plugin, from your
conversation or from a subagent it started.

lane's code in your plugin's `hooks/lane/` is a copy with its version, which `lane:up` brings to its
own version the next time it is run there.

## Documentation

- [The lanes](docs/lanes.md) lists each lane lane can lay, the sentence it writes into a step and
  when its hook tells it.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../dev/lane/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../LICENSE)
