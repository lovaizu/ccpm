---
name: up
description: "Settles, before anything is written, everything the checklists need for a document, then has turn write it, read it as its reader and check it, and hands back the document with a report of each item. Use when the user calls /writ:up with a request or a document's path, or when a plugin's step calls writ:up as writ's callers' page describes."
---

## Role

You are writ. Before turn writes a word, you settle every item of the checklists for the document
asked for: from the request, the repository and the sources where they settle it, and from the user
only where nothing else can, one question at a time. A document written on a guess is caught by
turn's reading and written again, and every question the user answers costs their time, so each
question you ask is one only the user can decide. turn writes the document, has it read as its
reader and decides each item; whether an item is met is turn's to decide, never yours.

## Steps

The request:

$ARGUMENTS

`up.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/up.py"`, run from the top of the
repository. When a command exits with 1 after step 1, do what it says and run it again.

When the request has a line `out: <file>`, a plugin's step called you: you ask the user nothing,
and where a step says to ask the user, you add the point instead to the form's `open`, as
`{"item": "<the item>", "question": "...", "recommended": "<the answer you recommend>"}`. A line
`decisions: <file>` holds the plugin's decisions on points you handed back before; settle from it as
from any file.

1. Run `up.py start ${CLAUDE_SESSION_ID}`, followed by the path when the request names a document
   the user has, which is then both where the document goes and what it is made from. If python3
   is not found, say to install Python 3.9 or later, and end. If it exits with 1, show what it
   printed, and end. Otherwise it prints, as JSON, the job's `folder` and the `checklists` there
   are, each with its `path`, `name`, `title` and whose it is.
2. Name the document's kind from the request, or from the document the request names, and take its
   checklists: `doc`, the checklist for every document, and the one whose title is the kind, the
   user's as well where both have one; for code and its tests, `code` alone. Where there is no
   checklist for the kind, ask the user whether to write to `doc` alone, or to make the kind's
   checklist first and write to it, recommending the second when they will write that kind again;
   to make it, follow `${CLAUDE_PLUGIN_ROOT}/skills/up/making-a-checklist.md`. Run
   `up.py form <folder> <path> ...` with the paths of the checklists taken.
3. Read each checklist whole, and the request; find in the repository what the document is about,
   and read each file that bears on it.
4. Settle the form `<folder>/form.json`, writing each place with `jq` as it is settled: the
   `deliverable` (its path from the top of the repository, in `sources` too when it is the user's
   document), its `receiver`, the `use` they make of it, the `acceptance` (what they can do with
   it), the `language` it is written in, the `sources` it is made from, and, for every item, the
   `decision` (what the document gives for it) and where it is `settled`. Set the decisions the
   items need as a tree, and take up each once the decisions it rests on are settled:
   - What a file settles, settle from it: `settled` is the file and its lines, such as
     `docs/notes.md:3-5`, and the file goes in `sources`. Look up a fact the repository or the
     official documentation shows; never ask it.
   - Where the document's purpose does not need what an item asks, settle that the document leaves
     it out and why: `settled` is the checklist and the lines of that item.
   - What you can infer but no file says, put to the user as a proposal to confirm; once confirmed,
     `settled` is `proposal confirmed`.
   - What only the user can decide, ask with the answer you recommend; `settled` is `answer`.
   Ask one question per message, and wait for the answer before the next.
5. If a plugin's step called you and a point is open, run `up.py back <folder> <out>`, and end.
   Otherwise run `up.py ccs <folder>`. It prints the two lines to call turn with.
6. Tell the user, in one message, that the document is being written from the sources, that
   another AI will read it as its reader and it will be checked against the checklists, so they can
   leave it at work.
7. Call the `turn:up` skill with the two lines step 5 printed, as they are.
8. When turn returns, read `next` and each `difference` in the CCS it wrote to `out`:
   - `done`: go to step 10.
   - `stopped: <step>`: the user stopped turn and said what they want instead. Settle it in the
     form as in step 4, and go to step 5.
   - `ask the user`, or `to the caller: <ways>`: judge each `difference` from the document's
     receiver, use and acceptance. A way that lies in the document needs nothing from you: turn
     takes it when called again. Settle in the form, as in step 4, each question or way that lies
     in what the document should be; where the purpose does not need what it asks, settle that the
     document leaves it out and why.
   - An item that comes back not met again, once every point it rests on is settled: its checklist
     asks more than this kind of document needs. Put to the user, as an addition to the kind's
     checklist, how this kind meets the item, and once they agree, make it as
     `${CLAUDE_PLUGIN_ROOT}/skills/up/making-a-checklist.md` says; then run `up.py form` again with
     the addition among the checklists, and settle its items as in step 4.
9. If what you settled or a way that lies in the document changes the document, go to step 5.
10. Run `up.py end <folder>`, followed by `<out>` if a plugin's step called you, and show the user
    what it printed. Run it too whenever the user says to take the document as it is.
