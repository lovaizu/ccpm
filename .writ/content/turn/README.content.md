# What turn's README says

## readme

### B-1: What they gain
- With turn, Claude Code makes a work for you, such as a README, a design document, a skill or code,
  that passes your checklist of what the work must give the person it is for, so you can hand it on
  without first reading it in their place.

### B-2: Who it is for
- Anyone who has Claude Code make such work, by asking in a conversation, or from a step of their
  own plugin, which "Calling turn from a plugin's step" (`calling-from-a-plugin.md`) covers.

### B-3: Why this one
- When Claude checks what it has just written, it already knows what each line means, so it can miss
  what a newcomer would not understand, as people do with their own writing. turn is built on this.
- The work is read by an AI that did not write it, the reader, which has only the work and what the
  person it is for would open with it.
- turn makes the work from your notes and checklist alone. So the work follows what you decided
  rather than whatever turn happened to open, and each run of the same request works from the same
  inputs.
- turn counts an item as passed only where lines of the work give it, and keeps those lines in
  `.turn/` in your repository, so you can check a pass instead of taking it on trust.
- What falls short is made again from what the work should give, not patched where it showed, and
  the work keeps giving every item it already gave.
- You are asked only what you alone can decide, and only at the end, so you can leave turn at work
  and answer everything at once.

### B-4: Using it on their own work
- The situation: you want the README of a small command-line tool; you have notes on it in
  `docs/notes.md`, and a checklist for READMEs in `checklists/readme.md`.
- A checklist: a list of items, each one thing a README must give the person it is for, such as
  being able to tell which Python version the tool needs.
- What you type in Claude Code: `With turn, write the README of this tool for developers who find it
  on GitHub, from docs/notes.md, against checklists/readme.md.`
- Naming turn has Claude hand your request to turn instead of writing the README itself. The README
  is made from your notes and checklist alone; what your notes leave open stays open for you.
- Each run writes the work, has the reader read it as the developer would, and checks each item
  against that reading; when the check finds something the work itself can give, it writes, reads
  and checks once more in the same run. It asks nothing while it works, and shows each step as it
  reaches it.
- What turn shows in this example:
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
- The line after `To make:` is what the work will let the developer do, shown before turn writes; if
  it is not what you want, you press Esc and say what you want instead, and turn starts over with
  your words.
- Each ⚠️ is something the work does not give yet. When the work itself can give it, turn makes the
  work again on it in the same run.
- Each ❓ is something only you can decide, which your notes and checklist leave open. turn leaves it
  out of the work and ends the run asking it, with every other such question. When you answer,
  Claude adds your answer to what the work says and runs turn again.
- The work goes where your request says, or where Claude takes it from your request: here,
  README.md at the top of the repository.

### B-5: Started from the README alone
- After installing, you ask as in the example, naming turn, with the person your work is for and your
  own notes and checklist.

### B-6: Where to go for more
- "Calling turn from a plugin's step" (`calling-from-a-plugin.md`): handing turn a task from a step of
  your own plugin, and what to do with what it hands back.
- The changelog (`CHANGELOG.md`): what changed in each version.

### B-7: Terms of use
- MIT License (`../LICENSE`).

### B-8: What it is
- turn is a plugin for Claude Code.

### B-9: Why each requirement is needed
- Claude Code: turn runs inside it.
- A git repository: if the work goes to a file already there, commit the file first, so you can get
  the old one back; until you do, turn stops before any work and says so.
- Python 3.9 or later as `python3`, with nothing beyond what comes with it: turn's own scripts run on
  it.
- jq: turn reads and changes its own JSON files with it.
- A checklist for each kind of work, as a Markdown file in your repository, named in your request by
  its path. Each item's ID is a capital letter, a hyphen and a number. A short checklist file:
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
- The writ checklists in this repository (`../writ/checklists/`) cover documents, READMEs, design
  documents, prompts, code and its tests, and checklists; you copy the ones you need into your
  repository.
- Installing: in Claude Code, you add the marketplace once with `/plugin marketplace add
  lovaizu/ccpm`, then install turn with `/plugin install turn@ccpm`.
- A checklist file: `name` and `version`, under which turn keeps each item's result in `.turn/`, so
  you can later tell which version an item was judged by; the paragraph under the title, what such
  work is for, which turn reads with every item; and each heading that starts with an ID, which makes
  an item, one thing the work must give, asked as a question.

## readme: Usability

### U-1: Nothing to learn of the product's inside
- The only part of turn named is the reader, the AI that did not write the work.

## doc

### B-12: Every term known
- The reader: the AI that did not write the work, which reads it as the person it is for would.
- A run: turn writing, reading and checking the work, once or, when the check finds something the
  work itself can give, twice.

### B-13: One name for each thing
- "The reader" names only the AI; the person the work is for is "the person the work is for", or in
  the example "the developer".
