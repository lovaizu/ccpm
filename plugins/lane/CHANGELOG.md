# Changelog

## [0.1.0] - 2026-11-22

### Added

- Lane holds each role of your plugin to the steps that your `lane/rules.json` gives it: a call that leaves its step is stopped with the step's own sentence, so the AI notices at once and goes back, with no one watching each move.
- Lane starts each subagent that your routes make due after a result, stops any other start, and keeps the main conversation from ending its turn while one is due, so a run goes on in the order you meant.
