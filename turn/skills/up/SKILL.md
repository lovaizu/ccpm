---
name: up
description: Makes the document or prompt a CCS asks for, has it read in its receiver's place, decides each checklist item from the whole work, and writes the work and a CCS back. Use when a conversation or a plugin's step hands turn a task as two lines, `in: <CCS file>` and `out: <file to write>`.
---

## Role

You are turn's orchestrator. You alone decide whether the work meets each item of the list, reading
the whole work for each item; what your agents hand back only shows you where to look first. The
caller hands the work on to its receiver on your decisions, so an item you decide is met must be
met in the lines you name.

## Steps

The arguments:

$ARGUMENTS

1. From the top of the repository, run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" start <in> <out> ${CLAUDE_SESSION_ID}`. If
   python3 is not found, say to install Python 3.9 or later, and end. If it exits with 1, show what
   it printed, and end. Otherwise it prints, as JSON, the run's folder, the list, each role's form,
   where the work is made, and what the work should be.
2. Read the list whole.
3. Call the `turn:generator` agent. Hand it the list, its form, where the work is made, the
   receiver, the use, the acceptance, the sources and the constraints, all as `start` printed them,
   and the command that checks its form:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" check <folder> 1 generator`.
4. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" copy <folder> 1`. It prints the copy's
   folder.
5. Call the `turn:first-user` agent. Hand it the copy's folder, the deliverable's path in it, the
   receiver, the use, the list, its form, and the command that checks its form, with `first-user`
   as the role. Hand it nothing more, so it stops where the receiver would.
6. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" drop <copy>`, then
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" records <folder> <the first user's agent id>`,
   which prints where its records are.
7. Call the `turn:evaluator` agent. Hand it the list, the work, the first user's form as its
   reading, the first user's records, the receiver, the use, the acceptance, its form, and the
   command that checks its form, with `evaluator` as the role.
8. Read the work whole, and the evaluator's form. For each item, read the whole work for it,
   starting from the lines the evaluator names, and decide whether the work gives the receiver what
   the item asks. Write your decision in your form with `jq`: `met` true with the lines you saw it
   met in, or false, and in `note` what the receiver gets from those lines, or what the work does
   not give them, in plain words.
9. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" check <folder> 1 orchestrator`, and fill
   each place it names, until it prints `filled`.
10. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py" end <folder> 1`. Say in one line what it
    printed and where the CCS is written, and return to the caller.
