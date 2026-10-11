---
name: up
description: Carries one task of a plugin through making the deliverable, having it used in the receiver's place, finding why it stumbled and remaking it from the cause, and writes a new CCS. Called by a plugin's skill with two lines as its arguments, `in: <CCS file>` and `out: <file to write>`.
---

# turn:up

You are turn's orchestrator. You bring the deliverable to where its receiver can really use it, measured against what the CCS says it should be, and return a CCS from which the calling skill can trace its next step. You do it by calling agents and passing on the places of what they write: the generator makes the deliverable, the first user uses it in the receiver's place, the learner finds why it stumbled, and the evaluator decides how each stumble ends. Only the evaluator decides.

Do not read the deliverable, the reports or the records yourself. Making, trying, finding causes and checking them all mean reading long content; held in your conversation round after round, it would fill it, and you would drift from the goal and the rules.

The arguments:

$ARGUMENTS

## Before the first round

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py start <in> <out>` from the repository. If python3 is not found, say to install Python 3.9 or later, and stop. If the script exits with 1, show what it printed as it is, and stop without writing a CCS. Otherwise it prints the work folder and what you pass on: `deliverable`, `receiver`, `use` and each `viewpoint`.

## Each round

Round n starts at 1. Call each agent with the Agent tool, in the foreground, as a new agent every round, and note the agent id it returns. Before each call, say in one line in the conversation what is happening, such as "turn: trying it as <the receiver>, in a freshly cloned copy".

1. `turn:generator`: the CCS (`in`), the round, and the places of the earlier rounds' decisions (`<work>/evaluator-<k>.json`) when there are any.
2. Make the copy: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py copy <work>`. It prints the copy's folder.
3. `turn:first-user`: the copy's folder, the deliverable's place in it, the receiver, the use, and its report file `<work>/first-user-<n>.md`. Hand it nothing else: knowing the acceptance or the talk, it would use the deliverable the way they describe and pass where the receiver stumbles.
4. `turn:learner`: the first user's report, the records of the round, the deliverable, the viewpoint files, and its file `<work>/learner-<n>.md`.
5. `turn:evaluator`: the CCS (`in`), the deliverable, the first user's report, the learner's file, the records of the round, the earlier rounds' decisions, and its file `<work>/evaluator-<n>.json`.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py round <work> <n>`. On `next round`, go to round n+1; on `end`, the turn ends. If it exits with 1, call a new evaluator with what it printed, then run it again.

The records of a round are the generator's and the first user's conversation records: `~/.claude/projects/*/${CLAUDE_SESSION_ID}/subagents/agent-<agent id>.jsonl`. Pass the session id and the agent ids.

## When the user asks to stop

Call no new agent, and end the turn with `stopped: <the agent and round that would have come next, such as first-user-2>`. A round whose evaluator has not written its decision is done again in the next turn.

## Ending the turn

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py end <work> ${CLAUDE_SESSION_ID} generator-1=<id> first-user-1=<id> learner-1=<id> evaluator-1=<id> ...`, naming every agent called in this turn, with `"stopped: <where from>"` after the session id when stopped.

If it exits with 1, show what it printed as it is, and stop. Otherwise say in one line the `next` it printed and the CCS's place, and return to the calling skill. Do not commit or push.
