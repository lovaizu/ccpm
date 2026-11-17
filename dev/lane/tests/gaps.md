# Lane's test gaps

Each place where Lane's test cases, in this folder, can't follow
[the architecture](../architecture.md) and the skeleton in `plugins/lane/`, for whoever makes the
architecture.

- Test strategy, Performance testing: the double of Claude Code runs each hook in the case's own
  process, so a time taken there leaves out the start of Python, which Claude Code pays on each
  hook event as it starts the guard anew. KR1.2 needs each event's time with that start in it.
- S5 and claude-code-states.md, a role's Read, Grep, or Glob: no record in `dev/tests/recorded/`
  holds a Grep's or a Glob's events, so the double of Claude Code sends neither, and no
  integration case shows a Lane of reads_none stopping a Grep or a Glob. Only the unit cases of
  reads_none show it, by Calls of their own.
