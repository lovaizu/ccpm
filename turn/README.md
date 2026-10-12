# turn

turn has Claude Code make a document or a prompt, such as a README, a design document or a skill,
and gives it back already read by someone in the place of the person it is for, made again where
that reading could not take what it needed, with only the questions you alone can answer. It is for
anyone who has Claude Code write such work, by asking in a conversation or from the steps of their
own plugin. It does not make code, which is checked by running its tests rather than by reading.

What only turn gives is a reading by an AI that did not write the work, in a fresh copy of your
repository that holds only what the person the work is for would have, against a checklist you
choose for that kind of work. Each item of the checklist, each thing it asks, counts as met only
where the lines of the work show it. When Claude checks what it has just written, it checks as the
writer, who knows what each line means, and is likely to pass what a newcomer would miss, as a
person reviewing their own writing does; turn is built on that assumption.

This README takes you to a first result by asking in a conversation. How a step of your own plugin
hands turn a task is in [ccs.md](skills/up/ccs.md).

## Example

You want the README of a small command-line tool. You have notes on it, and a checklist for READMEs.
In Claude Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

Claude writes your request down as the task turn takes: where the work goes, who it is for, what
they use it for, and which notes and checklist to work from. It starts turn with it, and turn shows:

```console
Plan: 1 write → 2 read → 3 check   (once more if something is missing; two rounds at most)

Round 1
  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and run it on their own files.
            .turn/readme/1/README.md
  2 read    Read as a developer who finds the tool on GitHub.
            .turn/readme/1/reading.json
  3 check   ⚠️ The reader could not tell which Python version the tool needs.
            ⚠️ The reader could not picture the result on their own files.
Round 2
  1 write   To make: the same, made again from why each was missing.
            .turn/readme/2/README.md
  2 read    Read again, as the same developer.
            .turn/readme/2/reading.json
  3 check   ✅ Nothing missing.

The README is at README.md.
❓ Which license is the tool under? Your notes do not say, so the README leaves it out.
```

The line after `To make:` is shown before turn writes. If it is not what you want, press Esc and say
what you want instead; Claude passes your words to turn, which starts again from the work as it
stands.

Each ⚠️ is something the reader could not take from the work. The next round makes the work again
from why it was missing, rather than patching the line where it showed, and has it read again.

Answer the question marked ❓ in the conversation: Claude adds your answer to the task and starts
turn again, which has the changed work read again before you get it. If something is still missing
after the second round, it comes back to you in the same way, with why, and you choose whether to
run turn again.

The paths are in `.turn/` in your repository. turn leaves each round's work and its reading there
for you to open, and for each item of the checklist, the lines of the work that show it met or why
none do, and the version of the checklist the work was made and checked by.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader's fresh copy is made from it.
- Python 3.9 or later, as `python3`, with nothing beyond what comes with it: turn's own scripts run
  on it, for what must come out the same every time, such as checking the task and keeping the
  record in `.turn/`.
- jq: the task is kept in a JSON file, and turn, and whoever writes the task, Claude in your
  conversation or your plugin's step, read and change parts of it with jq.
- A checklist for each kind of work, in your repository, since the work is made and checked by its
  items and the task names the checklist by its path there: a Markdown file that opens with what
  such work is for, followed by each item under a heading `### <ID>: <title>`. The
  [writ checklists](../writ/references/essentials/) cover documents, READMEs, design documents and
  prompts; copy the ones you need into your repository, as `checklists/readme.md` is in the
  Example.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#example), with your own notes and checklist.

## Documentation

- Calling turn from a step of your own plugin: [ccs.md](skills/up/ccs.md).
- What changed in each version: [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](../LICENSE)
