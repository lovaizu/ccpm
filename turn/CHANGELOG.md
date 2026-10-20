# Changelog

## [Unreleased]

### Added

- Before any work is made, turn checks that what your CCS and its files say can give every item its Good, and where it cannot, returns the questions alone, each with the items it settles and the answer it recommends — you ask the user once and call again, instead of a work made on a guess.
- Each checklist item says where it is answered, `Scope: its part`, `each part` or `whole`, and an item asked of each part gets its Good only where every section or file gives it — a part that falls short is not passed because another part gives the item.
- The AI reading in the receiver's place has what the CCS says the receiver has, such as the whole repository, and does what they do with the work, such as running its tests — a Good that holds only on paper, or one the receiver gets from what lies beside the work, is told apart.
- The AI that makes the work runs what it gives as the receiver would, such as the commands it tells and its tests — a work that fails on first use is made again before it reaches you.
- The result names, for every item, its Good with the lines that give it, the question it waits on, or what the receiver gets once it has it and where it was not found, and the lessons turn took on how its own run went — you check each Good by reading its lines, and hand the lessons on to turn's makers.
- Each AI of a run reads only what your CCS gives it and writes nothing but the work, its shell commands included — the work rests on what you decided, and the rest of your repository stays as you left it.
- A work can be several files that serve one purpose, such as code and its tests — turn makes, reads and checks them together.
- A work already at its paths is changed from what is there, not written again from nothing — what already serves its reader stays as it is.
- Several runs go at once, each kept apart — your plugin can have several works made at the same time.
- Each AI of a run tells your step, before it starts, what it will do, how far and how, and as each step ends, what is done and what comes next — a run going a slow or wrong way shows while it can still be stopped, not after its time is spent.

### Changed

- turn is called from your plugin's step: started in the background with `{"ccs", "kind", "result"}`, the CCS your step's own JSON file and every name in it yours, turn taking what it needs by the kinds you name — your step keeps its task in its own shape, and its context holds only what comes back.
- The call names, besides where the work goes, the checklists and the receiver, what the receiver uses the work for and what they have with it, such as the whole repository, and turn first checks that what they have lets its reader do what they do with the work, returning the questions alone where something is lacking — the AI reading in the receiver's place stands where they stand, and a Good it finds holds for them.
- The work is made where it goes, and a run cut off leaves its writing as changes git shows — you undo or finish them and call again.
- Where the AI reading in the receiver's place finds no Good, the work is made again aimed at where it stopped, what it did there and what it did not get, with no other reading between, up to three times a round and two rounds — each remake changes only what fell short, and a run that does not settle ends.

### Fixed

- turn checks each AI's reply as it hands it back, on Claude Code that ends an agent that way, as well as on one that ends it on its last message — a reply out of its form, or the orchestrator ending before its run returned, is sent back instead of passing unchecked and leaving the run unfinished.
- A folder your CCS names with a trailing slash, such as `docs/`, is taken as the folder — the AIs of a run can read the files inside it instead of being stopped at each.

### Removed

- Asking in a conversation, the console view of each step, the questions asked while the work goes on, and the `.turn/` folder — what turn returns is the result file your step reads.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
