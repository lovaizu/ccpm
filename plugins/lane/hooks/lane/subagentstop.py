"""SubagentStop entry of lane's hooks: keeps the orchestrator going while a start is due, and a
subagent going once where it gave no result, as hook.py says. hooks.json runs it as
`subagentstop.py <plugin>`, the plugin found where Claude Code gives its folder,
CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("SubagentStop", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
