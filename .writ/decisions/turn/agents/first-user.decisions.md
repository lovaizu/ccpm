# What turn/agents/first-user.md says

## prompt

### B-1: What is expected
- The agent is the receiver it is given, meeting the work for the first time, for the use it is
  given. It shows what the work gives the receiver: for each item of the run's list, what it took
  from the work and where, as the receiver would take it.

### B-2: Why it is needed
- The orchestrator decides each item starting from what the first user took; a writer checking its
  own work passes what a newcomer would miss, so the reading must come from one that did not write
  it and has only what the receiver would open.

### B-3: Everything that must happen every time
- It is handed the path of a brief, a JSON file holding `work`, `deliverable` (where the work will
  be, from which its links are followed), `opens` (what the receiver opens with the work),
  `receiver`, `use`, `list`, `form` and `check` (the command that checks its form).
- It reads the brief whole and the list whole; each item names one thing the receiver could take
  from the work.
- It reads the work once from the top, as the receiver, for the use; where the work leads the
  receiver to a file of `opens`, it opens that file as they would.
- It writes its form: for each item it took something for, under the item's ID, in `took`, what it
  took from the work for it in its own words, and in `lines`, the lines it took it from, such as
  `3-5, 12`; nothing for any other item.
- It runs `check` and fixes each place it names until it prints `filled`, then hands back one line
  saying the form is written.

### B-21: The scope of its inputs
- It works from what the brief names alone, so that it takes from the work only what the receiver
  would and stops where they would; turn's hook stops a read of anything else and names what may be
  read.

## prompt: Format

### F-1: Shape
- name: `first-user`.
- description: reads a work of a turn run as its receiver, with only what the receiver opens with
  it, and says for each item of the run's list what it took from the work and where; called by
  turn:up.
