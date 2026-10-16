# What turn's README says

The README is read by people deciding whether to use turn, so it speaks to anyone who has AI make
documents or code; its example is the UX's scene, a plugin's step calling turn.

## readme

### B-2: Who it is for
- Anyone who has AI make documents, code and the like.

### B-1: What they gain
- Each call is one turn of ACC (https://arxiv.org/abs/2601.11653): a step hands turn a CCS and goes
  on from the new CCS turn returns, instead of the whole conversation.
- turn is a Claude Code plugin: what it makes comes back meeting your checklist, since a reader that
  did not make it reads it in the place of the person it is for, and what falls short is made again
  before it comes back.

### B-4: Using it on their own work
- The example is a small plugin of the reader's own kind with a step that writes a README: in it the
  AI asks the user, one point at a time, what the checklist's items need, writes down what is
  decided, calls turn, gets back the work with each item's judgment and the lines that meet it,
  checks those against the work, fixes it and ends.
- It shows, from start to result: the step's text that calls turn with a CCS, kept short, and the
  CCS's parts that say the task (what is made, who reads it and for what, the checklists and
  decisions, the rules such as the language), those that say how the task stands after a turn
  empty since no turn has run, their writing left to the callers' page; that while the step waits, a reader other than the one that made the
  work reads it in its receiver's place and what falls short is made again, which the person sees
  in the panel below the prompt input; and the CCS that comes back, with what to do next, each
  item's judgment and lines and the questions for the user, then the AI checking, fixing and
  ending the step.

### B-3: Why this one
- turn is a turn of ACC: the plugin's AI carries only the CCS from step to step, so what it holds
  does not swell and it does not drift from its goal, where carrying the whole conversation piles up.
- When the AI that made a work checks it, it knows what each line means and misses where a newcomer
  stops; in turn a reader that did not make it reads it with only what the person it is for opens.
- turn makes the work from the decisions and checklists it is given alone and opens nothing else, so
  the work does not stray from what was decided.
- An item counts as met only where lines of the work give it, and those lines are named, so a
  judgment can be checked instead of taken on trust.
- What falls short is made again from what the work should give, not patched where it showed, and
  every item already met stays met.
