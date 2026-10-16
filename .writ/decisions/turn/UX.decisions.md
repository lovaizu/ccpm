# turn's UX

## ux

### B-1: The users and their goals
- The AI that runs a plugin's step and calls turn from it, such as rn's conductor: the work the step
  has made comes back meeting its checklist on every run.

### B-2: The scenes to the goal
1. In its step, the AI asks the user what the checklist's items need, and writes down what is
   decided.
2. It calls turn with a CCS that points to what it wrote down and the checklist.
3. It gets back the work and a new CCS, holding for each item of the checklist whether it is met and
   the lines that meet it, what to do next and what is not settled.
4. It checks against the work both the items met and those not met, fixes the work itself, and
   ends.

### B-3: The benefits
- turn is a turn of ACC (Agent Cognitive Compressor, https://arxiv.org/abs/2601.11653): the AI
  hands it a CCS and goes on from the new CCS it returns, carrying the CCS alone instead of the
  whole conversation, so however many steps it goes through, what it holds does not swell and it
  does not drift from its goal.
- The AI gets the work already read through the eyes of a reader who did not write it, and made
  again where that reading found it short, so it does not judge an item met on its own assumption.
