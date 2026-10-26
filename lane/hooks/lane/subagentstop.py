"""SubagentStop entry of lane's hooks: runs the lanes laid in one subagent as that subagent is about
to end, and keeps it going with the sentence of each lane it has not kept, which Claude Code gives
it as its next instruction.

hooks.json runs it as `subagentstop.py <plugin>:<subagent>`, the plugin found where Claude Code
gives its folder, CLAUDE_PLUGIN_ROOT, and the subagent's lanes in its hooks/lanes.json.
"""

import sys

import guard
import hook

hook.main("SubagentStop", sys.argv[1:], guard.Lanes)
