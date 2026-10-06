---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/42
status: running
artifact-language: English
conversation-language: Japanese
readme: writ/README.md
design: writ/docs/design.md
verification: writ/docs/verification.md
---

# Goal

Issue #36: writ's first-user history check stops a first user reading its own saved command output.
When a `writ:first-user` runs a Bash command whose output is too large, Claude Code saves it under
`~/.claude/projects/<project>/<session>/tool-results/`, and the check, which blocks any path under
`/.claude/projects`, stops the first user from reading it, so it spends a step finding another way.

# Acceptance criteria

## Attractive quality

- A1: A writ first user reads the whole of what its own tool calls returned, even when Claude Code
  saved it to a file for being too long, and goes on using the work without a detour.

## Must-be quality

- M1: The first user still never reads how the work was made: Claude Code's conversation records,
  and any saved output it cannot be shown to have made itself, including another first user's,
  stay closed to it.
- M2: Agents other than `writ:first-user` are not affected by the check.

# Assumptions

- Fact, `writ/docs/design.md:80`: the first user does not read how the work was made, since it would
  fill the work's holes with the maker's intent; hooks stop paths under `.claude/projects`, where the
  conversation records are, only when `agent_type` is `writ:first-user`.
- Fact, checked under `~/.claude/projects/` on this machine, Claude Code 2.1.291: a session's saved
  outputs share one folder, `<project>/<session>/tool-results/`, holding those of the main
  conversation and of every subagent in the session, beside the conversation records
  (`<session>.jsonl`, `<session>/subagents/agent-<id>.jsonl`). Files are named `toolu_….txt` or by a
  short random id, both forms for both kinds of agent (`toolu_` from WebFetch, which a first user
  does not have), and folders such as `pdf-<uuid>/page-N.jpg` hold the pages of a PDF read with
  Read; the name never says which agent wrote it. Only a long Bash output (`<id>.txt`) is seen
  stopped in use (#36). The saved path is quoted
  in the transcript of the agent whose call made it.
- Fact, `dev/writ/tests/test_pretooluse.py:17-31` and this machine: the hook input carries
  `transcript_path`, `agent_id`, `agent_type`, and `tool_use_id`; `agent_id` matches the name of the
  subagent's transcript `subagents/agent-<id>.jsonl`.
- Fact, `rn/hooks/checks/first_user_reads.py`: rn's own first-user check does not stop paths under
  `.claude/projects`, so rn is not part of this fix.

# Rules

- Follow `.claude/rules/plugin.md`: Python 3.9 with the standard library only, `unittest` tests in
  `dev/writ/tests/` that run every line and check both a case stopped and a case let through, and an
  entry under `## [Unreleased]` in `writ/CHANGELOG.md` without bumping the version.
- The user said writ need not be used for the rest of this session: the conductor fixes the
  documents itself.

# Tasks

### [x] #1: Plan sign-off
### [x] #2: Design sign-off

# Not yet specified

- The tasks that build what the design documents say: the hook in `writ/hooks/checks/`, its unittest
  cases, the A1 trial in `dev/writ/trials/`, `writ/agents/first-user.md:35-37` saying the first user
  may read the output its own calls saved, and the `writ/CHANGELOG.md` entry; planned after the
  Design sign-off.
