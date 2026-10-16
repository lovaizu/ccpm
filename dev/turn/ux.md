# turn UX

turn is one turn of ACC, the Agent Cognitive Compressor
(https://arxiv.org/abs/2601.11653), for an AI that runs a step of a plugin: it takes a CCS, the
Compressed Cognitive State that ACC hands from one turn to the next in place of the whole
conversation, makes the work of that step meeting the step's checklist, and returns a new CCS. The
checklist is the list of items the plugin gives for that work, each a question the work must meet.
Build and change every part of turn so that this AI gets that on every run.

## Users and goals

- The calling AI, the AI that runs a step of a plugin and calls turn from it, wants the work that
  step makes to come back meeting the step's checklist on every run.

  rn's conductor, the AI that runs the steps of the rn plugin, is one such AI.

## Scenes

- In its step, the calling AI asks the person using the plugin what the checklist's items need, and
  writes down what the person decides.
- The calling AI calls turn with a CCS that points to what it wrote down and the checklist.
- The calling AI gets back the work and a new CCS, which holds, for each item of the checklist,
  whether the work meets it and the lines of the work that meet it, what to do next and what is not
  settled.
- The calling AI checks each of these answers against the work, those that say an item is met as
  well as those that say it is not, fixes the work itself, and ends its step.

## Benefits

- The calling AI goes on from the new CCS turn returns, carrying the CCS alone instead of the whole
  conversation, so however many steps it goes through, what it holds does not swell and it does not
  drift from its goal.
- The calling AI gets the work already read inside turn by a reader other than the one that made
  it, reading it as the work's own readers would, and made again where that reading found it short
  of an item, so the calling AI does not judge an item met on its own assumption.
