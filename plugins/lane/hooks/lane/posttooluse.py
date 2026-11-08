"""PostToolUse entry of lane's hooks: keeps each call of a subagent of the plugin as it came back,
and, within a run, each start of the main conversation, telling it to wait, as hook.py says.
hooks.json runs it as `posttooluse.py <plugin>`, the plugin found where Claude Code gives its
folder, CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("PostToolUse", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
