# Changelog

## [Unreleased]

### Added

- `/overnight:stack` takes a queue file that names each task's prompt and the folder it works in. overnight runs the tasks three at a time from the hour you set, apart from Claude Code, so they go on after your session ends and you let go once you've stacked them.
- A task that reaches the usage limit goes on in the same session once the limit resets, so no one restarts it. Its new reply follows the earlier one, so you take in the whole result.
- overnight gives up a task that the limit stops seven times, with its reason and session, so the others go on.
- `/overnight:check` shows which tasks finished and which were given up, with each reply and the folder each task wrote in, so you take the results in with git.
