# Lane's skeleton gaps

Each place where Lane's skeleton in `plugins/lane/` can't follow [the architecture](architecture.md),
for the architecture's maker to mend.

- Test strategy, integration testing, and the strategy of the plugin's folder: the double of Claude Code writes no transcript at `transcript_path`, so no integration case reaches `plugin.plugin_root`, nor any move of a run past it.
- Test strategy, integration testing, and the strategy of the reporters as commands on the AI's path: the double puts no plugin's `bin/` on the path of the Bash tool, so no integration case runs `lane-step`, `lane-item`, or `lane-result` by its name as Claude Code does.
- Directory structure, `types/` of `hooks/lane/`: `python3` puts the folder of `guard.py` first on the import path, so a folder `types/` beside it takes the place of the standard library's `types`, and the guard fails at its first import, as `json` imports `enum`, which imports `types`; the rule types stay in `hooks/lane/lanes/` until the architecture names a folder that no module of the standard library shares.
- S10 and the Lane: the kept adapter gives each result with its role alone, so a run picked up in a new conversation with several lanes going at once can't place each kept result in its lane, nor give the starts due of each lane.
- The strategy of a route that starts one role several times: a route after a result that starts several roles makes each start due in the result's lane, and the architecture names no way that lane moves on, by each start's own result or by one result once each has its own.
