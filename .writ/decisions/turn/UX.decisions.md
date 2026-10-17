# turn's UX

## ux

### B-1: The users and their goals
- The AI that runs a plugin's step and calls turn from it, such as rn's conductor: the work the step
  has made comes back meeting its checklist on every run.

### B-5: The scenes to the goal
1. In its step, the AI asks the user what the checklists' items need, and writes a CCS that holds
   what is decided, where the work goes, the checklists and the receiver, who reads the work.
2. It calls turn with the CCS's path, the kinds it uses in the CCS for where the work goes, the
   checklists, the receiver, what the receiver reads it for and what they open with it, and where
   turn writes its result.
3. It gets back the work where it goes, and the result: each item's Good with the lines that give
   it, the questions only the user can decide, and each item left without Good, with what the
   receiver gets once it is Good.
4. It checks each Good against its lines and fixes each item without Good itself; it puts each
   question to the user, writes the answer into the work, or into the CCS and calls turn again when
   the answer changes much, and ends.

### B-2: Results measured, B-3: targets set high, B-4: why each
- The items of the checklist the calling AI fixes in the work after it comes back: none. Counted
  from the calling AI's own check, not from turn's judgment of itself.
- The time from calling turn to the work coming back, for a work the size of one README: three
  minutes, set high above the old turn's 4 to 12 minutes a run, since the calling AI, and the
  person, wait that long.
- Each version is judged by how close it comes to these, as an OKR's key results are.

### B-6: The benefits
- The AI hands turn the CCS it already keeps, as it is: turn defines nothing of it and takes what it
  needs by the kinds the AI names. A CCS is the state ACC (Agent Cognitive Compressor,
  https://arxiv.org/abs/2601.11653) keeps in place of the whole conversation; it is the caller's.
- The AI gets the work already read through the eyes of a reader who did not write it, and made
  again where that reading found no Good, so it does not judge an item on its own assumption.
- Each Good comes with the lines that give it, so the AI checks it by reading those lines, not by
  taking it on trust.
