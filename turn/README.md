# turn

With turn, Claude Code makes a work for you, such as a README, a design document, a skill or code,
that passes your checklist of what the work must give the person it is for, so you can hand it on
without first reading it in their place. It is for anyone who has Claude Code make such work, by
asking in a conversation, as this page shows, or from a step of their own plugin, as
[Calling turn from a plugin's step](calling-from-a-plugin.md) shows.

## Example

You want the README of a small command-line tool. You have notes on it in `docs/notes.md`, and a
checklist for READMEs in `checklists/readme.md`: a list of items, each one thing a README must give
the person the work is for, such as being able to tell which Python version the tool needs. In
Claude Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

Naming turn is what has Claude hand your request to turn as a task, instead of writing the README
itself. The person the work is for, here developers who find the tool on GitHub, and the notes and
checklist you name beside it, are what the task is made from.

Each run of turn writes the work, has an AI that did not write it, the reader, read it as the
developer would, and checks each item of your checklist against that reading. It asks you nothing
while it works, and shows each step as it reaches it:

```console
Plan: 1 write → 2 read → 3 check

  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and run it on their own files.
  2 read    Read as a developer who finds the tool on GitHub.
  3 check   ⚠️ Not yet: the developer can tell which Python version the tool needs.
            ⚠️ Not yet: the developer can picture the result on their own files.
The work is at README.md; running again can give what is not yet there.

Plan: 1 write → 2 read → 3 check

  1 write   To make: the same, now naming the Python version and showing a result on a sample file.
  2 read    Read again, as the same developer.
  3 check   ✅ Nothing missing.
The work is at README.md, waiting on you for one point.
❓ Which license is the tool under? Your notes do not say, so the README names none yet.

> MIT

Plan: 1 write → 2 read → 3 check

  1 write   To make: the same, now naming the MIT license.
  2 read    Read again, as the same developer.
  3 check   ✅ Nothing missing.
done
The work is at README.md.
```

The line after `To make:` is what the work will let the developer do, shown before turn writes. If
it is not what you want, press Esc and say what you want instead; turn starts over with your words,
from the work as it stands.

Each ⚠️ is something the work does not give the developer yet. When the work itself can give it,
turn ends the run saying so, and Claude runs turn again from the work as it stands, as above. When
Claude judges another run will not give it, Claude stops and tells you what is still missing, for
you to decide whether to run again or take the work as it is.

Each ❓ is something only you can decide, which your notes and checklist leave open. turn leaves it
out of the work and ends the run by asking it, with every other such question, instead of with
`done`. When you answer, Claude runs turn again with your answers, from the work as it stands, and
the run ends with `done` once nothing is left for you.

## Why turn

When Claude checks what it has just written, it already knows what each line means, so it can miss
what a newcomer would not understand, as people do with their own writing. turn is built on this
assumption, and what it gives over asking Claude alone follows from it:

- The work is read by the reader, which did not write it. The reader works in a fresh copy of your
  repository as committed, with the work put in, so it has only what the person the work is for
  would have.
- turn's check counts an item as passed only where lines of the work give it, and keeps those lines
  in `.turn/` in your repository, so you can check a pass instead of taking it on trust.
- What falls short is made again from what the work should give, not patched where it showed, and
  the work is made to keep giving every item it already gave.
- You are asked only what you alone can decide, and only at the end, so you can leave turn at work
  and answer everything at once.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader's copy is made from it. turn writes over a file already there only
  when git holds every change to it, so you can get the old one back; otherwise it stops before any
  work and says so.
- Python 3.9 or later, as `python3`, with nothing beyond what comes with it: turn's own scripts run
  on it.
- jq: turn reads and changes its own JSON files with it.
- A checklist for each kind of work, as a Markdown file in your repository, named in your request by
  its path. Each item's ID is a capital letter, a hyphen and a number:

  ```markdown
  ---
  name: readme
  version: 0.1.0
  ---

  # README

  A README lets a developer who finds the tool decide whether to use it, and start.

  ### B-1: Python version

  Can the developer tell which Python version the tool needs?
  ```

  The [writ checklists](../writ/checklists/) in this repository cover documents,
  READMEs, design documents, prompts, code and its tests, and checklists; copy the ones you need
  into your repository.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#example), naming turn, with the person your work is for and your own
notes and checklist.

## Documentation

- [Calling turn from a plugin's step](calling-from-a-plugin.md): handing turn a task from a step of
  your own plugin, and what to do with what it hands back.
- [Changelog](CHANGELOG.md): what changed in each version.

## License

[MIT License](../LICENSE)
