── writ-first-user-saved-output: a writ first user reads its own saved output without a detour ──
👉 #1 Plan sign-off ── read it on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
⬜ #2 Design sign-off

Draft PR: https://github.com/lovaizu/ccpm/pull/42

Next, once approved: work out how the check tells the first user's own saved output from another
agent's, and write it into writ's design document, so the first user reads its own long output while
everything that shows how the work was made stays closed.

Goal: Issue #36: writ's first-user history check stops a first user reading its own saved command
output. When a `writ:first-user` runs a Bash command whose output is too large, Claude Code saves it
under `~/.claude/projects/<project>/<session>/tool-results/`, and the check, which blocks any path
under `/.claude/projects`, stops the first user from reading it, so it spends a step finding another
way.
Judged by:
- A1: A writ first user reads the whole of what its own tool calls returned, even when Claude Code
  saved it to a file for being too long, and goes on using the work without a detour.
- M1: The first user still never reads how the work was made: Claude Code's conversation records,
  and any saved output it cannot be shown to have made itself, including another first user's, stay
  closed to it.
- M2: Agents other than `writ:first-user` are not affected by the check.

Toward what you would choose it for:
- A1: not yet given; today the first user is stopped from its own saved output. The plan fixes what
  it must do: open its own saved output, whatever tool made it, and only that. (first proposal)

### Whether the plan holds
- Good A1: the reason you filed the issue, the wasted step, is what A1 promises to remove, at
  steering.md "Attractive quality".
- Good M1: what M1 keeps closed rests on writ's design (writ/docs/design.md:80): a first user that
  reads how the work was made fills its gaps with the maker's intent.
- More A1: one session keeps every agent's saved output in one folder, and the file name never says
  which agent wrote it, so the check needs another way to tell the first user's own; that is the
  design's first point, at steering.md "Not yet specified". A way is seen on this machine: the saved
  path is quoted in the transcript of the agent that made it, and the check is told which agent is
  running (steering.md "Assumptions").
