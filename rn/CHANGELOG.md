# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Every plan and every task's result is now judged by a third party against a few named questions about whether it does its job — a pass means the work works, not that a step ran.
- A plan is judged as a chain — Goal, its Success criteria, each task's Objective, each task's Success criteria, the Assumptions — so a gap at any level is caught before you read it; a plan `/rn:gm` changes is judged again the same way, so a criterion nobody asked for cannot enter.
- `steering.md` names its bar as `Success criteria` (session and task) and each task's aim as `Objective` — the names say what is judged: that the goal is achieved, not that a deliverable exists.
- The agent in the conversation is a conductor, not a relay — it reads every result before the evaluator and you see it, and keeps the plan current with what each round taught, so what reaches you is worth your decision.
- Every evaluation round is committed into the session's own folder as the evaluator wrote it, an NG as much as an OK — you read what was judged and why on the pull request, next to the diff it judged, and the folder is cleared when you sign the session off, so what remains is the plan and the work.
- Hands-on work runs on the faster model (`sonnet`) and judgment on the stronger one (`opus`) — routine work moves fast and the calls that matter get the stronger read.
- `rn`'s prompt text reads in one sitting and every step says what it is for — you can tell what each command does and why.
- A session written under an older `rn` is rebuilt from the current template the next time a command runs on it, carrying every task, check-off and pending item — it goes on at the current bar with nothing to do by hand.
- `State` keeps a `Pending` line that survives a resume — a gate awaiting your verdict or an item you deferred is not lost between conversations.
- A session you approve at "Evaluation sign-off" is finished by its own record — `/rn:up` no longer offers it to resume, and nothing can say otherwise.
- A session's folder is named after what the work produces rather than the ticket it came from — `.rn/20260702-payment-fix/` reads as work, and the issue and pull request are recorded inside.
- `steering.md` opens with a small table of the session's facts — which `rn` it runs under, its issue, its pull request, its design, and whether it is running or paused — so you see where a session stands the moment you open it on GitHub.
- The session map quotes the goal and the task names as `steering.md` writes them — what you approved keeps its name across conversations.
- A review thread you open on the session PR carries the same weight as `/rn:gm <text>` — the reply is the change and its commit, and the thread is left for you to resolve.

### Removed

- The per-task review chain and its `checks/` files, and the per-session `design.md` template — a session leaves only `steering.md` and the deliverable.

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
