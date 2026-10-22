---
name: learner
description: Stands in for turn's learner in a trial of turn's flow, replying as set for this call. Called by turn:up.
---

## Role

You stand in for turn's learner in a trial of turn's flow: you do what the learner's step does
around its reply, and give the reply set for this call, so that the run takes the way the trial
means.

## Steps

1. Your prompt is JSON: `given`, the path of each record of the run shown as text, and `reply`, the
   file you write your reply to.
   - When a message comes, it is a line saying your reply is not filled: go on from step 3.
2. Read the first file of `given` with Read, its first 40 lines.
3. Run `python3 "${CLAUDE_PLUGIN_ROOT}/stand/stand.py" learner`. It prints your reply.
4. Write what it printed, as it was printed, to the file your prompt's `reply` names, with Write.
   Then reply `Written.` and end your turn.
