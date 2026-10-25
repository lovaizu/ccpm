"""PreToolUse entry of lane's hooks: runs the lanes laid in one subagent as that subagent is about
to use a tool, and denies the use with the sentence of each lane it drifts from.

hooks.json runs it as `pretooluse.py <plugin>:<subagent>`, the plugin found where Claude Code gives
its folder, CLAUDE_PLUGIN_ROOT, and the subagent's lanes in its hooks/lanes.json.
"""

import sys

import guard

guard.main("PreToolUse", sys.argv[1:])
