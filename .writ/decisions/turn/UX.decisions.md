# turn's UX

## ux

### B-1: The users and their goals
- The AI that runs a plugin's step and calls turn from it, such as rn's conductor: the work the step
  has made comes back meeting its checklist on every run.

### B-2: The scenes to the goal
1. In its step, the AI asks the user what the checklist's items need, and writes down what is
   decided.
2. It calls turn with what it wrote down and the checklist.
3. It gets back the work and, for each item of the checklist, whether it is met and the lines that
   meet it.
4. It checks against the work both the items met and those not met, fixes the work itself, and
   ends.
