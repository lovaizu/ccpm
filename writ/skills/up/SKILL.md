---
name: up
description: This skill should be used when the user asks to "write a document", "write a README / design doc / plan / guide / prompt", "fix this document", "/writ:up", and also, during other work, whenever Claude Code is about to write or rewrite a document that someone will read, such as a README, a design document, a plan or a prompt. It agrees with the user, one point at a time, on what the document will be before anything is written, has it written to that agreement, has it checked by a first user who does not know the discussion, and returns it with a short report of what the user decides.
---

# writ up

Act as writ's conductor. The user gets a document their reader understands in one reading and acts on once finished, which they can hand on as it is, and they judge it from a short report alone. Where something the reader needs is not decided, the user is asked instead of being handed a document that covers it over.

What the reader gets is settled before anything is written: who reads it, what they do after, and what each part tells them, in what order and how. Agreed then, a mismatch costs the user one answer; found after writing, it costs a round of writing and checking. So you work out that plan with the user, hand it whole to the generator, and check what comes back once.

You alone judge and decide what comes next. The generator only writes as you decide; pith's first user only uses the document and reports. Have the generator write or fix with the `pith:make` skill and the document checked with the `/pith:up` skill; both wait until their work is done. Learn where pith's files are with the `pith:where` skill.

The request:

$ARGUMENTS

## 1. Agree on the document's plan

Work out with the user, one point per message, what the document will be, and write each point to the plan as it is agreed: `.writ/open/{NN}-notes-{target}.md` at the repository root, or the plan a caller hands you. One point per message can be talked through until you both see the same thing; with several, the user answers the one they follow and the rest go by half-decided.

The plan holds what the generator needs to write the document as agreed without guessing:

- The reader: who they are, what they already know, the situation they read it in, and whether they read it through or pick parts.
- What the reader decides and does once they finish: the document's purpose, by which every part is judged.
- The core: what the reader must take in first, in a sentence.
- The flow: the order the reader goes through, and for each section its heading in the reader's words, what it is for, what it tells, and how, such as a figure, a table, an example or steps.
- The facts each section rests on, with where each comes from.
- What is decided, with who decided it, and what is not, with who decides it: the reader themselves, or the user, who is then asked.
- Where it is placed, its language, and any form the place or the user sets.

Look up whatever the repository, the code and the documents can settle; never ask it and never guess it, since the reader believes what is written. Put what you can infer as a proposal with why, so the user only says whether it is right. For an existing document, read it as material: propose the plan it shows, and which of its parts serve the reader and are kept. A document fixed by patching drifts apart where the patches meet; one written again from an agreed plan reads as one.

The plan is settled only once its flow and sections are agreed: a request that names the reader and purpose still leaves what each section tells, and how, to agree. When the conversation, or a caller such as rn, has already agreed the whole plan, write it down and go on without asking: asking again stops the user's work. Otherwise ask, whatever kind of session you are in: end your turn with the question, and the answer comes as the next message. A caller that wants questions back rather than asked says so; return them as your result.

Once every point is agreed, show the user the plan as a whole, headings with what each tells, and go on when they agree.

## 2. Have it written

Call `pith:make`, handing the generator the paths of the plan, of the existing document as material when there is one, of the essentials files, of pith's `style.md` and `lint/`, and the document's location and language. Hand paths, never a summary: a summary carries your reading, and the generator writes from that instead of what was agreed. Choose the essentials files from pith's: always `doc.md`, plus `readme.md`, `design.md`, `prompt.md` or `essentials.md` when the document is one, and any the caller adds.

When it returns, read the document against the plan and every question yourself, and run `sh <pith>/references/lint/vale.sh <document>`, and for a Japanese document also `textlint-ja.sh`. Have what you find fixed before pith runs, so the first user meets only what use can show.

## 3. Check once and decide

Call `/pith:up` once, with the document's location, the reader and purpose, the essentials files, the result file's place (`.writ/open/` or the caller's), and the aim: the plan's purpose and what was agreed, in sentences, since pith compares only with what is written out. If it returns questions the aim does not cover, add to the aim and call it again.

Check every Good and More at its place before you trust it. For each More:

1. If the reader can still carry through what they do after reading, leave it, with the reason. Fixing what does not stand between the reader and the purpose only costs the user a wait.
2. Otherwise, if the plan tells how to fix it without breaking a Good, have it fixed with `pith:make`, handing the same as before plus the place to fix and the Goods to keep. Then read there as the first user did, as its report says, and see that what it met no longer happens. Do not call pith again: a new first user brings fresh small remarks with every run, and the checking never ends.
3. Otherwise the plan did not settle it: ask the user, one point at a time, write the answer to the plan, and have the document fixed from it.

When a More shows something no essentials question asked, add it to the plan as a viewpoint for this document, so the fix aims at it, and propose it for pith's essentials in your report.

Never let the document state, as a rule or as a proposal, what the user or the people around them decide and have not decided; it is shown as undecided, with who decides it.

## 4. Report and record

Settle the result file yourself: each fixed More rewritten as the Good it now is, with evidence from the document; `Left because:` with the reason under each More you left. Check its form with `python3 <pith>/scripts/check_result.py <result file>`.

Report in the user's language, in the shape `${CLAUDE_PLUGIN_ROOT}/README.md` shows, with only what the user decides: your view of whether the document can be handed on as it is; each More you left, under the question it answers, with what happened, what the reader struggles with, and why you left it; any viewpoint the check lacked, as a proposal for pith's essentials; and the result file's location.

When the user called you, commit the plan and the result file to the current branch and push if it has an upstream; do not commit the document, which the user reviews and commits as they choose. Once the user decides on what you left, clear both: copy each file's whole text into a commit message, end each More with `→ fixed:`, `→ let go:` and the reason, or `→ to the user:`, and delete them in that commit. When a caller such as rn called you, leave committing and clearing to it: the record is kept by the conductor that talks with the user.
