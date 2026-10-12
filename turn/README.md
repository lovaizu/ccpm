# turn

Have Claude Code make a document or a prompt with turn, and it comes back already read by a second
AI in the place of the person it is for, its receiver, with what that reader could not take made again, and only
what you alone can decide left to you. turn is for anyone who has Claude Code make such work, by
asking in a conversation or from the steps of their own plugin.

When Claude writes something and checks it itself, it checks as the writer, who already knows what
each line means. With turn, the reader is an AI that knows nothing of how the work was made: it
starts where the receiver starts, and answers every question of a checklist for that kind of work.
Where it missed something, turn finds why, makes the work again from that cause, and has the new
version read once more before you get it.

## Example

You want the README of a small command-line tool. You have notes on it, and a checklist for READMEs.
In Claude Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

turn shows how the work will go, then what it means to make. If that is not what you want, press Esc
and say so.

```console
Plan: 1 write → 2 read → 3 check   (once more if something was missed; two rounds at most)

Round 1
  1 write   Developers who find the tool on GitHub can tell what it saves them and run it
            on their own files.                            .turn/task-2/1/README.md
  2 read    Read as a developer who meets the tool on GitHub.
  3 check   ⚠️ The reader could not tell which Python version the tool needs.
            ⚠️ The reader could not picture the result on their own files.
                                                           .turn/task-2/1/judgment.json
Round 2
  1 write   Made again from why each was missed.           .turn/task-2/2/README.md
  2 read    Read again, as the same developer.
  3 check   ✅ Nothing missed.

The README is at README.md.
❓ Which license is the tool under? Your notes do not say, so the README leaves it out.
```

Answer the question, and turn runs again with your answer. When the first round misses nothing,
turn stops there. When the second round still misses something, you get the work as it is, with
what was missed and why, and decide whether to run it again; turn does not change it again unread.
Each round's work and what the reader and the check found stay under `.turn/`. turn changes nothing
else in your repository, and never commits or pushes. If you stop it partway, ask again and it
carries on from where it stopped.

From a plugin, a step writes the task as a CCS, a JSON file of what to make, for whom, from what and
against which checklists, and calls `turn:up` with where it is and where to write the result:

````markdown
Write this task as a CCS in .setup/task-1.json, in the form of turn's `ccs.md`, and call the
`turn:up` skill with these two lines as its arguments:

```
in: .setup/task-1.json
out: .setup/task-2.json
```
````

turn writes the result as a new CCS, from which the step decides what to do next: finish, ask the
user what only they can decide, or decide itself what was left to it.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader starts from a fresh copy of it, as the receiver would.
- Python 3.9 or later, as `python3`: turn checks each CCS with it, using nothing beyond what comes
  with Python.
- jq: turn, and the plugins that call it, read parts of a CCS with it.
- A checklist for each kind of work: a Markdown file of yes-or-no questions, each under a heading
  `### <ID>: <title>`, on what that kind of work must give its receiver. The reader answers each of
  them. The [writ checklists](../writ/references/essentials/) cover documents, READMEs, design
  documents and prompts, and can be used as they are.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#example), with your own notes and checklist. A plugin that calls turn
names it in `dependencies` in its `.claude-plugin/plugin.json`.

## Documentation

- [ccs.md](skills/up/ccs.md): the form of a CCS, what turn writes back, and what each `next` asks of
  the caller.
- [CHANGELOG.md](CHANGELOG.md): what changed in each version.

## License

[MIT](../LICENSE)
