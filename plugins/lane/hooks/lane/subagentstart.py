"""SubagentStart entry of lane's hooks: keeps each start of a subagent of the plugin, and gives the
subagent its part whole, as hook.py says. hooks.json runs it as `subagentstart.py <plugin>`, the
plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("SubagentStart", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
