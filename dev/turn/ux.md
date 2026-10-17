# turn UX

turn makes the work a plugin's step asks for, has it read in the place of its receiver, the one the
work is for, and returns it with each item's Good. The step's checklists list the items, each a
question the work must meet; an item's Good is what the work gives its receiver for that item.
Build and change every part of turn so that the AI calling it gets that on every run.

## Users and goals

- G1: The calling AI, the AI that runs a step of a plugin and calls turn from it, wants the work that
  step makes to come back meeting the step's checklists on every run.

  rn's conductor, the AI that runs the steps of the rn plugin, is one such AI.

## Key results

- KR1.1: The items of the checklists the calling AI fixes in the work after it comes back: none.

  An item the work meets needs no fixing, and the calling AI counts what it fixes from its own
  check, not from turn's judgment of itself.
- KR1.2: The time from calling turn to the work coming back, for a work the size of one README: three
  minutes.

  The calling AI cannot go on with its step while it waits, so the user, the person using the
  plugin, waits as long.

## Scenes

- In its step, the calling AI asks the user what the checklists' items need, and writes a CCS that
  holds what is decided, where the work goes, the checklists and the receiver.

  A CCS, the Compressed Cognitive State of [ACC](https://arxiv.org/abs/2601.11653), a method for
  long AI tasks, is the small state an AI keeps in place of the whole conversation. It is the
  calling AI's, with the names it chooses: parts, each a list of entries, each entry a kind and its
  value.
- The calling AI calls turn with the CCS's path, the kinds it uses in it for where the work goes, the
  checklists, the receiver, what the receiver reads the work for and what they open with it, and
  where turn writes its result.
- The calling AI gets back the work where it goes, and the result: each item's Good with the lines
  that give it, the questions only the user can decide, and each item still without Good, with what
  the receiver gets once it is Good.
- The calling AI checks each Good against its lines and fixes each item without Good itself; it
  puts each question to the user, writes the answer into the work, or into the CCS and calls turn
  again when the answer changes much, and ends its step.

## Benefits

- The calling AI hands turn the CCS it already keeps, as it is, since turn defines nothing of it and
  takes what it needs by the kinds it is told.
- The calling AI gets the work already read inside turn by a reader other than the one that made
  it, reading it as the receiver would, and made again where that reading found no Good, so the
  calling AI does not judge an item on its own assumption.
- Each Good comes with the lines that give it, so the calling AI checks it by reading those lines,
  not by taking it on trust.
