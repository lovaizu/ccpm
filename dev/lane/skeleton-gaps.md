# Lane's skeleton gaps

Each place where Lane's skeleton in `plugins/lane/` can't follow [the architecture](architecture.md),
for the architecture's maker to mend.

- Test strategy, integration testing, and the strategy of the plugin's folder: the double of Claude Code writes no transcript at `transcript_path`, so no integration case reaches `plugin.plugin_root`, nor any move of a run past it.
- Test strategy, integration testing, and the strategy of the reporters as commands on the AI's path: the double puts no plugin's `bin/` on the path of the Bash tool, so no integration case runs `lane-step`, `lane-item`, or `lane-result` by its name as Claude Code does.
