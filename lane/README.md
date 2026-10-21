# lane

An AI told a step clearly still drifts from it on some runs, so lane has each step made together
with its hook: the step tells the AI the way, and the hook notices a drift from it and tells the AI
the way again. lane is for whoever builds a Claude Code plugin in the ccpm marketplace whose AI
works through steps: it holds a ready check for each drift such steps commonly meet, so they pair a
step with its hook by writing the step and one line of hook settings, no code of their own.

## Example

turn's generator makes a work that the AI calling turn checks and then keeps in git. Its step says
so:

```markdown
4. Make the work at the paths in `work` ... Leave it uncommitted: the calling AI checks it and keeps
   it in git.
```

An AI told a step clearly still drifts from it on some runs, such as committing what it just made.
So beside the step, turn's `hooks/hooks.json` has lane's check `no_commit` watch the generator, and
says what to tell it:

```json
{"type": "command", "if": "Bash(git *)",
 "command": "\"${CLAUDE_PLUGIN_ROOT}/lane/run\" no_commit --agent turn:generator --say 'leave the work uncommitted; the caller checks it and keeps it in git'"}
```

When the generator runs `cd "$repo" && git commit -m work`, Claude Code does not run it, and the
generator reads:

```
turn: leave the work uncommitted; the caller checks it and keeps it in git
```

It goes on to its next step with the work uncommitted, as its step says.

## Why lane

lane gives a plugin's hooks what a hook written on its own does not.

- Each hook tells the step's way, not only a refusal.

  A hook that only refuses leaves the AI to find another way to what it was doing; turn's generator,
  refused a commit, split the word `git` to get past the check. Told the step's way, the AI goes
  back to the step.
- Each check is written and tested once, in lane, and every plugin uses it as it is.

  A check written again in each plugin brings its own misreadings of the command with it.
- A check reads the forms the steps tell and the AI writes, not every way the shell has.

  The check stays small and is finished. What must hold whatever the AI writes is held where it
  holds, such as GitHub's branch protection, Claude Code's sandbox or its permission rules, as
  Claude Code's own docs say a check on the command text is not a security boundary.

## Requirements

- A plugin in the ccpm marketplace.

  A plugin takes lane by a symbolic link, which Claude Code copies into the plugin at install only
  from within the same marketplace.
- Python 3.9 or later, run as `python3`, on the machines the plugin runs on.

  Without it, lane's checks stop the tool calls they watch and ask for Python to be installed.

## Installation

lane is not installed on its own, as it has no hooks of its own. From your plugin's folder, link
lane:

```console
ln -s ../lane lane
```

Then, for each step, add to your plugin's `hooks/hooks.json` the check that fits it, the agent it
watches and what it says, as in the example.

## Documentation

- [The checks](checks.md) give each of lane's checks: the drift it notices, the steps it fits and
  how to set it.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../dev/lane/README.md) leads to its UX, its design and how it is
checked. A step that no check fits is met by adding a check to lane there, not by writing one in the
plugin.

## License

[MIT License](../LICENSE)
