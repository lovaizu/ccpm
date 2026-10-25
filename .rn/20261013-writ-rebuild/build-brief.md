# Build brief: bring one plugin to what its audit says it should be

Repository: /Users/kiyo/work/lovaizu/ccpm/.claude/worktrees/writ-rebuild (ccpm: lane, turn, rn).
Branch writ-rebuild. Commit as `git -c user.name=kiyobot -c user.email=kiyohito.itoh+bot@gmail.com
commit`, messages in the form of `git log -10` (one line saying what now holds, then the two
trailer lines below). Do not push. Do not touch files outside the slice your task names, except
where it says.

Trailer lines for every commit message:

    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01LCZwD8H3wK9UHJZ2DRfTqQ

## What the maintainer wants

These works are kept and used for a long time. Each is to be refined: simple, the necessary
minimum, nothing said twice, nothing against another part, nothing no reader needs. What the
maintainer fears most is that the thinking and intent built up in the prompts and the code wear
away in the clean-up: checks and tests only see behaviour, not intent.

## How

1. Read whole first: the audit reports your task names, `.claude/rules/dev.md`,
   `dev/architecture.md`, and the checklists that apply (`rn/checklists/product/code.md` for code
   and tests, `prompt.md` for agents and skills, `architecture.md`, `ux.md`, `readme.md` and
   `rn/checklists/usability.md` for documents, `rn/checklists/fix.md` for every change). Keep them
   open while you work.
2. For each finding, check it at its source first. Drop it where it is not true, saying why.
3. Before you change or remove a line, find why it is there: `git log -L <from>,<to>:<file>` or
   `git blame`, the commit message (it holds the options weighed and why), `.rn/*/decisions/`, the
   architecture's reasons, trial results. Keep that intent: where lines are merged, the kept place
   carries it; a line written against a slip a trial showed is dropped only where something else is
   shown to hold it now. A line whose reason you cannot find is kept, and listed for the maintainer.
4. Tests first for any change of behaviour: write or change the test, see it fail, then the code.
   Pure moves and renames keep the tests passing as they are.
5. After each group of changes run, from the top of the repository:
   `uv run --no-sync sh dev/check.sh <plugin>` (100% line and branch coverage, ruff, pyrefly,
   manifests); `CI=true uv run --no-sync sh dev/properties.sh <plugin>`; at the end
   `uv run --no-sync sh dev/mutate.sh <plugin>`, which must end with 0 survivors. A mutant no input
   the code takes can tell apart gets `# pragma: no mutate` on its line, and the reason is written
   once in `dev/<plugin>/cosmic-ray.toml`; every other survivor gets a test. Also run the checks of
   each other plugin that uses what you changed (`sh dev/changed.sh HEAD~1 HEAD` names them).
6. One commit per group of changes, each passing the checks, so one can be undone alone.
7. The plugin's README and UX (`<plugin>/README.md`, `dev/<plugin>/ux.md`) were agreed with the
   user. Change them only where they say what is untrue, and list each such change, old and new
   words, in your report; never reword them for style.

## Report (your final reply, English, terse)

- Each commit: hash and one line.
- Findings dropped, each with why.
- Findings left, each with why (and which need the maintainer).
- Each line or rule removed whose intent moved elsewhere: where it lives now.
- Lines kept for want of a reason found.
- README/UX changes, old and new words.
- The checks' final results: tests, coverage, mutation survivors (count and time), properties.
