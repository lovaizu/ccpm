# Lane's test gaps

Each place where Lane's test cases, in this folder, can't follow
[the architecture](../architecture.md) and the skeleton in `plugins/lane/`, for whoever makes the
architecture.

- Test strategy, Installation testing: `dev/scripts/e2e.py` runs Claude Code on plugin folders, and
  has no way to run the README's install commands in a fresh home's shell. So
  `test_lane_installs_by_the_readmes_commands` runs them by itself.
- Test strategy, Installation testing: the README's `claude plugin marketplace add lovaizu/ccpm`
  reads the marketplace on GitHub's main, which holds no Lane until Lane releases with rn. So
  `scenario.install` runs the README's commands with the top of this repository as the
  marketplace's source, which tries the same commands and marketplace file on the version under
  test.
- S6 and claude-code-states.md, a role's Read, Grep, or Glob: no record in `dev/tests/recorded/`
  holds a Grep's or a Glob's events, so the double of Claude Code sends neither, and no
  integration case shows a Lane of reads_none stopping a Grep or a Glob. Only the unit cases of
  reads_none show it, by Calls of their own.
