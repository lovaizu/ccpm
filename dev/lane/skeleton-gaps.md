# Lane's skeleton gaps

Each place where Lane's skeleton in `plugins/lane/` can't follow [the architecture](architecture.md),
for the architecture's maker to mend.

- Test strategy, integration testing, and the strategy of the plugin's folder: the double of Claude Code writes no transcript at `transcript_path`, so no integration case reaches `plugin.plugin_root`, nor any move of a run past it.
- Test strategy, integration testing, and the strategy of the reporters as commands on the AI's path: the double puts no plugin's `bin/` on the path of the Bash tool, so no integration case runs `lane-step`, `lane-item`, or `lane-result` by its name as Claude Code does.
- Run and S9, "until the order gives no start due": no start due means both a run that waits for a subagent still running and a run whose order starts no more, and the architecture names no other sign of a run's end, which place.skill_call needs to tell a new run from a move of the run that stands. The skeleton takes a run as ended once its order gives no start due while no start of it runs, kept as an `ended` entry, until the architecture says how a run ends.
- S10 and the route adapter: in a new conversation the run record holds no run, so the route adapter, which reads only the routes and the run given, gives the starts after the command, and a plugin that fixes its order by routes starts again from its command instead of going on where it stopped.
