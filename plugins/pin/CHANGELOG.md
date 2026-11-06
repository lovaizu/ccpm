# Changelog

## [Unreleased]

### Added

- `/pin:down` with your plan in your own words settles every point the plan needs from its goal down, in a design tree, `.pin/<yyyymmdd>-<name>/design-tree.md` — the AI that makes the work reads the design from the file, with nothing left to guess.
- Pin finds each fact itself with Read and Grep and shows it to you to confirm, settles each decision that the goal and the facts favor, and asks you a decision only where two ways serve the goal equally or it is hard to undo, with a recommendation that "yes" takes — your answers go only to what is yours.
- Each message from Pin holds one point, and a decision comes only once the decisions it builds on are settled — one answer can still change the next, and none changes another unseen.
- Before it ends, Pin shows you the whole design, each point in one short line with who settled it, and asks whether you and it mean the same — a point held otherwise than you mean shows before the work starts, not in it.
- Every answer is in the design tree before the next point goes out, and `/pin:down` on the same plan goes on from the file in `.pin/` — a stopped conversation loses no answer and asks nothing again.
- Your AI can write the goal, the questions and the points it settled with you into a design tree, each marked `(maker)`, and call the skill with its path — Pin keeps those points as given and asks you only the rest.
- Your main conversation carries each point to you and your answer back word for word, held by Lane's hooks to start the pinner, wait for it and put its point to you — no AI between you and Pin rewords a question or sums up an answer.
- The pinner writes only the design tree, changes it only with Read and Edit, and has `check.py` check it after each change, held by Lane's hooks — the design never ends with a question nothing serves or a decision that serves nothing.
