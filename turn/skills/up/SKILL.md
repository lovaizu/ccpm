---
name: up
description: Carries one task of a plugin through making the deliverable, having it used in the receiver's place, finding why it came out away from what it should be and remaking it, and writes a new CCS. Called by a plugin's skill with two lines as its arguments, `in: <CCS file>` and `out: <file to write>`.
---

# turn:up

You are turn's orchestrator. You bring the deliverable to where its receiver can really use it, judged against what the CCS says it should be, and return a CCS from which the calling skill can trace its next step. You do it by calling four agents and passing on the places of what they write: the generator makes the deliverable, the first user uses it in the receiver's place, the learner finds why it came out away from what it should be, and the evaluator gives each point of what it should be a Good or a More. Scripts decide whether the loop goes on and write the CCS.

Do not read the deliverable, the reports or the records yourself. Making, using, learning and judging all mean reading long content; held in your conversation round after round, it would fill it, and you would drift from the goal and the rules.

The arguments:

$ARGUMENTS

## Before the first round

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py start <in> <out> ${CLAUDE_SESSION_ID}` from the repository. If python3 is not found, say to install Python 3.9 or later, and stop. If the script exits with 1, show what it printed as it is, and stop without writing a CCS. Otherwise it prints the work folder and what you pass on: `deliverable`, `receiver`, `use`, and `remake` when round 1 has something to remake the deliverable from.

## Each round

Round n starts at 1. Call each agent with the Agent tool, in the foreground, as a new agent every round, and note the agent id it returns. Before each call, say in one line in the conversation what is happening, such as "turn: using it as <the receiver>, in a freshly cloned copy". Hand each agent the places below; the files in the work folder are made by up.py or by the agents before it. An agent may be kept running by turn's own check until it has done its job; wait for it.

1. `turn:generator`: the round, `<work>/should.md`, `<work>/remake-<n>.md` when there is one (in round 1, when `start` printed it; in a later round, always), and its report file `<work>/generator-<n>.md`.
2. Make the copy: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py copy <work>`. It prints the copy's folder. If it exits with 1, show what it printed as it is, and stop without writing a CCS.
3. `turn:first-user`: the copy's folder, the deliverable's place in it, the receiver, the use, and its report file `<work>/first-user-<n>.md`. Hand it nothing else.
4. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py steps <work> <generator's agent id> <first user's agent id>`. It writes the steps both agents took, `<work>/steps-generator-<n>.md` and `<work>/steps-first-user-<n>.md`.
5. `turn:learner`: the round, `<work>/should.md`, the first user's report, both steps files, and its file `<work>/learner-<n>.json`.
6. `turn:evaluator`: the round, `<work>/should.md`, the deliverable's place, the generator's and the first user's reports, both steps files, the learner's file, and its file `<work>/evaluator-<n>.json`.
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py round <work>`. On `next round`, go to round n+1; on `end`, the turn ends. If it exits with 1, show what it printed as it is, and stop without writing a CCS.

## When the user asks to stop

Call no new agent, and end the turn with `stopped: <the agent and round that would have come next, such as first-user-2>`.

## Ending the turn

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/up.py end <work> generator-1=<id> first-user-1=<id> learner-1=<id> evaluator-1=<id> ...`, naming every agent called in this turn, with `"stopped: <where from>"` after the work folder when stopped.

If it exits with 1, show what it printed as it is, and stop. Otherwise say in one line the `next` it printed and the CCS's place, and return to the calling skill. Do not commit or push.
