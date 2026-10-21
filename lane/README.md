# lane

lane lets an AI run the course your plugin sets to the end, at full speed with no one watching
each move, by holding the course in code. The flow holds the whole work: its phases, the parts every
run goes through in turn; the order of each piece of work within them; and the approvals of the
caller, the person or AI that calls your plugin. A lane holds a step that alone is not sure to hold,
a step being one line of what a subagent, an AI your plugin starts for one job, is told to do. The
lane is a sentence of the step together with a hook that notices a drift from it and tells the AI
the sentence again.

lane is a Claude Code plugin for you if you build a plugin whose work an AI does in several steps.
You answer and approve. lane writes your plugin's flow definition, the file that gives its phases,
its order and its rules, and lays the lanes on its subagents. lane's code then holds both on every
run.

## Example

In your plugin `notes`, the skill `/notes:changelog` makes the conversation it is typed in the
orchestrator, the AI that holds the run and decides each move. The orchestrator starts a subagent,
`changelog-writer`, that writes a project's changelog. One of its steps says:

```markdown
3. Write the new entries into `CHANGELOG.md`.
```

You ask Claude in your conversation to lay lanes on `notes`. Claude starts lane's subagent
`lane:up`, which reads the plugin's skills and subagents. It sends Claude, one at a time, each point
the files do not settle and each fact it found that its proposal rests on. Claude puts each to you
and sends your answer back:

```
Step 3 of changelog-writer writes `CHANGELOG.md`. Is it the only file it writes, and who commits it?
```

You answer that it is the only one, and that the orchestrator commits it once you have read it and
said OK. Once every point is settled, `lane:up` proposes the flow, with your approval before the
commit. It proposes the lanes on the steps that alone are not sure to hold, each under the action it
keeps: begin, read, write, run, test, hand on, wait or end; with its hook, and the step as it would
read:

```
Flow of /notes:changelog, in one phase:
  changelog: changelog-writer writes CHANGELOG.md;
             you read it and choose OK when the orchestrator asks;
             the orchestrator commits it, only after your OK.

Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  write: Write only `CHANGELOG.md`.                 hook write_only
  run:   Do not run `git commit` or `git push`.     hook hands_off

3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`. Do not run `git commit`
   or `git push`.
```

You choose OK when Claude asks. `lane:up` writes the flow definition into `notes`, the steps that
tell the flow each move into `/notes:changelog`, the step into `agents/changelog-writer.md` and the
hooks into `hooks/hooks.json`, and puts lane's code, which runs the flow and the hooks, in
`hooks/lane/`.

Then you run `/notes:changelog`. When `changelog-writer` runs `git commit -m notes`, Claude Code
does not run it, and the subagent reads:

```
notes: Do not run `git commit` or `git push`.
```

The orchestrator tells the flow each move before it makes it. When it tells the flow it will commit
before you have said OK, the flow refuses the move, and the orchestrator reads:

```
notes: Commit `CHANGELOG.md` only after the caller's OK on it.
```

The run goes on as its steps say, and ends with the changelog committed once you have said OK.

## Why lane

lane gives a plugin's run what steps and hooks written on their own do not.

- A refusal leads the AI back to its step, not only away from what it tried.

  A hook that only refuses leaves the AI to find another way to what it was doing, such as an AI
  refused a commit splitting the word `git` to get past the check. Told the step's own sentence, the
  AI goes back to the step.
- Each move the orchestrator tells the flow is held to the same course on every run: the flow
  refuses one that breaks your plugin's rules, such as going on before an approval, or having a
  piece of work made again more times than the flow definition allows.

  Tools that keep the plan as a file of tasks, such as Spec Kit or OpenSpec, leave the steps within
  each task to an AI reading a prompt, which keeps them on most runs and not on every one.
- An approval counts only as the OK the caller chose from Claude Code's question, which lane's
  hook records and no AI can fill in.

  An AI that can mark its own approval passes every check that rests on it; in tools whose AI
  writes the approval mark, such as cc-sdd, the mark stops nothing.
- The plan of a run, the tasks it walks, is data the flow keeps, which the orchestrator changes as
  facts come in, each change with its reason.

  The course and its rules stay fixed while the plan follows what the run finds.
- A run stopped anywhere goes on from its last move in a new conversation, as the flow keeps it in
  a file.

  A conversation ends, is cleared or is compacted, and what lives only in it is lost.
- Each check and the flow are written and tested once, in lane.

  Your plugin takes no misreadings of a command, or slips of a course, of its own.
- Lanes are laid only where a step alone is not sure to hold, and a check reads the forms the steps
  tell and the AI writes, not every way the shell has.

  The hooks stay few and small. What must hold whatever the AI writes is held where it holds, such
  as GitHub's branch protection, Claude Code's sandbox or its permission rules, as Claude Code's own
  docs say a check on the command text is not a security boundary.
- Each lane acts only in its subagent.

  Claude Code reads no hooks from a plugin subagent's own file, so lane writes them into the
  plugin's `hooks/hooks.json`, each naming its subagent. A hook written into a skill instead goes on
  running for the rest of the session once the skill has started, and is not told which skill runs,
  so it acts on work outside the skill too. So lane lays lanes on subagents alone, a step to keep
  goes into a subagent the skill starts, and the orchestrator is held by the flow.

## Requirements

- Claude Code, where your plugin runs and lane is installed.
- Python 3.9 or later, run as `python3`, on the machines the plugin runs on.

  Without it, the flow stops the run at its first move and the hooks stop the tool calls they
  watch, each asking for Python to be installed.

## Installation

lane comes from ccpm, a marketplace of Claude Code plugins on GitHub. Add it, then install lane:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

Then ask Claude to lay lanes on your plugin, as in the example. Claude starts `lane:up` from your
conversation, or from a subagent it started, since `lane:up` starts subagents of its own in the
layers below it and Claude Code lets subagents start subagents down to three layers.

lane's code in your plugin's `hooks/lane/` is a copy with its version, which `lane:up` brings to its
own version the next time it is run there. In a plugin of ccpm itself, the code is a link to lane's.

## Documentation

- [The lanes](lanes.md) give each lane lane can lay, under its action, and what its hook notices.
- [The flow](flow.md) gives each key of a flow definition and what it does.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[lane's development folder](../dev/lane/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../LICENSE)
