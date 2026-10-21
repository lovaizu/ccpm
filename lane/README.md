# lane

An AI told a step clearly still drifts from it on some runs, so lane lays a lane where a step alone
is not sure to hold: a sentence of the step together with a hook that notices a drift from it and
tells the AI the sentence again. lane is a Claude Code plugin for you if you write the steps of a skill or
an agent: once you have written them, `/lane:up` asks you what it needs, proposes the lanes to lay,
and on your OK writes both the steps and the hooks.

## Example

You have made a skill, `/notes:write`, that writes a project's changelog. One of its steps says:

```markdown
3. Write the new entries into `CHANGELOG.md`.
```

Having written the steps, you type `/lane:up`. lane asks, one point at a time, what it needs: first
which steps to lay lanes on, offering the skills and agents just written, then what the files do
not settle about them:

```
Which steps shall I lay lanes on? skills/write/SKILL.md was just changed.
```

```
Step 3 writes `CHANGELOG.md`. Is it the only file the skill writes, and who commits it?
```

You answer that it is the only one, and that you commit it yourself after reading it. Once every
point is settled, lane proposes the lanes to lay where a step alone is not sure to hold, each under
the action it keeps: begin, read, write, run, test, hand on, wait or end; with the step as it would
read and the hooks that keep it:

```
Lanes on step 3:
  write: Write only the OUT, `CHANGELOG.md`.
  run:   Do not commit the OUT.

3. Write the new entries into `CHANGELOG.md`, and no other file. Do not commit it.

skills/write/SKILL.md: write_only and hands_off (git commit, git push)
```

You say OK, and lane writes both into `skills/write/SKILL.md`, the step and its hooks, with lane's
code in `hooks/lane/`. Then, when the AI running `/notes:write` runs `git commit -m notes`, Claude
Code does not run it, and the AI reads:

```
notes: Do not commit the OUT.
```

It ends with the changelog written and uncommitted, as its step says.

## Why lane

lane gives a step's hooks what a hook written on its own does not.

- Each hook tells the step's own sentence, not only a refusal.

  A hook that only refuses leaves the AI to find another way to what it was doing, such as an AI
  refused a commit splitting the word `git` to get past the check. Told the step's way, the AI goes
  back to the step.
- You answer and approve, and write no check.

  Each lane's check is written and tested once, in lane, so the steps take no misreadings of a
  command of their own.
- Lanes are laid only where a step alone is not sure to hold, and a check reads the forms the steps
  tell and the AI writes, not every way the shell has.

  The hooks stay few and small. What must hold whatever the AI writes is held where it holds, such
  as GitHub's branch protection, Claude Code's sandbox or its permission rules, as Claude Code's own
  docs say a check on the command text is not a security boundary.

## Requirements

- Python 3.9 or later, run as `python3`, on the machines the steps run on.

  Without it, the hooks stop the tool calls they watch and ask for Python to be installed.

## Installation

```console
claude plugin install lane@ccpm
```

Then, once a skill's or an agent's steps are written, type `/lane:up`, as in the example.

lane puts its code where the steps are, once for all of them: `<plugin>/hooks/lane/` for a plugin,
`.claude/hooks/lane/` for a project and `~/.claude/hooks/lane/` for you alone. It writes a step's
hooks into the step's own file, or, for an agent of a plugin, which Claude Code reads no hooks
from, into the plugin's `hooks/hooks.json`. In a plugin of the ccpm marketplace the code is a link
to lane's; anywhere else it is a copy with its version, which `/lane:up` brings to its own version
the next time it is run there.

## Documentation

- [The lanes](lanes.md) give each lane lane can lay, under its action, and what its hook notices.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../dev/lane/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../LICENSE)
