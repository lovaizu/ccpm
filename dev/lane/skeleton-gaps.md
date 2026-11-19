# Lane's skeleton gaps

Each place where Lane's skeleton in `plugins/lane/` can't follow [the architecture](architecture.md),
for the architecture's maker to mend.

- Components, reporters, and S9: no arrow of S9 or S10 carries a reporter's report to the guard, and Data model has no kind of data for a report, so the form of a report lies on both sides of the handoff: in `bin/report.py`, which prints it, and in `place.Report`, which reads it.
- S1 to S8: no sequence draws how the guard meets a subagent's call, mark, or end, so `guard.call_made`, `guard.report_made`, `guard.subagent_ended`, and `guard.fact_added` follow the strategies of Components alone, and their integration cases have no arrow to name.
- Claude Code's states, a subagent started in the background, and a resume queued to a subagent that still runs: the table says Lane hooks no SubagentStart, yet the guard holds a queued resume's start back until that subagent's SubagentStart, so `hooks/hooks.json` enters the guard on no SubagentStart, and no event lets the start held back go.
- Components, the strategy of the plugin's folder found from the base directory of its skill, and S9's call of the skill: the states say that the transcript holds the base directory once the skill expands, but name no event at which it first does, and the PreToolUse of Skill comes before the expansion, so `guard.skill_called` can't tell at which event `plugin.plugin_root` first finds the folder.
- Test strategy, integration testing, and the strategy of the plugin's folder: the double of Claude Code writes no transcript at `transcript_path`, so no integration case reaches `plugin.plugin_root`, nor any move of a run past it.
- Test strategy, integration testing, and the strategy of the reporters as commands on the AI's path: the double puts no plugin's `bin/` on the path of the Bash tool, so no integration case runs `lane-step`, `lane-item`, or `lane-result` by its name as Claude Code does.
- Data model, Rules: the main conversation's calls are held to each Run's rules, yet nothing says how the rules name the main conversation, whose events carry no `agent_type`, so `rules.schema.json` keys the roles by agent type alone and gives the main conversation no steps.
- Components, the strategy of a new kind of check by a new rule type alone: the order in which a mark and an end are checked, and the form of each type's values in `rules.json`, make a new rule type change `hooks/lane/lanes/__init__.py` and `hooks/lane/rules.schema.json` beside its own module.
