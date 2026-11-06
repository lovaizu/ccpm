"""UserPromptExpansion entry of lane's hooks: begins a run as the command of the skill the routes
name is typed, and tells the main conversation the first start, as hook.py says. hooks.json runs it
as `userpromptexpansion.py <plugin>`, the plugin found where Claude Code gives its folder,
CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main(
    "UserPromptExpansion", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"]
)
