# Changelog

All notable, user-facing changes to the `rn` plugin are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
A version goes up by what changes for you: the middle number for anything you would notice, the
last for fixes that change nothing you do.

## [0.9.0] - 2026-10-03

0.9.0 rebuilds how a session runs, from your first words to the last sign-off.

### Added

- `rn` asks why you want the goal and finds what you really want behind your first words, one point per message with the answer it recommends, asking what a result must do for you before offering ways and asking what only you can know instead of guessing it, so what you get is what you meant.
- Acceptance criteria come in two kinds, what would make you choose the result and what you take for granted, each with an ID, and the effort goes to the first kind first, so the reason you wanted the work is checked while there is still time to change course.
- At the Design sign-off you also approve a verification document: for each criterion, how the product will be used as you would use it and what must happen then, so you know before anything is built how you will see that it works, and the same check can be run again after any later change.
- `/rn:on` asks which language to write the repository in and which to talk in, proposing what your repository and instructions already set, so a single yes settles both and everything `rn` writes and says comes in the one you chose.
- Each time `rn` decides what to do next on a task, it says in one line whether the task's purpose is fulfilled and what follows, so a glance tells you where the session is and why.
- When a session is taken up, and before each sign-off, its branch is brought up to the latest default branch, so you never approve work on files the default branch no longer has.
- Installing `rn` also installs `writ`, which writes your README, design document, and verification document, so what you settle reads well to whoever picks it up.
- `rn` checks its own record as it goes, so a decision not pushed, a sign-off passed without your `/rn:ty`, a finding left out of the record, or a reply to you in a language you did not choose is stopped where it happens. These checks need Python 3.9 or later; without it, `rn` stops in a repository it works in and says so, since a check skipped unseen would let a breach through.

### Changed

- A session started under an earlier `rn` has its goal worked out again with you from its old record when you run `/rn:up`, and stops at a new Plan sign-off; what was done is kept in the new plan as facts with where they are, and the old session's files are removed, staying readable in git; until then `/rn:ty`, `/rn:gm`, and `/rn:dn` ask you to run `/rn:up` first instead of bringing it up to date on their own, so every later decision is judged by why you want the goal.
- The QA, Design, Craft, and Verification reviewers are replaced: before you see a result, an agent that knows nothing of how it was made uses it as you would and says what it understood and what happened, so a result passes because it does its job, not because its maker or a reviewer says so.
- Every sign-off comes with what `rn` proposes to do next and why, what changed since your last approval, including what you settled by answering a question, and anything the product will no longer do; under each question it gives what is good and what falls short, with where and which of your criteria it bears on, and every assumption not yet checked stands as a shortfall until it is, so you can say yes or no without re-reading the work.
- Every proposal says first how close the work has come to each thing you would choose it for, and what came closer since the last one, so you decide when it is close enough instead of waiting for every shortfall to be cleared.
- `rn` spends its checks and fixes on what you would choose the work for: it checks that with the fewest uses that show it, the way you would use the product, and fixes first what brings it closer; small gaps off that path are neither chased nor put before you, so you get what you came for sooner.
- There is always a Design sign-off, and the tasks are planned only after it, so they follow what you agreed there instead of being rewritten.
- The README, design document, and verification document are written into your product (`README.md`, `docs/design.md`, `docs/verification.md` unless you agree another place) instead of a session's design under `.rn/`, and stay after the session, so the next session, or a teammate, starts from what you settled.
- `/rn:ty` and `/rn:gm` record your answer and stop instead of going straight on; say "go on", or `/clear` and then `/rn:up`, so you can clear the conversation at any sign-off and lose nothing.
- Feedback is no longer acted on point by point as worded: feedback on the plan or the design sends the session back to working it out with you, starting from what it shows you do not yet share, and stops at that sign-off again before anything is built on it, while feedback on the result gets tasks of its own, or goes back to the design when it changes what the product should be, so what lies behind your words is fixed, not only the words.
- `/rn:gm` gives feedback only on the sign-off waiting for you, and no longer carries out other instructions at other times; plain `/rn:gm` takes every comment you wrote on the pull request since `rn` stopped for the sign-off, and no longer takes comments by others, so you can give feedback where you read, and only your feedback decides the work.
- The last sign-off is now the Deliverable sign-off, and approving it with `/rn:ty` marks the pull request ready, so only the merge is left to you.
- `/rn:on` always starts a new branch from the latest default branch, even when you are on another branch, and stops without touching anything when you have uncommitted changes, so a session never builds on stale or unrelated work and never takes in yours. It names the session from your words instead of asking you for a name, and opens the draft pull request at once, before the plan is worked out, so you can follow the plan on the pull request as it is agreed.
- `/rn:up` takes up the session on the branch you are on, instead of searching the history for a paused one; check out the session's branch first, so the session you resume is always the one you are looking at.
- The findings on each piece of work are no longer kept as `checks/` files under `.rn/`: every report, with each finding and what became of it, is kept whole in the message of the commit that settles it, and every commit ends with a line saying what was decided and what comes next, instead of a `complete task #N` marker, so the pull request's history tells you why each finding was fixed or let go, and `.rn/` holds only `steering.md` and what is still open.
- The pull request body links, beside `steering.md`, the issues the work closes or serves and the pull requests it replaces, so GitHub connects them for you.

### Removed

- `rn` no longer replies to your review threads on the pull request, `/rn:dn` no longer asks about untracked files, and `/rn:up` no longer offers to commit or discard leftover changes; your comments are taken whole as feedback, and a pause commits and pushes what the task under way changed, so a resume has nothing to ask.

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
