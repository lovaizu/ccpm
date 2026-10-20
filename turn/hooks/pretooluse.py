"""PreToolUse entry of turn's hooks: runs each check as a tool is about to be used, and stops the
use with what they say."""

import sys

import events
import hook

sys.exit(hook.run("turn", events.PRETOOLUSE, sys.stdin, sys.stderr))
