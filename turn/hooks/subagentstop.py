"""SubagentStop entry of turn's hooks: runs each check as one of turn's agents ends, and keeps it
going with what they say."""

import sys

import events

sys.exit(events.main(events.SUBAGENTSTOP, sys.stdin))
