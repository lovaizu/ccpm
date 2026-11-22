# Changelog

## [Unreleased]

### Changed

- Your `check` fails the step only where it exits 1. Any other code, such as 2 where it can't read what it checks, says it couldn't check, so a check tells a step left short apart from one it couldn't judge.

### Fixed

- Where Lane can't check a move, such as when your adapter fails because the run's folder is gone, your `lane/rules.json` breaks its form, a `check` couldn't check, a checklist command fails, or a file to read whole is gone, it lets the move through and tells the AI what it couldn't check and why, instead of stopping it, so a conversation never loops on a stop that no one in it can mend.

## [0.1.0] - 2026-11-22

### Added

- Lane holds each role of your plugin to the steps that your `lane/rules.json` gives it: a call that leaves its step is stopped with the step's own sentence, so the AI notices at once and goes back, with no one watching each move.
- Lane starts each subagent that your routes make due after a result, stops any other start, and keeps the main conversation from ending its turn while one is due, so a run goes on in the order you meant.
