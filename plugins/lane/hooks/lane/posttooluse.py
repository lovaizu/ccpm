"""PostToolUse entry of lane's hooks: keeps each call of a subagent of the plugin as it came back,
and tells the orchestrator the next start as its start comes back, as hook.py says. hooks.json
runs it as `posttooluse.py <plugin>`, the plugin found where Claude Code gives its folder,
CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("PostToolUse", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
