# turn's UX

## ux

### B-1: The users and their goals
- The AI that runs a plugin's step and calls turn from it, such as rn's orchestrator: the work the step
  has made comes back meeting its checklists on every run.

### B-12: Every term known
- A checklist lists what the receiver, the one the work is for, should get from the work, one item
  each, asked as a question.
- An item's Good is the judgment that the receiver gets from the work what the item asks, with the
  lines that give it.

### B-5: The scenes to the goal
1. In its step, the AI asks the user what the checklists' items need, and writes a CCS that holds
   what is decided, where the work goes, the checklists and the receiver.
2. It calls turn with the CCS's path, the kinds it uses in the CCS for where the work goes, the
   checklists, the receiver, what the receiver reads it for and what they open with it, and where
   turn writes its result.
3. While turn runs, it is told by turn what each agent will do before it starts and what is done
   as each step ends, and passes each on to the user, who may stop the run there.
4. Where the CCS lacks what the run needs, or the work meets a point only the user can decide, turn
   sends it the question by message before the work resting on it is made; it puts the question to
   the user and sends the answer, and turn goes on from there (dev/architecture.md, Messages; A
   plugin that uses another).
5. It gets back the work where it goes, and the result: each item's Good with its lines, and the
   lessons from the run; an item still without Good has come to it as a question before.
6. It checks each Good against its lines, puts each lesson to the user, and ends.
7. A run stopped anywhere goes on from its last step when it calls turn again with the same result
   (dev/architecture.md, Where the course is kept).

### B-2: Results measured, B-4: why each, B-7: the order of priority
- The items of the checklists the calling AI judges the work, when it comes back, to meet; more is
  better. Counted from the calling AI's own check, not from turn's judgment of itself.
- The time from calling turn to the work coming back, for a work the size of one README; shorter is
  better, since the calling AI, and the person, wait that long.
- In that order: time is never saved by leaving the calling AI more to fix.
- Each version is judged against the version in use on the same task, with no target value.

### B-6: The benefits
- The AI gets the work already read through the eyes of a reader who did not make it, in the
  receiver's place, and made again where that reading found no Good, so it does not judge an item
  on its own assumption.
- Each Good comes with the lines it rests on, so the AI checks it by reading those lines.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
