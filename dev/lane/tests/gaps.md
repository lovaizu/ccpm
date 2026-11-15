# Lane's test gaps

Each place where Lane's test cases, in this folder, can't follow
[the architecture](../architecture.md) and the skeleton in `plugins/lane/`, for whoever makes the
architecture.

- Test strategy, Installation testing: `dev/scripts/e2e.py` runs Claude Code on plugin folders, and
  has no way to run the README's install commands in a fresh home's shell. So
  `test_lane_installs_by_the_readmes_commands` runs them by itself.
