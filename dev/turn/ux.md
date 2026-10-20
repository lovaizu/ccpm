# turn UX

turn makes the work a plugin's step asks for and returns it with each item of the step's checklists
judged by a reader that did not make it. Build and change every part of turn so that the AI calling
it gets that on every run.

## Users and goals

- G1: The calling AI, the AI that runs a step of a plugin and calls turn from it, wants the work that
  step makes to come back meeting the step's checklists on every run.

  A checklist lists what the receiver, the one the work is for, should get from the work, one item
  each, asked as a question. rn's conductor, the AI that runs the steps of the rn plugin, is one
  such calling AI.

## Key results

They stand from the highest priority: time is never saved by leaving the calling AI more to fix,
since a work it must fix costs the user the fixing as well as the wait.

- KR1.1: The items of the work the calling AI is not satisfied by when it comes back, each judged by
  whether the calling AI can tell it and fix it at once or it would go on unseen to whoever reads
  the work; fewer is better, and none once the goal is reached.

  What the calling AI tells and fixes at once costs the user a moment, while what goes on unseen
  reaches whoever reads the work; the calling AI judges each from its own check, not from turn's
  judgment of itself.
- KR1.2: The time from calling turn to the work coming back, for a work the size of one README;
  shorter is better.

  The calling AI cannot go on with its step while it waits, so the user, the person using the
  plugin, waits as long.

## Scenes

- In its step, the calling AI asks the user what the checklists' items need, and writes a CCS that
  holds what is decided, where the work goes, the checklists and the receiver.

  A CCS is the JSON file in which the calling AI keeps its task, in the shape
  [ACC](https://arxiv.org/abs/2601.11653) gives it: parts, each a list of entries, each entry a kind
  and its value, every name the calling AI's own.
- The calling AI calls turn with the CCS's path, the kinds it uses in it for where the work goes, the
  checklists, the receiver, what the receiver reads the work for and what they have with it, and
  where turn writes its result.
- While turn runs, the calling AI is told by each of turn's agents, before it starts its work, what
  it will do, how far and how, and as each step ends, what is done and what comes next; it passes
  each on to the user, who may stop the run there.

  A run going a slow or wrong way shows before its time is spent, not after the work comes back.
- The calling AI gets back the work where it goes, and the result: each item's Good with its lines,
  the questions only the user can decide, each item still without Good, with what the receiver
  gets once it is Good and where it was not found, and the lessons turn took on how its run went, to hand on to turn's makers. Where the CCS cannot give an item its Good, it gets the questions alone,
  before any work is made.

  An item's Good is the judgment that the receiver gets from the work what the item asks, with the
  lines that give it.
- The calling AI checks each Good against its lines and fixes each item without Good itself; it
  puts each question to the user, writes the answer into the work, or into the CCS and calls turn
  again when no work came back or the answer changes much, and ends its step.

## Benefits

- The calling AI gets the work already read by a reader that did not make it, in the receiver's
  place, and made again where that reading found no Good, so it does not judge an item on its own
  assumption.
- Each Good comes with the lines it rests on, so the calling AI checks it by reading those lines.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
