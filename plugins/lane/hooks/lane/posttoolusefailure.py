"""PostToolUseFailure entry of lane's hooks: tells the orchestrator the start still due where its
start failed, as hook.py says. hooks.json runs it as `posttoolusefailure.py <plugin>`, the plugin
found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main(
    "PostToolUseFailure", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"]
)
