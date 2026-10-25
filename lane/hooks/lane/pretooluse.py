"""PreToolUse entry of lane's hooks: runs the lanes its command lays in one subagent as that
subagent is about to use a tool, and denies the use with the sentence of each lane it drifts from.

hooks.json runs it as `pretooluse.py <plugin>:<subagent> <step>:<lane>:<what it takes>...`, the
plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT.
"""

import sys

import guard

guard.main("PreToolUse", sys.argv[1:])
