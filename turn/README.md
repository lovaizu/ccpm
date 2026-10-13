# turn

With turn, Claude Code makes a work for you, such as a README, a design document, a skill or code,
that passes your checklist of what the work must give the person it is for, so you can hand it on
without first reading it in their place. It is for anyone who has Claude Code make such work, by
asking in a conversation, as below, or from a step of their own plugin, as
[Calling turn from a plugin's step](calling-from-a-plugin.md) shows.

## Example

You want the README of a small command-line tool. You have notes on it in `docs/notes.md`, and a
checklist for READMEs in `checklists/readme.md`: a list of items, each one thing a README must give
the person who reads it, such as being able to tell which Python version the tool needs. In Claude
Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

Claude writes your request down as a task for turn, in a small JSON file: where the work goes, who
it is for, what they use it for, and which notes and checklist to work from. It starts turn with it,
and turn shows each step of each round as it reaches it. Under the writing step is the work as that
round made it, and under the reading step what another AI, reading the work as the developer, took
from it for each item of your checklist. Both files stay in the run's folder under `.turn/`, and you
may open them to see how the work was read:

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

The line after `To make:` is what the work will let the developer do, shown before turn writes. If
it is not what you want, press Esc and say what you want instead; turn starts over with your words,
from the work as it stands.

Answer a question marked ❓ when it shows; turn goes on writing meanwhile.

Each ⚠️ is something the work does not give the developer yet. turn makes the work again to give it
and has it read again. If something is still missing after the second round, turn shows it and asks
whether to run again or take the work as it is.

What turn leaves in your files:

- The work, where you asked. turn writes over a file already there only when git holds every change
  to it, so you can get the old one back; otherwise it stops before any work and says so.
- The task Claude writes and turn's answer to it, which says whether anything is left for you: two
  small JSON files. Claude picks where they go when it starts turn; name a place in your request if
  you want them somewhere.
- The run's folder, `.turn/<name>/`, named after turn's answer file, such as `.turn/readme/`: the
  files shown under each step, and turn's check of each item.

turn commits nothing. If a file outside these changes while turn runs, such as one you edit
meanwhile, turn names it in a last line, `Also changed during the run, outside the work:`, so you
can tell what turn did not write.

## Why turn

When Claude checks what it has just written, it reads as the writer. It knows what each line means,
so it can miss what a newcomer would not understand, as people do with their own writing. turn is
built on this assumption, and what it gives over asking Claude alone follows from it:

- The work is read by another AI, which did not write it: the reader. It reads in a fresh copy of
  your repository as committed, with the work put in, so it has only what the person the work is for
  would have.
- An item counts as passed only where lines of the work give it, and `.turn/` keeps those lines,
  so you can check a pass instead of taking it on trust.
- What falls short is made again from what the work should give, not patched where it showed, and
  the work is made to keep giving every item it already gave.
- You are asked only what you alone can answer, as soon as it comes up, while the work goes on.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader's copy is made from it, and turn only writes over a file git can
  give back.
- Python 3.9 or later, as `python3`, with nothing beyond what comes with it: turn's own scripts run
  on it. turn does not install it.
- jq: turn and Claude read and change the task with it. turn does not install it.
- A checklist for each kind of work, as a file in your repository, since the task names it by its
  path. It is a Markdown file that opens with front matter giving its `name` and `version`, then
  says what such work is for, followed by each item under a heading `### <ID>: <title>`, where the
  ID is a capital letter, a hyphen and a number, such as `B-1`. The
  [writ checklists](../writ/references/essentials/) in this repository cover documents, READMEs,
  design documents and prompts; copy the ones you need into your repository, as
  `checklists/readme.md` is in the Example.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#example), with your own notes and checklist.

## Documentation

- [Calling turn from a plugin's step](calling-from-a-plugin.md): handing turn a task from a step of
  your own plugin, and what to do with what it hands back.
- [Changelog](CHANGELOG.md): what changed in each version.

## License

[MIT License](../LICENSE)
