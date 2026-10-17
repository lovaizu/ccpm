# turn's UX

## ux

### B-1: The users and their goals
- The AI that runs a plugin's step and calls turn from it, such as rn's conductor: the work the step
  has made comes back meeting its checklist on every run.

### B-5: The scenes to the goal
1. In its step, the AI asks the user what the checklist's items need, and writes down what is
   decided.
2. It calls turn with a CCS that points to what it wrote down and the checklist.
3. It gets back the work and a new CCS, holding for each item of the checklist whether it is met and
   the lines that meet it, what to do next and what is not settled.
4. It checks against the work both the items met and those not met, fixes the work itself, and
   ends.

### B-2: Results measured, B-3: targets set high, B-4: why each
- The items of the checklist the calling AI fixes in the work after it comes back: none. Counted
  from the calling AI's own check, not from turn's judgment of itself.
- The time from calling turn to the work coming back, for a work the size of one README: three
  minutes, set high above the old turn's 4 to 12 minutes a run, since the calling AI, and the
  person, wait that long.
- Each version is judged by how close it comes to these, as an OKR's key results are.

### B-6: The benefits
- turn is a turn of ACC (Agent Cognitive Compressor, https://arxiv.org/abs/2601.11653): the AI
  hands it a CCS and gets a new CCS back. That what the AI holds does not swell and it does not
  drift shows only over many turns, so it is the caller's benefit (rn's), not turn's; the CCS is
  turn's input and output.
- The AI gets the work already read through the eyes of a reader who did not write it, and made
  again where that reading found it short, so it does not judge an item met on its own assumption.
