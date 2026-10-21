# lane

An AI told a step clearly still drifts from it on some runs, so lane has each step made together
with its hook: the step tells the AI the way, and the hook notices a drift from it and tells the AI
the way again. lane is for whoever builds a Claude Code plugin in the ccpm marketplace whose AI
works through steps, and keeps that AI to its steps through a run no one watches.

## Example

turn's generator makes a work that the AI calling turn checks and then keeps in git. Its step says
so:

```markdown
4. Make the work at the paths in `work` ... Leave it uncommitted: the calling AI checks it and keeps
   it in git.
```

An AI told a step clearly still drifts from it on some runs, such as committing what it just made.
So the step is made with its check, `turn/hooks/checks/no_commit.py`, which reads the command with
lane's `shell.git` and finds a commit or a push in the repository the run works in:

```python
for folder, said in shell.git(event["tool_input"]["command"], cwd):
    if said and said[0] in ("commit", "push") and shell.inside(folder, cwd):
        return ["leave the work uncommitted; the caller checks it and keeps it in git"]
return []
```

turn's hook entry runs each check with lane's `hook.run`. When the generator runs
`cd "$repo" && git commit -m work`, Claude Code does not run it, and the generator reads:

```
turn: leave the work uncommitted; the caller checks it and keeps it in git
```

It goes on to its next step with the work uncommitted, as its step says.

## Why lane

lane gives a plugin's hooks what a hook written on its own does not.

- Each hook is made with its step and tells the step's right way.

  A hook that only refuses leaves the AI to find another way to what it was doing; turn's generator,
  refused a commit, split the word `git` to get past the check. Told the step's way, the AI goes
  back to the step.
- A check reads the forms the steps tell and the AI writes, not every way the shell has.

  The check stays small and is finished. What must hold whatever the AI writes is held where it
  holds, such as GitHub's branch protection, Claude Code's sandbox or its permission rules, as
  Claude Code's own docs say a check on the command text is not a security boundary.
- The ways worth keeping are written once, each with what it is for and how it is done, and the code
  every plugin needs, such as reading the event and a command, is written and tested once.

## Requirements

- A plugin in the ccpm marketplace.

  A plugin takes lane's files by symbolic links, which Claude Code copies into the plugin at install
  only from within the same marketplace.
- Python 3.9 or later, run as `python3`, on the machines the plugin runs on.

  Without it, the plugin's hooks stop the tool calls they check and ask for Python to be installed.

## Installation

lane is not installed on its own, as it has no hooks of its own. From your plugin's `hooks` folder,
link lane's files:

```console
ln -s ../../lane/hooks/hook.py hook.py
ln -s ../../lane/hooks/shell.py shell.py
```

Then, for each step, write its check in `hooks/checks/<name>.py`, list it in the entry of its hook
event, and name the step's right way in what the check returns, as in the example.

## Documentation

- [The patterns](patterns.md) give each way of pairing a step with its hook: what it is for, how it
  is done, and a check that does it.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../dev/lane/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../LICENSE)
