# Changelog

## [Unreleased]

### Added

- A checklist's item IDs may be `A1` as well as `A-1` — a verification document whose scenes are `### A1:` headings is read as a checklist, so a product is used against the same document its user approved.
- A work can be several files that serve one purpose, such as code and its tests, each named as a `deliverable` — turn writes, reads and checks them together, so what the receiver needs only from them together is checked as one.

### Changed

- The work reaches where it goes only when the run returns — a run stopped or cut off leaves your files as they were.
- The work is made in a copy of the repository as it is committed, kept under `.turn/` while the run goes — the tests and builds the work needs run there as they would in place, and nothing has to be copied beside the work for them.
- A change to the work after it has been handed to the reader is stopped — the version read is the version you get back.
- Each stop turn's hooks make names the step it concerns and why — you and Claude see at once what went wrong and what that step needs.
- The CCS names each input by what it is for: `checklist`, `decisions` (what you decided the work must say or do, and leave out), `reference` (what it follows or draws on, which turn reads in place of a copy) and `receiver_opens` (what the receiver opens with it); `viewpoint`, `answer` and `difference` of 0.1.0 are gone, and turn returns the rules it learns in its own part instead of adding them to your constraints — your plugin's step says what each file is for once, and nothing it did not ask piles up across calls.
- turn and each agent it starts read only the files the CCS names, turn's own files and their own commands' output; a read outside them is stopped — the work follows what you decided, not whatever turn happened to open.
- turn asks nothing while it works: what only you can decide is left out of the work and asked, with every other such question, when the run ends — you can leave turn at work and answer everything at once, and no stop message shows while it waits for the AIs that write, read and check the work. Called again with your answers, turn starts from the work it returned and writes over it without your committing it first, unless you changed it since.
- turn takes a second pass only when the first leaves something the work itself can give, and returns what the second still leaves with how it would be given, with your questions — Claude, or your plugin's step, which knows what you agreed, decides whether to run again.
- The console shows only each step, not the paths of turn's own files — you follow the run without learning how turn keeps it.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
