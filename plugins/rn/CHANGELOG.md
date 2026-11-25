# Changelog

## [0.11.0] - 2026-11-25

### Changed

- rn hears your goal one point at a time, from an issue's number or a few words, and asks only what your request, issue, repository, and earlier answers leave open.
- rn shows the way to the goal step by step in your words, and you sign off only the steps you choose to check.
- Each message opens with where the run stands and speaks in your language and terms, never of rn's insides.
- rn drops each point and finding that your goal's people would reach the goal without, so the plan and the deliverables don't pile up.
- An AI new to the work checks the whole pull request and its CI before rn proposes the merge, and the pull request stays a draft until you mark it ready.
- Where what rn makes holds a prompt, rn tests its scripts by unit tests, static analysis, and coverage, and leaves the prompts to your own end-to-end run.
- rn no longer needs Lane.

### Added

- A problem with a deliverable already made, such as a push that your checks refuse, is mended at once where the mend keeps the plan's decisions.
- Inside herdr, each run's worktree opens as a herdr workspace.
- An AI can start, pick up, and pause a run, so an AI that gives out work can run rn in each worktree.
- You can pause or cancel a run in your own words. A cancel also removes the run's branch and open pull request on GitHub.

### Fixed

- A command that only reads the plan is no longer refused as a write.
- A fix that your goal's people need is made past the remake limit.
- The steps put each deliverable after those it rests on.
- rn cuts the parts of a deliverable that its people don't need.
- `/rn:up` picks up only a run that still exists, and each run gets its own pull request.
- The final check waits for the CI to start, and names a cancelled or timed-out check for you to run again.
- A run no longer waits on a permission prompt when a maker removes its own files.

## [0.10.0] - 2026-11-22

### Changed

- rn plans the deliverables your goal needs in a design tree, and you sign off the plan before it makes any.
- rn asks you only the decisions that change what the people get, one at a time with its recommendation, and goes on with other work while one waits.
- Evaluators read each deliverable as its people would, and rn remakes it from the decision behind each shortfall until they find it good.
- `/rn:ty` signs off and goes on at once. `/rn:gm` sends back to the decision behind your words.
- rn works in its own worktree and branch. `/rn:dn` pauses with the work pushed, and `/rn:up` picks it up in any conversation.
- Lane replaces writ, and rn's folder carries its own license.

## [0.9.0] - 2026-10-06

### Added

- rn finds what you want behind your first words before it offers a way.
- Acceptance criteria split into what you'd choose the result for and what you take for granted, and the first kind comes first.
- A verification document says how you can see that the product works.
- `/rn:on` settles both languages in one answer.
- rn checks its own record as it goes. It needs Python 3.9 or later.

### Changed

- A user-like agent tries each result in place of the reviewers.
- Each sign-off says what changed and how close the work has come to your goal.
- rn writes the README, design, and verification documents into your product, where they stay after the session.
- Feedback goes back to what lies behind your words. `/rn:gm` takes your comments on the pull request.
- Each session starts from the newest default branch, and approving the last sign-off marks the pull request ready.

### Removed

- rn no longer replies to review threads, or asks about leftover files on a pause or a resume.

## [0.8.0] - 2026-07-07

### Added

- A session started under an older rn is brought up to date when you resume it.

### Changed

- The design answers each question its template raises, and updates an existing design in place of a new one.

## [0.7.0] - 2026-07-05

### Added

- `/rn:ty` approves and `/rn:gm` revises at every sign-off.
- Each message that waits for you opens with a map of the session.

### Changed

- You sign off the plan, the approach, and the result, in place of each task.
- A session's folder starts with its date.

### Fixed

- `/rn:dn` leaves a clean worktree.

## [0.6.0] - 2026-06-24

### Changed

- **Breaking:** the commands are `/rn:on`, `/rn:dn`, and `/rn:up`.

## [0.5.0] - 2026-06-24

### Changed

- **Breaking:** the commands are `/rn:rdy`, `/rn:brb`, and `/rn:bak`.

## [0.4.0] - 2026-06-15

### Changed

- An implementation expert writes and commits each task, while the main assistant plans and reviews.

## [0.3.0] - 2026-06-15

### Changed

- Trial and error happens out of sight, and routine review fixes no longer ask you.

## [0.2.0] - 2026-06-14

### Added

- `/rn:gm` restates your goal and opens a draft pull request with the plan.
- A reviewer checks each task before its commit.

## [0.1.0] - 2026-06-13

### Added

- Goal-driven sessions that carry across conversations: `/rn:gm`, `/rn:bb`, and `/rn:hi`.
