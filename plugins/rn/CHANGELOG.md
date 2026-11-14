# Changelog

## [Unreleased]

### Changed

- `/rn:up` with what you want lays out every piece the goal needs, and the order it needs them in, before it makes any, so no piece goes missing or comes before what it takes.
- rn makes each piece by the best practice of its kind. A second AI judges it as its people would, given only the piece, what it takes from, and a record of its commands tried in a throwaway copy. rn makes the piece again until it meets every question of its kind, so what you get is usable as it comes.
- rn asks you one point at a time, only what the purpose and the best practices leave to you, with its recommendation, and says at the end what it decided without asking, so your answers go only to what's yours.
- `/rn:up` alone, in a new conversation, picks the work up where it stopped from `.rn/<date>-<goal>/` in your repository, so you never answer a point twice.
- rn commits each piece on its own branch `rn/<date>-<goal>` and keeps one draft pull request for you to merge, so the work stays in your repository and the merge stays yours.
- rn now installs Lane with it, which holds each of its steps on every run.
- rn's folder carries its own license, and its manifest names its homepage and repository, so a copy of the folder alone says how you may use rn and where it comes from.

### Removed

- `/rn:ty` and `/rn:gm`: you answer each point in your own words, and merge the draft pull request yourself.
- rn no longer needs Turn, which it now holds.

## [0.9.0] - 2026-10-06

0.9.0 rebuilds how a session runs, from your first words to the last sign-off.

### Added

- `rn` asks why you want the goal and finds what you really want behind your first words, one point per message, asking what you want a result to do for you before offering any way, offering ways with what each gives and costs and the one it recommends, and asking what only you can know instead of guessing it, so what you get is what you meant.
- Acceptance criteria come in two kinds, what would make you choose the result and what you take for granted, each with an ID, and the effort goes to the first kind first, so `rn` checks the reason you wanted the work while there's still time to change course.
- At the Design sign-off you also approve a verification document: for each criterion, how to use the product as you would use it and what must happen then, so you know before `rn` builds anything how you can see that it works, and anyone can run the same check again after any later change.
- `/rn:on` asks which language to write the repository in and which to talk in, proposing what your repository and instructions already set, so a single yes settles both and everything `rn` writes and says comes in the one you chose.
- Each time `rn` decides what to do next on a task, it says in one line whether the task has fulfilled its purpose and what follows, so a glance shows you where the session is and why.
- When you take up a session, and before each sign-off, `rn` brings its branch up to date with the default branch, so you never approve work on files the default branch no longer has.
- Installing `rn` also installs `writ`, which writes your README, design document, and verification document, so what you settle reads well to whoever picks it up.
- `rn` checks its own record as it goes, so it stops a decision not pushed, a sign-off passed without your `/rn:ty`, a finding left out of the record, or a reply to you in a language you didn't choose where it happens. These checks need Python 3.9 or later. Without it, `rn` stops in a repository it works in and says so, since a check skipped unseen would let a breach through.

### Changed

- A session started under an earlier `rn` has its goal worked out again with you from its old record when you run `/rn:up`, and stops at a new Plan sign-off. The new plan keeps the work already done as facts with where to find them, and `rn` removes the old session's files, which stay readable in git. Until then, `/rn:ty`, `/rn:gm`, and `/rn:dn` ask you to run `/rn:up` first instead of bringing it up to date on their own, so `rn` judges every later decision by why you want the goal.
- In place of the QA, Design, Craft, and Verification reviewers, an agent that knows nothing of how a result came about uses it as you would before you see it, and says what it understood and what happened, so a result passes because it does its job, rather than on the word of its maker or a reviewer.
- Every sign-off comes with what `rn` proposes to do next and why, what changed since your last approval, including what you settled by answering a question, and anything the product stops doing. Under each question it gives what's good and what falls short, with where and which of your criteria it bears on, and every assumption not yet checked stands as a shortfall until `rn` checks it, so you can say yes or no without re-reading the work.
- Every proposal says first how close the work has come to each thing you would choose it for, and what came closer since the last one, so you decide when it's close enough instead of waiting for `rn` to clear every shortfall.
- `rn` spends its checks and fixes on what you would choose the work for: it checks that with the fewest uses that show it, the way you would use the product, and fixes first what brings it closer. It neither chases small gaps off that path nor puts them before you, so you get what you came for sooner.
- There's always a Design sign-off, and `rn` plans the tasks only after it, so they follow what you agreed there instead of getting rewritten.
- `rn` writes the README, design document, and verification document into your product, as `README.md`, `docs/design.md`, and `docs/verification.md` unless you agree another place, instead of a session's design under `.rn/`, and they stay after the session, so the next session, or a teammate, starts from what you settled.
- `/rn:ty` and `/rn:gm` record your answer and stop instead of going straight on, so you can clear the conversation at any sign-off and lose nothing. To go on, say "go on" or `/clear` and then `/rn:up`.
- `rn` no longer acts on feedback point by point as worded: feedback on the plan or the design sends the session back to working it out with you, starting from what it shows you don't yet share, and stops at that sign-off again before `rn` builds anything on it, while feedback on the result gets tasks of its own, or goes back to the design when it changes what the product should be, so `rn` fixes what lies behind your words, not only the words.
- `/rn:gm` gives feedback only on the sign-off waiting for you, and no longer carries out other instructions at other times. Plain `/rn:gm` takes every comment you wrote on the pull request since `rn` stopped for the sign-off, and no longer takes comments by others, so you can give feedback where you read, and only your feedback decides the work.
- The last sign-off is now the Deliverable sign-off, and approving it with `/rn:ty` marks the pull request ready, so only the merge remains for you.
- `/rn:on` always starts a new branch from the newest commit of the default branch, even when you're on another branch, and stops without touching anything when you have uncommitted changes, so a session never builds on stale or unrelated work and never takes in yours. It names the session from your words instead of asking you for a name, and opens the draft pull request at once, before you and `rn` work out the plan, so you can follow the plan on the pull request as you agree it.
- `/rn:up` takes up the session on the branch you're on, instead of searching the history for a paused one. Check out the session's branch first, so the session you resume is always the one you're looking at.
- `rn` no longer keeps the findings on each piece of work as `checks/` files under `.rn/`. The message of the commit that settles a report keeps it whole, with each finding and what became of it, and every commit ends with a line saying what `rn` decided and what comes next, instead of a `complete task #N` marker, so the pull request's history shows you why `rn` fixed or let go each finding, and `.rn/` holds only `steering.md` and what's still open.
- The pull request body links, beside `steering.md`, the issues the work closes or serves and the pull requests it replaces, so GitHub connects them for you.
- Where rn can't find Claude Code's record of the conversation, it says it couldn't check whether you typed `/rn:ty` or `/rn:gm`, or search the session's conversations for a learning's cause, and where it looked—rn never takes a check it couldn't make for one that found nothing.

### Removed

- `rn` no longer replies to your review threads on the pull request, `/rn:dn` no longer asks about untracked files, and `/rn:up` no longer offers to commit or discard leftover changes. `rn` takes your comments whole as feedback, and a pause commits and pushes what the task under way changed, so a resume has nothing to ask.

## [0.8.0] - 2026-07-07

### Added

- Every session now records which version of `rn` it started under, and each command checks that against the installed version on every run—on a mismatch, it reconciles the session's plan, design, and remaining tasks to the current conventions automatically before continuing, so older sessions keep working correctly as `rn` itself evolves, with nothing extra for you to do.

### Changed

- Writing or updating a session's `design.md` now requires an explicit decision and the reasoning behind it for every question the design template raises—no section can stay blank or get silently skipped any longer—so the resulting design doc always shows what the session decided and why, not just what it ultimately built.
- Starting a session no longer always creates a brand-new `design.md`: if an existing one already covers the work's area, the assistant now points at it and walks through an update instead of authoring from scratch, so related work accumulates in one design doc instead of spawning duplicates.

## [0.7.0] - 2026-07-05

### Added

- `/rn:ty`, to approve, and `/rn:gm`, to revise, give you one accept/revise vocabulary at every gate and confirmation point—plan, design, evaluation, or any reviewed result—so you always know how to respond and the assistant never has to guess your intent from prose.
- `/rn:gm` with no argument now works through your PR's unresolved review threads one at a time—addressing each and replying with the fix, or asking a question when the ask is unclear—and leaves resolving each thread to you on GitHub, so review feedback gets handled systematically without anything getting closed out from under you.
- Once a session is underway, every message that stops for your input opens with a compact session map—✅ done / 👉 now / ⬜ ahead, plus what the message asks—so you can answer on the spot without opening `steering.md` to see where things stand.

### Changed

- Session directories now carry a date prefix, `.rn/{yyyymmdd}-{slug}/`, such as `.rn/20260702-payment-fix/`, so as sessions accumulate under `.rn/`, a directory listing reads in chronological order.
- You now sign off at three points—the plan up front, the approach when it needs a separate look, and the result at the end—instead of approving every task. In between, the assistant works through the tasks and has them checked behind the scenes, and only interrupts you mid-flight when a call is genuinely yours—so you get fewer interruptions while keeping the say on the moments that matter.
- A plan now writes its completion criteria as two questions anyone can answer with evidence—has the work actually achieved the goal, and are new problems absent—so a criterion can't pass just because the work produced some file.
- `steering.md` stays a lean plan for the remaining work: design intent and decisions now live in a separate `design.md` it points to, finished-task detail and deliberation stay in git and the PR, and a pause records only a short forward pointer—so the plan never piles up across pause/resume cycles.

### Fixed

- `/rn:dn`, the pause, now finishes with a genuinely clean worktree—leftover test/build files now fall under git's ignore rules so they stop keeping the tree dirty, the assistant shows you anything ambiguous rather than deleting it, and the pause always completes instead of getting stuck.

## [0.6.0] - 2026-06-24

### Changed

- **Breaking:** the three commands have new names, `/rn:on` to start, `/rn:dn` to pause, and `/rn:up` to resume—a two-letter on / down / up set that follows the session's lifecycle: power **on** to start, take it **dn**, for down, to pause, then **up** to resume. Update any habits or notes from the old `/rn:rdy`, `/rn:brb`, and `/rn:bak`.

## [0.5.0] - 2026-06-24

### Changed

- **Breaking:** the three commands have new names, `/rn:rdy` to start, `/rn:brb` to pause, and `/rn:bak` to resume—short, consistent chat-shorthand names that make the start→pause→resume flow easier to remember. Update any habits or notes from the old `/rn:gm`, `/rn:bb`, and `/rn:hi`.

## [0.4.0] - 2026-06-15

### Changed

- A dedicated implementation expert now does each task's hands-on work—writing the change and committing it—while the assistant you talk to stays focused on planning, review, and getting your approval. Your work accumulates as plain commits with a single completion marker per task, so the history stays easy to follow.

## [0.3.0] - 2026-06-15

### Changed

- When a task involves messy trial-and-error, that now happens out of sight, so only the finished, already-reviewed change reaches you for approval at every task boundary—keeping the conversation light and leaving you in control of what gets committed.
- The assistant now decides routine review fixes against a clear quality bar instead of asking you about minor things, so it consults you only on decisions that are genuinely yours.

## [0.2.0] - 2026-06-14

### Added

- `/rn:gm` restates your goal in its own words and opens a draft PR with the full plan, so you can review and fix the direction before any work starts.
- A reviewer now checks each task, deliberately looking for problems before the work goes into a commit, so it catches mistakes early instead of after the fact.

### Changed

- The plan in `steering.md` is clearer to review on the PR: a single **Acceptance criteria** section, which replaces the earlier "Verification" section, spells out when the goal counts as done and what's in or out of scope.

## [0.1.0] - 2026-06-13

### Added

- Initial release—goal-driven work sessions with `/rn:gm` to start, `/rn:bb` to step away, and `/rn:hi` to resume, so one goal carries across conversations without losing the thread.
