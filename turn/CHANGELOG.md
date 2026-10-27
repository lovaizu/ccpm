# Changelog

## [Unreleased]

### Added

- Before the AI that makes the work writes anything, it sends your step what your CCS and its files leave open that only the user can decide, each question with the items it settles and the answer it recommends, settling every other point itself and naming it with why in the result, and goes on once your step has kept the answer in its CCS and sent it back — the user is asked once, and only what is theirs, instead of a work made on a guess.
- Each checklist item says where it is answered, `Scope: its part`, `each part` or `whole`, and an item asked of each part gets its Good only where every section or file gives it — a part that falls short is not passed because another part gives the item.
- The AI reading in the receiver's place has what the CCS says the receiver has, such as the whole repository, and does what they do with the work, such as running its tests — a Good that holds only on paper, or one the receiver gets from what lies beside the work, is told apart.
- The AI that makes the work runs what it gives as the receiver would, such as the commands it tells and its tests — a work that fails on first use is made again before it reaches you.
- Your call names `test`, the one command that checks the work, such as `make check`, or `null` where it has none, and the AI that makes the work passes it after its last change before it ends — a work that fails your own check does not come back to you.
- The result names every item's Good with the lines that give it — you check each Good by reading its lines.
- The result names each choice the AI that made the work took on its own, one your CCS and its files leave open, with why — your step can show its user what was decided without asking them.
- Each AI of a run is held to its step by lane's hooks: it reads only what it is given, a role writes only the work or its reply, the AI reading in the receiver's place answers every item of your checklists, and the AIs that make, read and pass on the work run no `git commit` or `git push`; one that drifts is told its step again and goes back to it — the work rests on what you decided, and the rest of your repository stays as you left it.
- A work can be several files that serve one purpose, such as code and its tests — turn makes, reads and checks them together.
- A work already at its paths is changed from what is there, not written again from nothing — what already serves its reader stays as it is.
- Several runs go at once, each kept apart — your plugin can have several works made at the same time.
- turn tells the main conversation as each of its AIs starts what it will do and as each ends what is done, and when it asks and when the result is back, each line within the move it goes with, waiting for each AI's end itself — a run going a slow or wrong way shows while it can still be stopped, and telling it costs the run no moves of its own.
- A run stopped anywhere, by you or by a conversation that ended, goes on from its last move when your step calls turn again with the same call — no work already done is done again.
- [Calling turn](docs/calling.md) gives the checklist's form, the CCS, the call, the questions and the result in full — your step's text can be written from it without reading turn's code.

### Changed

- Each of turn's agents reads its steps whole, from its own file under `prompts/`, before it does anything else, held there by lane's hooks, its entry saying where each script and form its steps name lies — every run of an agent works from all of its steps, wherever Claude Code installs turn.
- turn is called from your plugin's step: started in the background with `{"ccs", "kind", "result", "test"}`, the CCS your step's own JSON file and every name in it yours, turn taking what it needs by the kinds you name — your step keeps its task in its own shape, and its context holds only what comes back.
- The call names, besides where the work goes, the checklists and the receiver, what the receiver uses the work for and what they have with it, such as the whole repository — the AI reading in the receiver's place stands where they stand, and a Good it finds holds for them.
- The work is made where it goes, and a run cut off leaves its writing as changes git shows — you see what it wrote before you call again.
- While a run goes, where it stands and each AI's reply are kept in `.turn/<yyyymmdd>-<name>/` at the top of your repository, the day it began and the result's path, each removed once the run returns — the folder beside your result holds the result alone, a run stopped goes on however many days later, and one line of your `.gitignore` decides whether git keeps a run stopped partway.
- Where the AI reading in the receiver's place finds no Good, it says where it stopped, what it did there, what it did not get and how that keeps the receiver from using the work, and sends back only such a gap, leaving what a formatter, a linter or a type checker shows to them; the AI that made the work mends each gap or says why it lies outside the purpose, the reader holds it or lets it go given that reason, and a gap the two still differ on comes to your step at once as a question of the purpose; a gap mended and still found is made again, up to three times a round and two rounds, after which an item still without Good comes to your step as a question — each remake changes only what keeps the receiver from using the work, and a gap seen wrong is settled by its reason, not by another round of making.
- What an item's `Tried by` line says is run, where it has one, is run alike by the AI that makes the work and the AI that reads it, and the maker checks each item with its evidence, the command it ran and what it printed or the lines, in short, giving again on a remake only the items sent back — maker and reader see the same, and a run spends nothing on a claim no one reads.

### Fixed

- A run moves on from each of its AIs, and returns, only once that AI has ended — no AI still finishing its reply leaves a file of a run already gone in your repository.
- A run started by an agent, as rn starts turn, goes on once each AI it sent more work has ended — it no longer waits on a notice Claude Code gives the main conversation alone, ending without its result.
- Each AI of a run writes its reply to a file turn reads, and a reply out of its form is sent back to it with what to fill — no reply passes unchecked, however Claude Code ends an agent.
- A `cd` in your conversation while a run goes no longer stalls it: each path of the call keeps meaning the folder the call was made from, and each AI of the run is given its files as whole paths — the run reads and writes where you called it, wherever your conversation moves.
- A folder your CCS names with a trailing slash, such as `docs/`, is taken as the folder — the AIs of a run can read the files inside it instead of being stopped at each.

### Removed

- Asking in a conversation, the console view of each step, and the work and readings of each round kept in `.turn/` — what turn returns is the result file your step reads.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
