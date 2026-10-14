# Changelog

## [Unreleased]

### Changed

- turn asks nothing while it works: what only you can decide is left out of the work and asked, with every other such question, when the run ends — you can leave turn at work and answer everything at once, and no stop message shows while it waits for the AIs that write, read and check the work. Called again with your answers, turn starts from the work it returned and writes over it without your committing it first, unless you changed it since.
- turn takes its second pass only when the first leaves something the work itself can give and nothing for you or the calling step to decide, and returns what the second still leaves with how it would be given — no pass is spent on a work that waits on your answer, and Claude, or your plugin's step, which knows what you agreed, decides whether to run again.
- The console shows only each step, not the paths of turn's own files — you follow the run without learning how turn keeps it.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
