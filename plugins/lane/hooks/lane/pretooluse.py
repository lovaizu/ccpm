"""PreToolUse entry of lane's hooks: judges each tool call of a subagent of the plugin with lanes
laid, and, within a run, each start of the main conversation, as hook.py says. hooks.json runs it
as `pretooluse.py <plugin>`, the plugin found where Claude Code gives its folder,
CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("PreToolUse", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
