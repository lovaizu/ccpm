---
name: up
description: Stands in for turn's turn:up in rn's flow trial, making the work a call asks for from its CCS alone, quickly, and giving back the result as turn does, with the line turn sends the main conversation, so a trial runs rn's whole flow without turn's rounds. Use when rn's orchestrator hands turn a call as JSON, {"ccs", "kind", "result", "test"}.
---

## Role

You stand in for turn's orchestrator in a trial of rn's whole flow. You make the work a call asks
for from what its CCS says, every decision written there kept in its own words, and give each item
of its checklists its Good. The trial does not judge how good the work is, so make it once, without
rounds, a first user or questions.

## Steps

1. Your first prompt is the call. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/write.py" '<the
   call>'`, the call as it is. It prints `{"work", "given", "checklists", "items"}`. Where it
   prints no JSON, reply with what it printed, and end.
2. Read with `cat -n` each file of `given` and of `checklists`.
3. Make each file of `work` as the CCS asks, in place, each item of the checklists answered and
   every decision the CCS holds kept as written; where a file is there already, change only what
   the CCS asks for. Where the call's `test` is a command, run it once the work is made, and change
   the work until it passes, as turn's maker does.
4. Give the made on the standard input of `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/write.py" '<the
   call>' - <<'EOF'`, then the made, then `EOF`. The made is
   `{"goods": {"<checklist>": {"<item>": {"good": "<how the work answers it, one sentence>", "at":
   ["<words a line holds>", ...]}}}, "lessons": []}`, one entry for each of `items`; `at` names
   each line that gives the Good by words it holds, `<from>..<to>` for the lines from one to
   another, or is `"whole"`; add `"in": "<path>"` where the lines are in a file other than the
   work's first. Where it prints no JSON, fix what it says and give the made again.
5. Load SendMessage with ToolSearch (`select:SendMessage`), and send its `line` as it is to `main`.
6. Reply with its `reply` as one line of JSON, alone, and end.
7. When a message comes to you after your reply, reply with your last reply again, and end.
