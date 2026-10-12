# turn

Have Claude Code make a document or a prompt with turn, and you can hand it on without first
reading it yourself as the person it is for. Before you get it, a second AI, the reader, has read
it as that person would, what it could not take from it has been made again, and you are asked
only what you alone can decide. turn is for anyone who has Claude Code write such work, by asking
in a conversation or from the steps of their own plugin. It does not make code, which is checked
by running its tests rather than by reading.

When Claude checks what it has just written, it checks as the writer, who already knows what each
line means, and passes what the person it is for would miss. turn's reader knows nothing of how the
work was made: it starts where that person starts, and answers each question of a checklist you
choose for that kind of work. For what it missed, turn finds why, and the work is made again
from that cause instead of patched where the miss showed.

## Example

### In a conversation

You want the README of a small command-line tool. You have notes on it, and a checklist for READMEs.
In Claude Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

turn shows the plan, then, before anything is written, what it means to make:

```console
Plan: 1 write → 2 read → 3 check   (once more if something was missed; two rounds at most)

Round 1
  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and run it on their own files.
            .turn/readme/1/README.md
  2 read    Read as a developer who meets the tool on GitHub.
            .turn/readme/1/reading.json
  3 check   ⚠️ The reader could not tell which Python version the tool needs.
            ⚠️ The reader could not picture the result on their own files.
Round 2
  1 write   To make: the same, made again from why each was missed.
            .turn/readme/2/README.md
  2 read    Read again, as the same developer.
            .turn/readme/2/reading.json
  3 check   ✅ Nothing missed.

The README is at README.md.
❓ Which license is the tool under? Your notes do not say, so the README leaves it out.
```

In each round, an AI writes the work, the reader reads it as the person it is for, and in the
check further AIs, which neither wrote nor read it, find why anything was missed and judge each
question of the checklist; Claude in your conversation decides from what they found. If the line
after `To make:` is not what you want, press Esc and say what you want instead: the work starts
again from what you say. The paths are where each round's work, and what the reader took from it,
are kept, in turn's folder `.turn/`, for you to open while turn works or after.

Answer the question, and turn runs again from the work as it stands, with your answer, and has the
changed work read again before you get it. When the first round misses nothing, turn stops there.
When the second round still misses something, you get the work as it is, with what was missed and
why, and decide whether to run it again; turn does not change it again unread. turn changes nothing
in your repository but the work and `.turn/`, and never commits or pushes.

### From your plugin

A step of your plugin hands turn the same kind of task in a file and decides its next move from the
file turn writes back:

````markdown
Write this task in .setup/task-1.json, in the form given in turn's `ccs.md`, and call the
`turn:up` skill with these two lines as its arguments:

```
in: .setup/task-1.json
out: .setup/task-2.json
```
````

turn works as in the conversation above and writes `.setup/task-2.json` in the same form, from
which the step decides its next move, as `ccs.md` describes.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader reads the work in a fresh copy of it that turn makes and removes,
  so it sees nothing the person the work is for would not have.
- Python 3.9 or later, as `python3`: turn checks the task it is given, and what it returns, with it,
  using nothing beyond what comes with Python.
- jq: turn, and a plugin that calls it, read parts of the task file with it.
- A checklist for each kind of work, as a Markdown file that opens with who reads such work and what
  it gives them, followed by each question under a heading `### <ID>: <title>`: the reader reads as
  the person the opening names and answers the questions one by one. The
  [writ checklists](../writ/references/essentials/) cover documents, READMEs, design documents and
  prompts, and can be used as they are.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#in-a-conversation), with your own notes and checklist. A plugin that
calls turn also names it in `dependencies` in its `.claude-plugin/plugin.json`, so that installing
the plugin installs turn.

## Documentation

- [ccs.md](skills/up/ccs.md): the form of the task file a plugin writes and of the one turn writes
  back.
- [CHANGELOG.md](CHANGELOG.md): what changed in each version.

## License

[MIT](../LICENSE)
