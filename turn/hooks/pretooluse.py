"""PreToolUse entry of turn's hooks: runs each check as a tool is about to be used, and stops the
use with what they say."""

import sys

import events

sys.exit(events.main(events.PRETOOLUSE, sys.stdin))
