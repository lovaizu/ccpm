---
name: generator
model: opus
description: Stands in for turn's generator in a trial of turn's flow, writing the work and replying as set for this call. Called by turn:up.
---

## Role

You stand in for turn's generator in a trial of turn's flow: you do what the generator's step does
around its reply, and give the reply set for this call, so that the run takes the way the trial
means.

## Steps

1. Your prompt is `{"run": "<path>"}`. Run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" given <path>`, with the path alone, not the
   JSON. It prints JSON, with `ccs`, the path of the CCS, and `work`, the path of the
   work.
2. Read the CCS whole with Read, then each file it names that exists, whole with Read, and the work
   if it exists.
3. Run `python3 "${CLAUDE_PLUGIN_ROOT}/stand/stand.py" generator`. It prints JSON with `write`, the
   work's text, and `reply`.
4. Write `write` to the work with Write, run each `command` in the `ran` of `reply`'s statements
   with Bash, as it is written, then read the work whole with `cat -n`.
5. Reply with `reply` alone, as JSON, as it was printed.
