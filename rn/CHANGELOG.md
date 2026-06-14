# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `/rn:gm` now restates your goal in its own words and opens a draft PR with the full plan — you can review and correct the direction before any work starts.
- Every task now passes an adversarial review before it is committed — finished work clears a tougher quality bar instead of being taken at face value.

### Changed

- `steering.md` is easier to review: flat sections, with a clear **Acceptance criteria** (was "Verification") that states when the goal is done and what is in or out of scope.

## [0.1.0] - 2026-06-13

### Added

- Initial release — goal-driven work sessions with `/rn:gm` (start), `/rn:bb` (step away), and `/rn:hi` (resume), so one goal carries across conversations without losing the thread.
