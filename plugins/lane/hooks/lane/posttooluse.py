"""PostToolUse entry of lane's hooks: keeps each call of one subagent lanes are laid in as it comes
back, so the guard holds the subagent to it before Claude Code's record holds it, as called.py says.

hooks.json runs it as `posttooluse.py <plugin>:<subagent>`, the plugin found where Claude Code gives
its folder, CLAUDE_PLUGIN_ROOT.
"""

import sys

import called
import hook

# Keeping a call takes nothing of the plugin, the subagent or the event held.
hook.main("PostToolUse", sys.argv[1:], lambda root, agent, held: called.Kept())
