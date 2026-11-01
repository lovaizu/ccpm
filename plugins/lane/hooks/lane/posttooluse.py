"""PostToolUse entry of lane's hooks: keeps each call of one subagent lanes are laid in as it comes
back, so the guard holds the subagent to it before Claude Code's record holds it, and the report a
subagent of the flow's order hands back with SubagentHandback, as called.py says.

hooks.json runs it as `posttooluse.py <plugin>:<subagent>`, the plugin found where Claude Code gives
its folder, CLAUDE_PLUGIN_ROOT.
"""

import sys

import called
import hook

# Keeping a call takes the plugin, to read its flow, and the subagent, not the event held.
hook.main("PostToolUse", sys.argv[1:], lambda root, agent, held: called.Kept(root, agent))
