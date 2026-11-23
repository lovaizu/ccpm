# Changelog

## [Unreleased]

### Added

- `/overnight:stack` takes a queue file that names each task's prompt and the folder it works in. overnight runs the tasks apart from Claude Code, three at a time, from the hour you set or else at once, so they go on after your session ends and you let go once you've stacked them.
- Each task starts with its tools allowed and its edits accepted, so it never stops to ask for a permission that no one is there to give. A task with `writes` set to `true` writes only in its folder, and each other task gets only read-only tools.
- A task that reaches the usage limit goes on in the same session once the limit resets, so no one restarts it. Its new reply follows the earlier one, so you take in the whole result.
- overnight gives up a task that the limit stops seven times, with its reason and session, so the others go on.
- `/overnight:check` shows which tasks finished and which were given up, with each reply and the folder each task wrote in, so you take the results in with git.
- A plugin that runs its own AI sessions can stack its task as a queue of one and read from `/overnight:check` how it ended, so the task gets the same wait and resume without the plugin writing them again.
