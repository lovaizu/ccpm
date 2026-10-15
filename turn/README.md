# turn

turn is a Claude Code plugin with which Claude makes a work for you, such as a README, a design
document, a skill or code with its tests, that passes your checklist of what the work must give the
person it is for, so you can hand it on without first reading it as them yourself. It is for anyone
who has Claude Code make such work, by asking in a conversation or from a step of their own plugin.

## Example

You want the README of a small command-line tool. You have notes on it in `docs/notes.md`, and a
checklist for READMEs in `checklists/readme.md`: a list of items, each one thing a README must give
the person it is for, such as being able to tell which Python version the tool needs.

In Claude Code, you type:

```
With turn, write the README of this tool for developers who find it on GitHub, from docs/notes.md, against checklists/readme.md.
```

Naming turn has Claude hand your request to turn instead of writing the README itself. turn makes
the README from your notes and checklist alone.

A run of turn writes the work, has the reader read it, and checks each item against that reading.
The reader is an AI that did not write the work; it has only the work and what the developer would
open with it, and reads it as the developer would. turn shows each step as it reaches it:

```
Plan: 1 write → 2 read → 3 check

  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and run it on their own files.
  2 read    Read as a developer who finds the tool on GitHub.
  3 check   ⚠️ Not yet: the developer can tell which Python version the tool needs.
            ⚠️ Not yet: the developer can picture the result on their own files.

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
it is not what you want, you press Esc and say what you want instead, and turn starts over with your
words.

Each ⚠️ is an item of your checklist that the reader's reading did not find given. When the work
itself can give it, turn makes the work again on it in the same run. `✅ Nothing missing.` means the
reader's reading found every item given; it reaches as far as your checklist's items and an AI
reading in the developer's place, not the developer themselves.

Each ❓ is something your notes and checklist leave open, which only you can decide. turn asks
nothing while it works: it leaves each such point out of the work and asks them all at the end of the
run. When you answer, as with `MIT` above, Claude adds your answer to what the work says and runs
turn again.

The work goes where your request says, or where Claude takes it from your request: here, README.md
at the top of the repository. A work can be several files that serve one purpose, such as code and
its tests; turn writes, reads and checks them together.

## Why turn

When Claude checks what it has just written, it already knows what each line means, so it can miss
what a newcomer would not understand, as people do with their own writing. turn is built on this.

- You learn where the work fails the person it is for, since the reader does not know what each
  line was meant to say.
- The work follows what you decided: turn opens nothing beyond the notes and checklist you name, so
  each run of the same request works from the same inputs.
- You can check a pass instead of taking it on trust.

  turn counts an item as passed only where lines of the work give it, and keeps those lines in
  `.turn/` in your repository.
- What falls short is made again from what the work should give, not patched where it showed, and
  the work keeps giving every item it already gave.

  Each time the work is made again, the reader reads it whole and every item is checked again.
- You can leave turn at work and answer everything at once.

## Requirements

- Claude Code, which turn runs inside.
- A git repository for your work.

  If the work goes to a file already there, commit the file first, so you can get the old one back;
  until you do, turn stops before any work and says so.
- Python 3.9 or later as `python3`, with nothing beyond what comes with it.

  turn's own scripts run on it.
- jq, the command-line JSON tool.

  turn reads and changes its own JSON files with it.
- A checklist for each kind of work, as a Markdown file in your repository, named in your request by
  its path.

  Its `name` and `version` label the results turn keeps. The paragraph under the title says what
  such work is for, and turn reads it with every item. Each heading that starts with an ID, a capital letter, a
  hyphen and a number, makes an item: one thing the work must give, asked as a question. A short
  checklist file:

  ```
  ---
  name: readme
  version: 0.1.0
  ---

  # README

  A README lets a developer who finds the tool decide whether to use it, and start.

  ### B-1: Python version

  Can the developer tell which Python version the tool needs?
  ```

  The checklists in this repository ([`../rn/checklists/`](../rn/checklists/)) cover documents,
  READMEs, design documents, prompts, code and its tests, and checklists; you copy the ones you need
  into your repository.

## Installation

In Claude Code, add the marketplace once, then install turn:

```
/plugin marketplace add lovaizu/ccpm
/plugin install turn@ccpm
```

Then ask as in the example, naming turn, with the person your work is for and your own notes and
checklist:

```
With turn, write <the work> for <the person it is for>, from <your notes>, against <your checklist>.
```

## Documentation

- [Calling turn from a plugin's step](calling-from-a-plugin.md) tells how to hand turn a task from a
  step of your own plugin, and what to do with what it hands back.
- The [changelog](CHANGELOG.md) tells what changed in each version.

## License

MIT License ([`../LICENSE`](../LICENSE)).
