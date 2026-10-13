# Changelog

## [Unreleased]

### Fixed

- While a run waits for the AI that reads or checks the work, it is no longer told to end the run — the run waits for the reading and the check instead of ending without them, and no stop message shows while it waits.

## [0.1.0] - 2026-10-13

### Added

- `turn:up` lets Claude Code make any work, such as a document, a prompt or code, that passes your checklist, asked in a conversation or from a plugin's step — another AI reads it as the one it is for and what does not pass yet is made again, so you hand it on without first reading it as its receiver, and are asked only what you alone can answer.
