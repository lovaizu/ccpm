# turn UX

turn makes the work a plugin's step asks for, has it read in its receiver's place, and returns it
with the Good each item of the step's checklist finds in it. The checklist is the list of items the
plugin gives for that work, each a question the work must meet; an item's Good is what the work
gives its receiver for that item. Build and change every part of turn so that the AI calling it
gets that on every run.

## Users and goals

- G1: The calling AI, the AI that runs a step of a plugin and calls turn from it, wants the work that
  step makes to come back meeting the step's checklist on every run.

  rn's conductor, the AI that runs the steps of the rn plugin, is one such AI.

## Key results

- KR1.1: The items of the checklist the calling AI fixes in the work after it comes back: none.

  An item the work meets needs no fixing, and the calling AI counts what it fixes from its own
  check, not from turn's judgment of itself.
- KR1.2: The time from calling turn to the work coming back, for a work the size of one README: three
  minutes.

  The calling AI cannot go on with its step while it waits, so the person using the plugin waits
  as long.

## Scenes

- In its step, the calling AI asks the person using the plugin what the checklist's items need, and
  writes a CCS that holds what is decided, the work, the checklists and who reads the work.

  A CCS, the Compressed Cognitive State of [ACC](https://arxiv.org/abs/2601.11653), is the small
  state an AI keeps in place of the whole conversation; it is the calling AI's, in the shape it
  chooses: parts, each a list of entries, each entry a kind and its value.
- The calling AI calls turn with the CCS's path, the kinds it uses in it for the work, the
  checklists, who reads the work, what they read it for and what they open with it, and where turn
  writes its result.
- The calling AI gets back the work where it goes, and the result: each item's Good with the lines
  that give it, the questions only the person can decide, and each item left without Good, with what
  the receiver gets once it is Good.
- The calling AI checks each Good against its lines, fixes the work itself where it falls short, and
  ends its step.

## Benefits

- The calling AI hands turn the CCS it already keeps, as it is, since turn defines nothing of it and
  takes what it needs by the kinds it is told.
- The calling AI gets the work already read inside turn by a reader other than the one that made
  it, reading it as the work's own readers would, and made again where that reading found no Good,
  so the calling AI does not judge an item on its own assumption.
- Each Good comes with the lines that give it, so the calling AI checks it by reading those lines,
  not by taking it on trust.
