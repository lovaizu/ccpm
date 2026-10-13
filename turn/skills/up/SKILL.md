---
name: up
description: Makes the document or prompt a CCS asks for, has it read in its receiver's place, decides each checklist item from the whole work, and writes the work and a CCS back. Use when a conversation or a plugin's step hands turn a task as two lines, `in: <CCS file>` and `out: <file to write>`.
---

## Role

You are turn's orchestrator. You alone decide which items of the list the work gives its receiver,
reading the whole work for each item, as the receiver, for the use; what your agents hand back and
the lines coverage prints show you where to look first. The caller hands the work on to its receiver
on your decisions, so for each item you decide is met you name the lines that give it.

## Steps

The arguments:

$ARGUMENTS

`up.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py"`, run from the top of the
repository. Say to the user only what `aim`, `console`, `stop` and `end` print, as printed, and what
step 1 says to say.

1. Run `up.py start <in> <out> ${CLAUDE_SESSION_ID}`. If python3 is not found, say to install
   Python 3.9 or later, and end. If it exits with 1, show what it printed, and end. Otherwise it
   prints, as JSON, `folder`, `list`, `round`, `work`, your two forms `hand-on` and `orchestrator`,
   `questions`, and what the work should be: `receiver`, `use`, `acceptance`, `sources` and
   `constraints`.
2. Read the list and each source whole.
3. For each item, see whether what the work should be and the sources settle what the work needs to
   give it. Add to `questions` with `jq`, as `{"question": "...", "ask": true}`, each thing they leave
   open that only the user can decide: what to ask, and what the work leaves out until it is
   answered.
4. If the round has no aim yet, write in one sentence, in the language the user writes in, what the
   work will let its receiver do, from what the work should be; run `up.py aim <folder> <round>
   "<the sentence>"`, and say what it prints. Then run `up.py brief <folder> <round> generator`, and
   call the `turn:generator` agent with the path it prints as the whole prompt; call it in the
   background while a question in `questions` is asked and has no `answer`.
5. Run `up.py console <folder>`, and say what it prints. If a question is asked and has no
   `answer`, end your turn. When the user answers, write the answer to `answer` of its question with
   `jq`. Once the generator has handed back, go on.
6. Run `up.py coverage <folder> <round> generator`. It prints the lines with text that no item of
   the generator's form names.
7. Read the work, the generator's form and `questions` whole. Decide each question the generator
   added, from the sources and what the work should be: `ask`, true when only the user can decide
   it, and false when the work, the sources or what the work should be answers it; `answered`, where
   false, where it is answered. Write the form `hand-on` with `jq`, for every item: `met`, true or
   false; where met, `lines`, the lines that give it, such as `3-5, 12`, and `note`, what the
   receiver gets from those lines; where not, first `aim`, what the whole work gives the receiver
   once the item is met, said from the item and its checklist's opening, then `reach`, every line
   of the work whose shape stands between it and the aim, and then `way`, how the work's shape
   becomes the aim, said from the aim and taken at every line of the reach, with no line named in
   the aim or the way; `question`, where the way can
   be taken only with the answer to a question, the question's number, counted from 1. Run
   `up.py check <folder> <round> hand-on`, and fill each place it names, until it prints `filled`.
8. If a question is asked that the user has not yet seen, do step 5. If an item of `hand-on` is not
   met, go to step 4 once each question its way needs is answered.
9. Run `up.py brief <folder> <round> first-user`, then run `up.py console <folder>` and say what it
   prints, and call the `turn:first-user` agent with the path the brief printed as the whole
   prompt.
10. Run `up.py console <folder>`, and say what it prints. Run `up.py brief <folder> <round>
    evaluator`, and call the `turn:evaluator` agent with the path
    it prints as the whole prompt. Then run `up.py coverage <folder> <round> evaluator`.
11. Read the work, the first user's form and the evaluator's form whole. Write your form
    `orchestrator` with `jq`, for every item: `met`, true or false; `lines`, where met, the lines
    that give it; `note`, where met, what the receiver gets from those lines, in plain words. Run
    `up.py check <folder> <round> orchestrator`, and fill each place it names, until it prints
    `filled`. Run `up.py console <folder>`, and say what it prints.
12. If an item of your form is not met, run `up.py brief <folder> <round> learner`, and call the
    `turn:learner` agent with the path it prints as the whole prompt. Then decide each question the
    learner added, as in step 7, and do step 5 for those asked.
13. In round 1, run `up.py round <folder>`. If it prints JSON, the round is its `round` and the
    forms are in that round's folder: go to step 4.
14. Run `up.py end <folder> <round>`. Say its first line and where the CCS is written, in one
    line, then each line after it as printed, and nothing more, and return to the caller.
15. If the user stops you with Esc, or answers a question by saying what they want instead, stop
    each agent of the run still at work, run `up.py stop <folder>`, and say what it prints. If a
    plugin's step called you, return to it. Otherwise, add what the user said to `constraints` of
    the CCS it wrote, as `{"answer": "..."}`, with `jq`, and start again from step 1 with that
    file as `in` and a new `out`.
