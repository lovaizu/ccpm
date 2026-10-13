# turn

With turn, Claude Code can make any work for you, such as a README, a design document, a skill or
code, that passes your checklist. Another AI reads the work as the person it is for, and what does
not pass yet is made again. You are asked only what you alone can answer, as soon as it comes up,
while the work goes on.

turn is for anyone who has Claude Code make such work, in a conversation or from a step of their
own plugin. Any kind of work fits, as long as there is a checklist to measure it by.

Why another reader: when Claude checks what it has just written, it reads as the writer. It knows
what each line means, so it can miss what a newcomer would not understand, as people do with their
own writing. turn is built on this assumption. Its reader did not write the work, and reads it in a
fresh copy of your repository that holds only what the person it is for would have. Each item of
the checklist counts as passed only where lines of the work show it.

This README shows how to get a first result by asking in a conversation. To call turn from a step of
your own plugin, see [Calling turn from a plugin's step](calling-from-a-plugin.md).

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
            ❓ Which license is the tool under? Your notes do not say.

> MIT

            .turn/readme/1/README.md
  2 read    Read as a developer who finds the tool on GitHub.
            .turn/readme/1/first-user.json
  3 check   ⚠️ Not yet: the developer can tell which Python version the tool needs.
            ⚠️ Not yet: the developer can picture the result on their own files.
Round 2
  1 write   To make: the same, now naming the Python version and showing a result on a sample file.
            .turn/readme/2/README.md
  2 read    Read again, as the same developer.
            .turn/readme/2/first-user.json
  3 check   ✅ Nothing missing.
done
The work is at README.md.
```

The line after `To make:` is shown before turn writes. If it is not what you want, press Esc and say
what you want instead; Claude rewrites its request to turn from your words, as if you had asked so
from the start, and turn starts again from the work as it stands.

Each ⚠️ is something the work does not yet give the person it is for, said as what they will be
able to do once it does. turn works out how the work would give it, such as a line on the Python
version, makes the work again with that rather than patching the line where it showed, and has it
read again.

Answer a question marked ❓ when it shows. turn goes on writing meanwhile, and puts your answer
into the work before it is read. If something is still missing after the second round, it comes
back to you with what the work would need to give it, and you choose whether to run turn again.

The paths are in `.turn/` in your repository, where turn keeps what you may want to open later:
each round's work and its reading; for each item of the checklist, the lines that show it met, or
what the work would need to meet it; and the version of the checklist the work was checked by.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader's fresh copy is made from it.
- Python 3.9 or later, as `python3`, with nothing beyond what comes with it: turn's own scripts run
  on it, for what must come out the same every time, such as checking the task and keeping the
  record in `.turn/`.
- jq: the task is kept in a JSON file, and turn, and whoever writes the task, Claude in your
  conversation or your plugin's step, read and change parts of it with jq.
- A checklist for each kind of work: the work is made and checked by its items. It is a Markdown
  file that opens with front matter giving its `name` and `version`, then says what such work is
  for, followed by each item under a heading `### <ID>: <title>`. Keep it in your repository, since the task names it by its path there. The
  [writ checklists](../writ/references/essentials/) cover documents, READMEs, design documents and
  prompts; copy the ones you need, as `checklists/readme.md` is in the Example.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#example), with your own notes and checklist.

## Documentation

- [Calling turn from a plugin's step](calling-from-a-plugin.md)
- [Changelog](CHANGELOG.md)

## License

[MIT License](../LICENSE)
