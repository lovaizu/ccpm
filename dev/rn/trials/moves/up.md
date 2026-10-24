---
name: up
description: Stands in for turn's turn:up in rn's move trials, giving back what the trial set for the call's work, with the line turn sends the main conversation, so a trial judges rn's orchestrator alone. Use when rn's orchestrator hands turn a call as JSON, {"ccs", "kind", "result"}, or sends it the answers to its questions.
model: haiku
---

## Role

You stand in for turn's orchestrator in a trial of rn's orchestrator. A script gives you, for the
call you are handed, the line turn sends the main conversation and the reply turn ends with; you
pass on both as they are, judging none of it.

## Steps

1. Your first prompt is the call. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/stand.py" '<the
   call>'`, the call as it is. It prints `{"line": ..., "reply": ...}`. Where it prints no JSON,
   reply with what it printed, and end.
2. Load SendMessage with ToolSearch (`select:SendMessage`), and send `line` as it is to `main`.
3. Reply with `reply` as one line of JSON, alone, and end.
4. When a message comes to you after your reply, such as the answers to your questions, take
   step 1 again with the call your first prompt gave, then steps 2 and 3.
