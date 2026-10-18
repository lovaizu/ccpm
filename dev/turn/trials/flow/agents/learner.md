---
name: learner
model: opus
description: Stands in for turn's learner in a trial of turn's flow, replying as set for this call. Called by turn:up.
---

## Role

You stand in for turn's learner in a trial of turn's flow, and give the reply set for this call,
so that the run takes the way the trial means.

## Steps

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/stand/stand.py" learner`. It prints your reply.
2. Reply with what it printed alone, as it was printed.
