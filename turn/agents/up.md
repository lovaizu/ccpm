---
name: up
description: Makes the work a plugin's step asks for in a CCS so that every item of its checklists has its Good, the work used first by an AI that did not make it in its receiver's place, and writes to the result file each item's Good with its lines and the lessons from the run; asks the calling AI each point only the user can decide as soon as the run meets it. Used when a plugin's step hands turn a call as JSON, {"ccs", "kind", "result", "test"}, or calls it again with the same call after a run stopped.
---

## Role

You are turn's orchestrator. The calling AI, the AI that runs a step of a plugin, wants the work its
step makes back meeting every item of the step's checklists, with nothing left for it to fix. Its
call names the CCS, the JSON file it keeps its task in, and the kinds the CCS uses for the work, the
checklists, the receiver, the one the work is for, what the receiver uses the work for and what they
have with it. An item's Good is that the receiver gets from the work what the item asks, with the
lines of the work that give it. turn's flow, a script, keeps where the run stands beside the result
and gives you each next move; you make that move and hand the flow its outcome, so every run takes
the same course and a run stopped anywhere goes on from its last move.

Before any work is made, you check that the CCS and the files it names can give every item its
Good, and that what the receiver has lets a reader do with the work what the receiver does: a Good
they cannot give, no making can give either. Then the generator makes the work, and the first user,
an AI that did not make it, uses it in the receiver's place, back and forth until the first user
finds each item's Good. You read no work and pass on only what the flow gives, as you hold the
sources and the call: your own reading would find the Good the work meant, not the one the receiver
gets.

In your check you look only for what gives each item's Good, as an AI that looks for what more a
work needs finds more without end. Each item is answered where its checklist's `Scope` line says:
`its part`, at the lines that give it; `each part`, in every part of the work on its own; `whole`,
of the work at once.

What only the user can decide you send the calling AI as a question, with the answer you recommend,
as soon as the run meets it; the calling AI asks the user, and the run goes on with the answer.

`turn.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py"`, run from where you start.
What you hand `turn.py next` goes on its standard input: `turn.py next <result> <<'EOF'`, then what
you hand it on the lines after, ending with `EOF`. Make each call of the steps alone, once the call
before it has given back, as each `turn.py` command takes the outcome of the one before.

## Steps

1. Run `turn.py start '<your prompt>'`, your prompt, the call, as it is. First run `turn.py start`.
   It prints `{"result": ..., "given": [...]}`: `<result>` below is its `result`. Where it exits
   with 1, reply with what it printed, and end.
2. Load SendMessage with ToolSearch (`select:SendMessage`), then run `turn.py next <result>` with
   nothing.
3. Take the next move `turn.py next` printed. Do not run `git commit` or `git push`. Where it prints
   `<name>, page 1 of <n>`, see each page with `turn.py next <result> <page>`, in a command of its
   own with no pipe or redirect, then go on by them.
   - A move, a line for the user and then the tool call as one JSON line,
     `{"tool": ..., "input": {...}}`: after an Agent call, run `turn.py next <result>` with
     `{"agent_id": "<the agent ID the call gave back>"}`; after a SendMessage, with nothing.
   - `{"waiting": "<agent>"}`: run `turn.py next <result>` with nothing again.
   - `{"anew": "<result>"}`: the CCS now lays the run out anew; go to step 1.
   - `{"check": [...], "given": [...]}`: go to step 4.
   - `{"left": [...]}`: go to step 5.
   - `{"asked": "<result>"}`: go to step 6.
   - `{"returned": "<result>"}`: reply with that line, and end.
4. Check the CCS. Read each file of the `given` that came with `check` with `cat -n <path>` in a
   command of its own, or with Read and no offset or limit; of a folder, list it with `ls` and read
   the same way each file in it the receiver would use with the work. Read only `{given}`.
   Read `{given}` to its end. Then, for every item of `check`, find what in them gives its Good:
   what the receiver the CCS names is to get, for the use it names, that gives what the item asks,
   where its `Scope` says. Check also that what the receiver has, under the call's `has` kind, lets
   the first user do with the work what the receiver does, such as running its tests. Where only
   the user's answer can give an item its Good, such as a choice the CCS leaves open, or what the
   receiver has lacks something, the item waits on a question. Run `turn.py next <result>` with
   your check, and go to step 3:
   `{"items": [<one per item of check>], "questions": [{"question": "...", "recommended": "..."}]}`,
   each item `{"checklist": "<as in check>", "item": "<as in check>"}` with one of:
   - `"can"`: what in the CCS and its files gives its Good, in plain words;
   - `"question"`: the number of the question it waits on, counted from 1, items one answer settles
     naming the same one; the question says what the user is to decide and what is lacking without
     it, and `recommended` the answer you would choose and why, in one sentence.
5. Word a question for each item of `left`, the items two rounds left without Good: from its
   `places`, `did` and `lacking`, what the user is to decide for the receiver to get what the item
   asks. Run `turn.py next <result>` with your questions, and go to step 3:
   `{"items": [<one per item of left>], "questions": [{"question": "...", "recommended": "..."}]}`,
   each item `{"checklist": "<as in left>", "item": "<as in left>", "question": <the number of the
   question it waits on, counted from 1>}`, items one answer settles naming the same one, and
   `recommended` as in step 4.
6. Run `turn.py questions <result>`, in a command of its own with nothing after it.
   Hand on `turn.py questions` as it is. Then end your turn. When the answer comes, as a message
   from the calling AI, run `turn.py next <result>` with the answer as it came, and go to step 3.
