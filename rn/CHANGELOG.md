# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version goes up by what changes for you: the middle number for anything you would notice, the
last for fixes that change nothing you do.

## [0.9.0] - 2026-10-03

### Added

- `rn` asks why you want the goal and finds what you really want behind your first words, one point at a time with the answer it recommends, so what you get is what you meant.
- Acceptance criteria come in two kinds, what would make you choose the result and what you take for granted, each with an ID, and the effort goes to the first kind first, so the reason you wanted the work is checked while there is still time to change course.
- At the Design sign-off you also approve a verification document: for each criterion, how the product will be used as you would use it and what must happen then, so you know before anything is built how you will see that it works, and the same check can be run again after any later change.
- Before you see a result, an agent that knows nothing of how it was made uses it as you would and says what it understood and what happened, so a result passes because it does its job, not because its maker says so.
- Installing `rn` also installs `writ`, which writes your README, design document, and verification document, so what you settle reads well to whoever picks it up.
- `rn` checks its own record as it goes, so a decision not pushed, a sign-off passed without your `/rn:ty`, or a finding left out of the record is stopped where it happens. These checks need Python 3.9 or later.

### Changed

- Every sign-off comes with what `rn` proposes to do next and why, and under each question what is good and what falls short, with where, so you can say yes or no without re-reading the work.
- Every proposal says first how close the work has come to each thing you would choose it for, and what came closer since the last one, so you decide when it is close enough instead of waiting for every shortfall to be cleared.
- `rn` spends its checks and fixes on what you would choose the work for: it checks that with the fewest uses that show it, the way you would use the product, and fixes first what brings it closer; small gaps off that path are neither chased nor put before you, so you get what you came for sooner.
- There is always a Design sign-off, and the tasks are planned only after it, so they follow what you agreed there instead of being rewritten.
- Plain `/rn:gm` takes every comment you wrote on the pull request since `rn` stopped for the sign-off, so you can give feedback where you read.
- A session started under an earlier `rn` has its goal worked out again with you from its old record when you run `/rn:up`, and stops at a new Plan sign-off, so every later decision is judged by why you want the goal.

### Removed

- `rn` no longer replies to your review threads on the pull request, and `/rn:dn` no longer asks about untracked files; your comments are taken whole as feedback, and a pause commits only what the task changed.

## [0.8.0] - 2026-07-07

### Added

- Every session now records which version of `rn` it started under, and each command checks that against the installed version on every run — on a mismatch, it reconciles the session's plan, design, and remaining tasks to the current conventions automatically before continuing, so older sessions keep working correctly as `rn` itself evolves, with nothing extra for you to do.

### Changed

- Writing or updating a session's `design.md` now requires an explicit decision and the reasoning behind it for every question the design template raises — a section can no longer be left blank or silently skipped — so the resulting design doc always shows what was decided and why, not just what was ultimately built.
- Starting a session no longer always creates a brand-new `design.md`: if an existing one already covers the work's area, the assistant now points at it and walks through an update instead of authoring from scratch, so related work accumulates in one design doc instead of spawning duplicates.

## [0.7.0] - 2026-07-05

### Added

- `/rn:ty` (approve) and `/rn:gm` (revise) give you one accept/revise vocabulary at every gate and confirmation point — plan, design, evaluation, or any reviewed result — so you always know how to respond and the assistant never has to guess your intent from prose.
- `/rn:gm` with no argument now works through your PR's unresolved review threads one at a time — addressing each and replying with the fix, or asking a question when the ask is unclear — and leaves resolving each thread to you on GitHub, so review feedback gets handled systematically without anything getting closed out from under you.
- Once a session is underway, every message that stops for your input opens with a compact session map — ✅ done / 👉 now / ⬜ ahead, plus what's being asked — so you can answer on the spot without opening `steering.md` to see where things stand.

### Changed

- Session directories now carry a date prefix — `.rn/{yyyymmdd}-{slug}/` (e.g. `.rn/20260702-payment-fix/`) — so as sessions accumulate under `.rn/`, a directory listing reads in chronological order.
- You now sign off at three points — the plan up front, the approach when it needs a separate look, and the result at the end — instead of approving every task; in between, the assistant works through the tasks and has them checked behind the scenes, and only interrupts you mid-flight when a call is genuinely yours — so you get fewer interruptions while keeping the say on the moments that matter.
- Completion criteria in a plan are now written as two questions anyone can answer with evidence — is the goal actually achieved, and are new problems absent — so a criterion can't pass just because some file was produced.
- `steering.md` stays a lean plan for the remaining work: design intent and decisions now live in a separate `design.md` it points to, finished-task detail and deliberation stay in git and the PR, and a pause records only a short forward pointer — so the plan never piles up across pause/resume cycles.

### Fixed

- `/rn:dn` (pause) now finishes with a genuinely clean worktree — leftover test/build files are git-ignored so they stop keeping the tree dirty, anything ambiguous is shown to you rather than deleted, and the pause always completes instead of getting stuck.

## [0.6.0] - 2026-06-24

### Changed

- **Breaking:** the three commands are renamed to `/rn:on` (start), `/rn:dn` (pause), and `/rn:up` (resume) — a two-letter on / down / up set that follows the session's lifecycle: power **on** to start, take it **dn** (down) to pause, then **up** to resume. Update any habits or notes from the old `/rn:rdy`, `/rn:brb`, `/rn:bak`.

## [0.5.0] - 2026-06-24

### Changed

- **Breaking:** the three commands are renamed to `/rn:rdy` (start), `/rn:brb` (pause), and `/rn:bak` (resume) — short, consistent chat-shorthand names that make the start→pause→resume flow easier to remember. Update any habits or notes from the old `/rn:gm`, `/rn:bb`, `/rn:hi`.

## [0.4.0] - 2026-06-15

### Changed

- Each task's hands-on work — writing the change and committing it — is now done by a dedicated implementation expert, while the assistant you talk to stays focused on planning, review, and getting your approval; your work accumulates as plain commits with a single completion marker per task, so the history stays easy to follow.

## [0.3.0] - 2026-06-15

### Changed

- When a task involves messy trial-and-error, that now happens out of sight, so only the finished, already-reviewed change reaches you for approval at every task boundary — keeping the conversation light and leaving you in control of what gets committed.
- Routine review fixes are now decided against a clear quality bar instead of asking you about minor things, so you are consulted only on decisions that are genuinely yours.

## [0.2.0] - 2026-06-14

### Added

- `/rn:gm` restates your goal in its own words and opens a draft PR with the full plan, so you can review and fix the direction before any work starts.
- Each task is now checked by a reviewer that deliberately looks for problems before the work is committed, so mistakes are caught early instead of after the fact.

### Changed

- The plan in `steering.md` is clearer to review on the PR: a single **Acceptance criteria** section (previously "Verification") spells out when the goal is done and what is in or out of scope.

## [0.1.0] - 2026-06-13

### Added

- Initial release — goal-driven work sessions with `/rn:gm` (start), `/rn:bb` (step away), and `/rn:hi` (resume), so one goal carries across conversations without losing the thread.
