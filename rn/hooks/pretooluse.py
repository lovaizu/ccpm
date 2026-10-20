"""PreToolUse entry of rn's hooks: runs each check as a tool is about to be used, and stops the use
with what they say.

The checks are rn's guards: each stops a move of rn's conductor, the AI running rn's commands in the
user's conversation, that breaks one of rn's rules, saying what to do instead and why. hooks.json
runs this with rn's scripts on PYTHONPATH, as the checks find the session through rn.py.
"""

import sys

import events
import hook

sys.exit(hook.run("rn", events.PRETOOLUSE, sys.stdin, sys.stderr))
