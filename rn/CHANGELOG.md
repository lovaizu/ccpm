# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `/rn:gm` restates your goal in its own words and opens a draft PR with the full plan, so you can review and fix the direction before any work starts.
- Each task is now checked by a reviewer that deliberately looks for problems before the work is committed, so mistakes are caught early instead of after the fact.

### Changed

- The plan in `steering.md` is clearer to review on the PR: a single **Acceptance criteria** section (previously "Verification") spells out when the goal is done and what is in or out of scope.

## [0.1.0] - 2026-06-13

### Added

- Initial release — goal-driven work sessions with `/rn:gm` (start), `/rn:bb` (step away), and `/rn:hi` (resume), so one goal carries across conversations without losing the thread.
