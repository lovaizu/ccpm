── writ-first-user-saved-output: a writ first user reads the output its own calls saved ──
✅ #1 Plan sign-off
👉 #2 Design sign-off ── read it on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes

Draft PR: https://github.com/lovaizu/ccpm/pull/42

Approve the design, and I will plan and build the tasks it calls for: the hook that lets the first user read only the output its own calls saved, its unittest cases, the A1 trial in dev/writ/trials/, a line in the first user's definition saying it may read that output, and the CHANGELOG entry. The design closes #36 without opening Claude Code's records to the first user, and the A1 scene already reproduces #36 against today's writ, so the same scene will show the fix.

Goal: Issue #36: writ's first-user history check stops a first user reading its own saved command output. When a `writ:first-user` runs a Bash command whose output is too large, Claude Code saves it under `~/.claude/projects/<project>/<session>/tool-results/`, and the check, which blocks any path under `/.claude/projects`, stops the first user from reading it, so it spends a step finding another way.
Judged by:
- A1: A writ first user reads the whole of what its own tool calls returned, even when Claude Code saved it to a file for being too long, and goes on using the work without a detour.
- M1: The first user still never reads how the work was made: Claude Code's conversation records, and any saved output it cannot be shown to have made itself, including another first user's, stay closed to it.
- M2: Agents other than `writ:first-user` are not affected by the check.

Toward what you would choose it for:
- A1: on paper, fully: the design lets the first user read its own saved output by any reading tool, and the A1 scene, run against today's writ, reaches exactly the stop of #36, so after the build it shows whether the first user reads the whole output without a detour (first proposal of the design).

Changed since the last approval: none
Taken away: nothing; every stop of today stays, and the one new stop (when the hook cannot read the first user's own record) applies only to paths that are stopped today anyway.

### What the first user may read
- Good A1: the first user reads the file its own call saved, by Read, Grep or Bash, at writ/docs/design.md:82 and writ/docs/verification.md:63.
- Good M1: only a path Claude Code itself recorded as saved output in the first user's own record opens; a path it typed or printed, such as other agents' outputs found with `find`, does not, at writ/docs/design.md:82 and writ/docs/verification.md:69-71.
- Good M1: a path written with `~` or `..` is compared as the same file, so it neither opens another file nor stops the first user's own, at writ/docs/design.md:82 and writ/docs/verification.md:64-66.
- Good M2: the check still applies only to `writ:first-user`, at writ/docs/design.md:80 and writ/docs/verification.md:74.
- More A1: the rule rests on one trial on Claude Code 2.1.291, with a general-purpose subagent, showing that the record quotes the saved path before the read, at writ/docs/design.md:82; the A1 scene run on the built hook will show whether it holds for the first user.

### How you will see it works
- Good A1: the A1 scene starts the first user as writ does, as a subagent, and has it run the script as written, so Claude Code saves the output and the answer lies only in it, at writ/docs/verification.md:19-23 and :36-46; run against today's writ, the first user tried to read the saved file and was stopped, as in #36.
- Good M1: every M1 rule has its own machine check, at writ/docs/verification.md:64-73.
