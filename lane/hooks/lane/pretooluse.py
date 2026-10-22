"""PreToolUse entry of lane's hooks: runs the lanes its command lays in one subagent as that
subagent is about to use a tool, and stops the use with the sentence of each lane it drifts from.

hooks.json runs it as `pretooluse.py <plugin>:<subagent> <step>:<lane>:<what it takes>...`, the
plugin found where Claude Code gives its folder, CLAUDE_PLUGIN_ROOT. A command not in that form
lets the call through, telling the user, as no subagent or lane can be told from it.
"""

import os
import sys

import hook
import lanes

try:
    agent, laid = lanes.laid(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), sys.argv[1:])
except ValueError as wrong:
    sys.stderr.write(
        f"lane: the hook's command {wrong}, not as lane:up writes it, so this call goes on"
        " unchecked; run lane:up again on the plugin to write its hooks anew\n"
    )
    sys.exit(hook.UNREAD)
sys.exit(hook.run(agent.split(":")[0], laid, sys.stdin, sys.stderr, agent))
