# lane

lane is a Claude Code plugin that tells a subagent of your plugin the step it drifts from, in the
step's own sentence.

An AI that runs your plugin's steps drifts from some of them now and then, such as committing where
a step says not to, or ending its work before the subagent that reviews it has run. A hook that only
refuses leaves the AI to look for another way to what it was doing: one AI refused a commit split
the word `git` to get past the check. And each check you write yourself is one more piece of code to
write, test and keep right in your plugin.

If you have an AI build a plugin whose work an AI does in several steps, lane lets your plugin's
subagents run at full speed with no one watching each move, each finding its own way back to its
steps. Your AI, the one building your plugin, lays the checks without writing one, and lane asks you
nothing.

A lane is laid on one step of a subagent, a step being one numbered item of what the subagent is
told to do. A lane is a sentence written into the step, together with a hook that notices a drift
from it, stops the call that drifts, and tells the subagent that sentence again. Told the step's own
sentence, the subagent goes back to the step rather than around the refusal. Your AI writes the
lanes it proposes in a proposal, a JSON file. lane's layer, the script `lay.py`, prints them as they
would be laid. Once your AI approves them, `lay.py` writes them into your plugin with lane's guard,
the code that runs the hooks. lane writes and tests each kind of check once, so your plugin carries
no check of its own that might misread a command. Your AI lays lanes only where a step alone is not sure to
hold, so the hooks stay few and small.

The order your subagents go in is one more thing to drift from. Where one subagent, the
orchestrator, starts the others, your AI writes their order in the proposal as a flow: which
subagent comes after which, and which answer sends the work back. `lay.py` then lays a lane on a
step of the orchestrator, with the sentence "Take each move `flow.py` prints." `flow.py`, a script
of lane's, prints the next move, such as starting the reviewer, from the flow and from what the
subagents have answered.
When the orchestrator does something else, or is about to end, before it takes that move, its hook
stops it and tells it that sentence. So your plugin keeps no script of its own for the order.

**Non-goals**

- lane is no security boundary. What must hold whatever the AI writes is held by GitHub's branch
  protection, Claude Code's sandbox or its permission rules, as Claude Code's own docs say a check
  on the command text is not a security boundary.
- lane reads a command in the forms the steps tell and the AI writes, not in every way the shell
  has. Where lane cannot settle which file a command names, it stops the call and tells the
  subagent to name the file by its path.
- lane lays lanes on subagents alone, not on skills. A hook written into a skill goes on running for
  the rest of the session once the skill has started, and is not told which skill runs, so it would
  act on work outside the skill. A step to keep goes into a subagent the skill starts. So the
  orchestrator of a flow is a subagent, not the main conversation.
- A flow is an order your AI sets beforehand, with the ways back it names. lane does not choose the
  next subagent from what a run finds; a plugin whose order changes that way says the order in its
  orchestrator's steps.
- lane sees only what shows in a tool call or in how the subagent ends, not what the subagent only
  weighs.

## Requirements

- Claude Code, where your plugin runs and lane is installed.
- Python 3.9 or later, run as `python3`, on the machines the plugin runs on.

  Without it, the hooks stop the tool calls they watch, each asking for Python to be installed,
  and at a subagent's end tell you so and let it end.

## Installation

lane comes from ccpm, a marketplace of Claude Code plugins on GitHub. Add the marketplace, then
install lane:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

`claude plugin list --json` then lists `lane@ccpm`, and its `installPath` is lane's folder. Claude
Code installs each version of lane in a new folder, so your AI reads the folder there each time.
lane is ready when `lay.py` in that folder prints its usage:

```console
$ python3 <lane's folder>/scripts/lay.py
usage: lay.py print <proposal>
       lay.py write <proposal>
       lay.py up <plugin>
```

## Walkthrough

In your plugin `notes`, the skill `/notes:changelog` starts a subagent, `notes-lead`, the
orchestrator of the work. `notes-lead` starts `changelog-writer`, which writes the new entries of a
project's changelog, and then `changelog-reviewer`, which reads them against the project's commits.
The reviewer answers `more` when an entry needs the writer again. The skill shows you the entries
and commits `CHANGELOG.md` once you have said OK. The first step of `notes-lead`, in
`agents/notes-lead.md`, and one of the writer's steps, in `agents/changelog-writer.md`, say:

```markdown
1. Start the subagents of the work.
```

```markdown
3. Write the new entries into `CHANGELOG.md`.
```

While building `notes`, your AI knows that `CHANGELOG.md` is the only file step 3 writes, and that
the skill, not the subagent, commits it. It also knows that the reviewer comes after the writer,
and that the reviewer's `more` sends the work back to the writer. It proposes the flow, laid on
step 1 of `notes-lead`, and two lanes on step 3 of the writer, write_only and hands_off, in
`.lane/20261030-notes/notes.json` at the root of the repository:

```json
{"plugin": "notes",
 "flow": {"orchestrator": "notes-lead", "step": 1,
  "order": ["changelog-writer", "changelog-reviewer"],
  "back": [{"from": "changelog-reviewer", "to": "changelog-writer", "while": "more"}]},
 "subagents": [{"name": "changelog-writer", "steps": [{"step": 3, "lanes": [
  {"lane": "write_only", "takes": ["CHANGELOG.md"]},
  {"lane": "hands_off", "takes": ["git commit", "git push"]}]}]}]}
```

Your AI has `lay.py print` show the flow and the lanes, each under the action it watches with its
hook, and each step as it would read:

```console
$ python3 <lane's folder>/scripts/lay.py print .lane/20261030-notes/notes.json
Flow of notes-lead, laid on its step 1:
  changelog-writer, then changelog-reviewer
  back to changelog-writer while changelog-reviewer answers more
  then notes-lead ends
Lanes on step 1 of notes-lead, each hook acting in notes-lead alone:
  follow: Take each move `flow.py` prints.  hook follow_next

1. Start the subagents of the work. Take each move `flow.py` prints.

Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  write: Write only `CHANGELOG.md`.              hook write_only
  run:   Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`. Do not run `git commit` or `git push`.
```

Your AI approves them, and has `lay.py write` lay them from the same file:

```console
$ python3 <lane's folder>/scripts/lay.py write .lane/20261030-notes/notes.json
Wrote step 1 of notes-lead, and where `flow.py` lies, into agents/notes-lead.md.
Wrote step 3 of changelog-writer into agents/changelog-writer.md.
Wrote the hooks of notes-lead and changelog-writer into hooks/hooks.json.
Wrote the flow and the lanes laid into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Removed the proposal .lane/20261030-notes/notes.json.
Removed its folder <the repository>/.lane/20261030-notes.
```

Then you run `/notes:changelog`. `notes-lead` runs `flow.py`, which prints its first move: start
`changelog-writer`. `notes-lead` starts it. When `changelog-writer` runs `git commit -m notes`,
Claude Code does not run it, and the subagent reads:

```
notes: Do not run `git commit` or `git push`.
```

The writer goes back to step 3 and ends with the entries written. `notes-lead`, given the
entries, is about to end with them before the reviewer has run. Its hook stops the end, and
`notes-lead` reads:

```
notes: Take each move `flow.py` prints.
```

`notes-lead` runs `flow.py`, which prints the move to start `changelog-reviewer`. The reviewer
answers `more` for one entry, which misses a fix in the commits. `flow.py` then prints the move to
start the writer again, and after it the reviewer. Once the reviewer no longer answers `more`,
`flow.py` prints no move. `notes-lead` ends with the reviewed entries, and the skill commits the
changelog once you have said OK.

When lane is updated, your AI first runs `lay.py up <your plugin's folder>` on a plugin with lanes
laid before. It brings lane's code in your plugin to lane's version with the same flow and lanes,
and says each lane laid before, for your AI to keep in its next proposal.

Who does what in which order, here and when lane cannot check a call, is in
[the scenes of lane's UX](../../dev/lane/ux.md#scenes).

## How it works

![How lane works](how-it-works.svg)

lane is made of two parts. The layer, `lay.py`, runs while your AI builds your plugin: it prints the
proposal and writes the approved flow and lanes into your plugin. The guard, lane's code in your
plugin's `hooks/lane/`, runs on every call of a subagent with lanes and as it ends: Claude Code
hands it the call, and the guard reads the lanes your AI approved from `hooks/lanes.json`. Both make
each lane's sentence from the same lanes, so what the subagent is told on a drift is the sentence
its step says. `flow.py`, part of the guard's code, reads the flow from the same file. The
orchestrator is a subagent with lanes too, so its calls and its end reach the guard as the other
subagents' do.

## Documentation

- [The lanes](docs/lanes.md) lists each lane lane can lay, the sentence it writes into a step and
  when its hook tells it, and gives the proposal your AI writes them in.
- [The flow](docs/flow.md) gives the form your AI declares a flow in, and how `flow.py` reads what
  each subagent answered.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../../dev/lane/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../../LICENSE)
