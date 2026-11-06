"""Stop entry of lane's hooks: keeps the main conversation going once where it would end its turn
while a start of the run is due, as hook.py says. hooks.json runs it as `stop.py <plugin>`, the
plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("Stop", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
