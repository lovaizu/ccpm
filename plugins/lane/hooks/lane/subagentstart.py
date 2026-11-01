"""SubagentStart entry of lane's hooks: tells the orchestrator of the flow its move due as it
starts, which Claude Code adds for it to read before its first prompt, as moves.py reads the move.

hooks.json runs it as `subagentstart.py <plugin>:<orchestrator>`, the plugin found where Claude
Code gives its folder, CLAUDE_PLUGIN_ROOT, and the flow in its hooks/lanes.json.
"""

import sys

import called
import hook

# Telling the move takes the plugin, to read its flow, and the subagent, not the event held.
hook.main("SubagentStart", sys.argv[1:], lambda root, agent, held: called.Started(root, agent))
