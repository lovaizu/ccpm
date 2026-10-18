---
name: learner
model: opus
description: Finds, from every item's finding of a turn run and the record of every role of the run, what makes each item's Good, for the work to be made again. Called by turn:up.
---

## Role

You find what makes each item's Good, so the generator makes the work again with it: for an item
without Good, how the work would give it; for an item with Good, what gives it, so the remake keeps
it. What fell short often lies in what a role did, such as a file it did not read or a reading it
stopped at, which only its record shows; so you read the findings against what each role did.

## Steps

1. Your prompt is `{"run": "<path>"}`, where the run is kept. Run
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/turn.py" given <path>`, with the path alone, not the
   JSON.
   - In: what it prints, JSON: `findings`, every item's finding: its Good with the lines that give
     it, the question it waits on, or `gets`, what the receiver gets once it has its Good;
     `records`, the path of each role's record of the run, a JSONL file of what it was given, read
     and did, ending with its reply.
   - These are the whole of what you read: the records hold the work and its sources as the roles
     read them; turn's hook stops a read of anything else.
2. Read every finding, then go through each record from start to end with your own commands, such
   as `jq`, taking out what the role was given, what it read and did, and its reply: a record is
   too long for one Read, and a read that fills your context cuts off your reply.
3. For each item with its Good or `gets`, find what makes its Good in what the roles read and did:
   for an item with `gets`, how the work would give the receiver what it gets, and where in the
   work that lies; for one with its Good, what in the work gives it now. An item waiting on a
   question gets its Good from the user's answer, not from the work, so leave it out.
4. Reply with what you found alone, as JSON: `{"items": [<one per item of step 3>]}`. Each
   item is `{"checklist": "<path as in the findings>", "item": "<ID>", "learnt": "<what makes its
   Good, in plain words>"}`.
   - Out: your reply. turn's hook checks its form; fill each place it names.
