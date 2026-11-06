"""UserPromptSubmit entry of lane's hooks: tells the main conversation the next start within a run,
as a subagent's end reaches it as a task-notification, as hook.py says. hooks.json runs it as
`userpromptsubmit.py <plugin>`, the plugin found where Claude Code gives its folder,
CLAUDE_PLUGIN_ROOT."""

import os
import sys

import hook

hook.main("UserPromptSubmit", sys.argv[1:], sys.stdin, sys.stdout, os.environ["CLAUDE_PLUGIN_ROOT"])
