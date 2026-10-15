# turn

turn is a plugin for Claude Code. With it, Claude Code makes a work for you, such as a README, a
design document, a skill, or code with its tests, that passes your checklist of what the work
must give the person it is for, so you can hand it on without first reading it in their place. It is for anyone who has
Claude Code make such work, by asking in a conversation, as this page shows, or from a step of their
own plugin, as
[Calling turn from a plugin's step](calling-from-a-plugin.md) shows.

## Example

You want the README of a small command-line tool. You have notes on it in `docs/notes.md`, and a
checklist for READMEs in `checklists/readme.md`: a list of items, each one thing a README must give
the person it is for, such as being able to tell which Python version the tool needs.

In Claude Code, you type:

```
With turn, write the README of this tool for developers who find it on GitHub, from docs/notes.md, against checklists/readme.md.
```

Here is what turn shows in this example:

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

- Each `Plan:` line starts one writing, reading and checking. A run of turn does this once, or twice
  when the check finds something the work itself can give; here the first run has two, and the run
  after your answer has one.
- The line after `To make:` is what the work will let the developer do, shown before turn writes. If
  it is not what you want, press Esc and say what you want instead; turn starts over with your words.
- Each ⚠️ is something the work does not give yet. When the work itself can give it, turn makes the
  work again on it in the same run.
- Each ❓ is something only you can decide, which your notes and checklist leave open. turn leaves
  it out of the work and ends the run asking it, together with every other such question; your
  answer starts the next run, as `> MIT` does above.
- The work goes where your request says, or where Claude takes it from your request: here,
  `README.md` at the top of the repository. A work can be several files that serve one purpose,
  such as code and its tests; turn writes, reads and checks them together.

## Why turn

When Claude checks what it has just written, it already knows what each line means, so it can miss
what a newcomer would not understand, as people do with their own writing. turn is built on this:

- The work is read by the reader, which did not write it and has only the work and what the person it
  is for would open with it.
- turn makes the work from your notes and checklist alone. So the work follows what you decided
  rather than whatever turn happened to open, and each run of the same request works from the same
  inputs.
- turn counts an item as passed only where lines of the work give it, and keeps those lines in
  `.turn/` in your repository, where you can open them and check each item yourself instead of
  taking it on trust.
- What falls short is made again from what the work should give, not patched where it showed, and
  the work keeps giving every item it already gave.
- You are asked only what you alone can decide, and only at the end, so you can leave turn at work
  and answer everything at once.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: if the work goes to files already there, commit them first, so you can get
  the old ones back; until you do, turn stops before any work and says so.
- Python 3.9 or later as `python3`, with nothing beyond what comes with it: turn's own scripts run on
  it.
- jq: turn reads and changes its own JSON files with it.
- A checklist for each kind of work, as a Markdown file in your repository, named in your request by
  its path. A short checklist file:

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

  - `name` and `version`: turn keeps each item's result in `.turn/` under them, so you can later
    tell which version of your checklist an item was judged by.
  - The paragraph under the title: what such work is for. turn reads it with every item when it
    reads and checks the work.
  - A heading that starts with an ID, a capital letter, a hyphen and a number such as `B-1`, makes
    an item: one thing the work must give, asked as a question. Other headings are not items.

  You can write your own, or copy the ones you need from the [writ checklists](../writ/checklists/)
  in this repository, which cover documents, READMEs, design documents, prompts, code and its tests,
  and checklists.

## Installation

In Claude Code, add the marketplace once, then install turn:

```
/plugin marketplace add lovaizu/ccpm
/plugin install turn@ccpm
```

Then ask as in the example, naming turn, with the person your work is for and your own notes and
checklist.

## Documentation

- [Calling turn from a plugin's step](calling-from-a-plugin.md): handing turn a task from a step of
  your own plugin, and what to do with what it hands back.
- [Changelog](CHANGELOG.md): what changed in each version.

## License

[MIT License](../LICENSE).
