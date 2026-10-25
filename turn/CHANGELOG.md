# Changelog

## [Unreleased]

### Added

- Before any work is made, turn checks that what your CCS and its files say can give every item its Good, and where it cannot, sends your step the questions, each with the items it settles and the answer it recommends, and goes on once your step has kept the answer in its CCS and sent it back — you ask the user once, instead of a work made on a guess.
- Each checklist item says where it is answered, `Scope: its part`, `each part` or `whole`, and an item asked of each part gets its Good only where every section or file gives it — a part that falls short is not passed because another part gives the item.
- The AI reading in the receiver's place has what the CCS says the receiver has, such as the whole repository, and does what they do with the work, such as running its tests — a Good that holds only on paper, or one the receiver gets from what lies beside the work, is told apart.
- The AI that makes the work runs what it gives as the receiver would, such as the commands it tells and its tests — a work that fails on first use is made again before it reaches you.
- Your call names `test`, the one command that checks the work, such as `make check`, or `null` where it has none, and the AI that makes the work passes it after its last change before it ends — a work that fails your own check does not come back to you.
- The result names every item's Good with the lines that give it, and the lessons turn took on how its own run went — you check each Good by reading its lines, and hand the lessons on to turn's makers.
- Each AI of a run is held to its step by lane's hooks: it reads only what it is given, a role writes only the work or its reply, the AI reading in the receiver's place answers every item of your checklists, and the AIs that make, read and pass on the work run no `git commit` or `git push`; one that drifts is told its step again and goes back to it — the work rests on what you decided, and the rest of your repository stays as you left it.
- A work can be several files that serve one purpose, such as code and its tests — turn makes, reads and checks them together.
- A work already at its paths is changed from what is there, not written again from nothing — what already serves its reader stays as it is.
- Several runs go at once, each kept apart — your plugin can have several works made at the same time.
- turn tells the main conversation, before each move of the run, its own moves among them, what was done and what the move will do, how far and how — a run going a slow or wrong way shows while it can still be stopped, not after its time is spent.
- A run stopped anywhere, by you or by a conversation that ended, goes on from its last move when your step calls turn again with the same call — no work already done is done again.

### Changed

- turn is called from your plugin's step: started in the background with `{"ccs", "kind", "result", "test"}`, the CCS your step's own JSON file and every name in it yours, turn taking what it needs by the kinds you name — your step keeps its task in its own shape, and its context holds only what comes back.
- The call names, besides where the work goes, the checklists and the receiver, what the receiver uses the work for and what they have with it, such as the whole repository, and turn first checks that what they have lets its reader do what they do with the work, returning the questions alone where something is lacking — the AI reading in the receiver's place stands where they stand, and a Good it finds holds for them.
- The work is made where it goes, and a run cut off leaves its writing as changes git shows — you see what it wrote before you call again.
- While a run goes, where it stands and each AI's reply are kept in `.turn/<yyyymmdd>-<name>/` at the top of your repository, the day it began and the result's path, with the records the learner reads, each removed once the run returns — the folder beside your result holds the result alone, a run stopped goes on however many days later, and one line of your `.gitignore` decides whether git keeps a run stopped partway.
- Where the AI reading in the receiver's place finds no Good, the work is made again aimed at where it stopped, what it did there and what it did not get, with no other reading between, up to three times a round and two rounds, after which an item still without Good comes to your step as a question — each remake changes only what fell short, and a run that does not settle asks you rather than going on.

### Fixed

- Each AI of a run writes its reply to a file turn reads, and a reply out of its form is sent back to it with what to fill — no reply passes unchecked, however Claude Code ends an agent.
- A `cd` in your conversation while a run goes no longer stalls it: each path of the call keeps meaning the folder the call was made from, and each AI of the run is given its files as whole paths — the run reads and writes where you called it, wherever your conversation moves.
- A folder your CCS names with a trailing slash, such as `docs/`, is taken as the folder — the AIs of a run can read the files inside it instead of being stopped at each.

### Removed

- Asking in a conversation, the console view of each step, and the work and readings of each round kept in `.turn/` — what turn returns is the result file your step reads.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
