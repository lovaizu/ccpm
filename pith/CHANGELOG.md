# Changelog

All notable changes to pith are recorded here, in the format of [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

### Added

- pith is a plugin of its own, and `/writ:pith` is now `/pith:up` — you can check any work by use without installing a plugin for writing documents, and writ and rn check through the same place.
- Essentials for a Claude Code plugin (`plugin.md`): the plugin's README story is run end to end, and what the user waited, read and was asked is set beside what they got — a plugin is judged by what it costs its user, not only by each part working.
- The essentials for a prompt also ask what differs without the prompt or with the version in use, and on each model it runs on — a prompt is kept only for what it adds.

### Changed

- The short result holds only pith's view and each More in full; every Good stays in the result file — what you read grows with what you decide, not with the number of questions.
- You settle a result file yourself, and pith's hook checks its form on every write — finishing a check no longer starts another run of pith.

### Fixed

- A first user may read its own long command output that Claude Code saved for it — it is no longer stopped as if it were reading how the work was made.
