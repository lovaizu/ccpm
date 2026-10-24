"""SubagentStop entry of lane's hooks: runs the lanes its command lays in one subagent as that
subagent is about to end, and keeps it going with the sentence of each lane it has not kept, which
Claude Code gives it as its next instruction.

hooks.json runs it as `subagentstop.py <plugin>:<subagent> <step>:<lane>:<what it takes>...`, the
plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT.
"""

import sys

import lanes

sys.exit(lanes.main("SubagentStop", sys.argv[1:]))
