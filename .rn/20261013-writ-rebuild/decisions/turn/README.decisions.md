# What turn's README says

The README is read by people deciding whether to use turn, so it speaks to anyone who has AI make
documents or code in the steps of their own plugin; its example is the UX's scene, a plugin's step
calling turn.

## readme

### B-2: Who it is for
- Anyone who has AI make documents, code and the like in the steps of their own plugin.

### B-1: What they gain
- turn is a Claude Code plugin: what a step has it make comes back meeting the step's checklists,
  read first by a reader that did not make it, in the place of the one it is for, with each item's
  Good and the lines it rests on.
- A checklist and a Good are said as the UX says them, where they are first met.

### B-4: Using it on their own work
- The example is a step of the reader's own kind that writes a README: the step's AI writes its
  task in a small CCS, calls turn with the CCS's path, its kinds and where the result goes, in a few
  lines of the step's text; turn first sends it by message the question the CCS leaves to the user,
  and the AI puts it to the user and sends the answer back, and turn goes on from there; turn tells
  the AI what each of its agents will do before it starts and what is done as each step ends, and
  the AI passes each on to the user; turn writes the work, its reader reads it in the receiver's
  place and what has no Good is made again; turn returns the work and the result, each item's Good
  and lines; the AI checks each Good and ends.
- A CCS is said in a sentence, with ACC linked; how to write one and the result's form in full are
  for the page on calling turn, reached from Documentation.

### B-3: Why this one
- When the AI that made a work checks it, it knows what each line means and misses where a newcomer
  stops; in turn a reader that did not make it reads it with only what the receiver opens.
- Each Good comes with the lines it rests on, so it is checked by reading them.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
- A run stopped anywhere, by the user or by a conversation that ended, goes on from its last step
  when the step calls turn again with the same result, as turn keeps where it stands in a file
  beside the result (dev/architecture.md, Going on from the state).

### Installation
- turn is called from the main conversation or from an agent the main conversation starts, as its
  agents take the two layers below the caller and Claude Code starts agents down to three layers
  below the main conversation (sub-agents docs, Let subagents spawn their own subagents).
