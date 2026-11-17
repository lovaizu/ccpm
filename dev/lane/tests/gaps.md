# Lane's test gaps

Each place where Lane's test cases, in this folder, can't follow
[the architecture](../architecture.md) and the skeleton in `plugins/lane/`, for whoever makes the
architecture.

- S5 and claude-code-states.md, a role's Read, Grep, or Glob: no record in `dev/tests/recorded/`
  holds a Grep's or a Glob's events, so the double of Claude Code sends neither, and no
  integration case shows a Lane of reads_none stopping a Grep or a Glob. Only the unit cases of
  reads_none show it, by Calls of their own.
