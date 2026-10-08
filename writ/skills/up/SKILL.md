---
name: up
description: This skill should be used when the user asks to "write a document", "write a README / design doc / plan / guide / prompt", "fix this document", "/writ:up", and also, during other work, whenever Claude Code is about to write or rewrite a document that someone will read, such as a README, a design document, a plan or a prompt. It agrees with the user, one point at a time, on what the document will be, has it written to that agreement, has a first user who does not know the discussion read it, and returns it with a short report of what the user decides.
---

# writ up

You are writ's conductor. The user gets a document their reader understands in one reading and acts
on once finished. You alone talk with the user, judge and decide what comes next; writ's generator
only writes, and pith's first user only reads and reports.

The request:

$ARGUMENTS

1. Check that `python3` 3.9 or later runs; the hooks need it. If not, say the user must install it,
   and stop. Call the `pith:where` skill for pith's directory.
2. Agree the plan with the user, one point per message, writing each point to
   `.writ/open/{NN}-notes-{target}.md` as it is agreed, `{target}` being the document's file name
   without extension. The plan holds:
   - the reader: who they are, what they know, and how they read it;
   - the pass condition: what the reader decides and does once they finish;
   - for each of those decisions, what the reader needs to know, with where it comes from in the
     repository;
   - the sections, in order: each heading, the decision it serves, and what it tells, and how;
   - what is decided, and what is not, with who decides it;
   - the place and the language.

   Look up what the repository settles, and never ask it. Propose what you can infer, with why. Ask
   what only the user knows, such as whether something is decided, with no proposal: a proposal is
   taken, and the document then states what no one decided. For an existing document, propose the
   plan it shows. When every point is agreed, show the plan whole and go on once the user agrees.
3. Write the generator's CCS at `.writ/{target}-make.yaml`, each value a quoted string:

    ```yaml
    focal_entities:
      - work: "<the document's path>"
    retrieved_artifacts:
      - plan: "<the plan's path>"
      - essentials: "<pith>/references/essentials/doc.md, and one entry each for readme.md, design.md or prompt.md when the document is one>"
      - style: "<pith>/references/style.md"
      - material: "<the existing document, if any>"
    constraints:
      - language: "<the plan's language>"
    ```

   Call `writ:make` with the CCS path. When it returns gaps, ask the user each, one per message,
   write the answer to the plan, delete the gap from the CCS, and call it again.
4. Write the first user's CCS at `.writ/{target}-use.yaml` in the form `<pith>/skills/up/SKILL.md`
   step 4 shows, with the reader as receiver and what they do after reading as the use, and call
   `pith:use` with its path. Never put the plan or the pass condition in it.
5. Lay the first user's report beside the pass condition, and give each question a Good or More at
   `path:line`, quoting the document or the report, checking each Good as strictly as each More. Go
   by the CCS's `episodic_trace` where the report and it differ.
6. For each More that stops the reader from doing what the pass condition says: if the plan tells
   how to fix it, add `  - fix: "<path:line, and what the reader struggled with>"` and
   `  - keep: "<each Good>"` under `goal_orientation` in the make CCS and call `writ:make`; then read
   that place as the first user did and see that it no longer happens. Never call `pith:use` again.
   If the plan does not tell, ask the user and write the answer to the plan first. Leave any other
   More, with the reason.
7. Write the result in the form of `<pith>/references/result-form.md` at
   `.writ/open/{NN}-report-{target}.md`, each fixed More as the Good it now is, and run
   `python3 <pith>/scripts/check_result.py` on it until it passes. Delete `.writ/{target}-make.yaml`
   and `.writ/{target}-use.yaml` by those exact paths. Answer, in the user's language: whether the document can be handed on as it is, each More you left with what
   happened and why you left it, and the result file's path.
