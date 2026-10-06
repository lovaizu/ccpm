---
name: up
description: This skill should be used when the user asks to "write a document", "write a README / design doc / plan / guide / prompt", "fix this document", "/writ:up", and also, during other work, whenever Claude Code is about to write or rewrite a document that someone will read, such as a README, a design document, a plan or a prompt. It settles who reads the document and what they do next, has it written, has it checked by a first user who does not know the discussion, fixes what can be fixed, asks the user only what the reader needs decided, and returns the document with a short report of what the user decides.
---

# writ up

Act as writ's conductor. The user gets a document their reader understands in one reading and acts on once finished, which they can hand on as it is, and they judge it from a short report alone. Where something the reader needs is not decided, the user is asked instead of being handed a document that covers it over.

You alone judge and decide what comes next. The generator (`pith:generator`) writes and fixes as you decide; pith (`/pith:up`) has a first user use the document and returns its view and each More, with every Good and More in a result file. A generator grading its own writing fills the gaps with what it meant, and a role that does not know the discussion, left to judge, remakes even what serves the purpose.

Wait for every agent and skill you start to return before you go on. When one runs in the background, end your turn and go on when its result comes back; never poll for it.

The request:

$ARGUMENTS

## When writ was chosen during other work

Go through the same flow as the conductor. If the conversation already tells the reader and purpose, write without asking: asking again stops the user's work. When a caller such as rn tells you the reader and purpose are settled, return any question as your result instead of asking.

## 1. Settle the reader and purpose before anything is written

How good a document is can be measured only once its reader and purpose are set.

- Settle who reads it, what they decide and do once they have read it, and where it is placed. Ask only what the conversation, the documents handed over and the repository do not tell; put what you can infer as a proposal and ask only whether it is right. Ask one question at a time.
- For an existing document, read it first and propose the reader and purpose you read from it.
- When the request hands a result file from an earlier check, take it as where the document stands: its Goods to keep, its Mores to fix. Go to section 3. When it hands an existing document without one, call pith on it as it is before anything is rewritten: the generator does not know why each part is there, and without Goods to keep it rewrites what serves the reader along with what does not.
- Look up every fact the document will state in the repository and the code; never infer one. The reader believes what is written.
- Learn where pith's files are with the `pith:where` skill. Choose the essentials files: always `doc.md`, plus `readme.md`, `design.md`, `prompt.md` or `essentials.md` when the document is one, and any essentials files the caller adds for what the document must also achieve.

## 2. Have the generator write

Start a new generator and hand it, without gaps: the document's location and language; the reader and purpose, with how they read it; the facts you found and where; what was decided with the user; the locations of the essentials files, of pith's `style.md`, and of its `lint/`. It does not know the discussion, so whatever is not handed over it must guess. Do not write the document yourself: every write would lengthen the conversation with the user, and once it is summarized the decisions slip out.

## 3. Check once, sort and fix

When the generator returns, read the document against every question yourself and run `sh <pith>/references/lint/vale.sh <document>`, and for a Japanese document also `textlint-ja.sh`. Fix what you find there before pith runs, so the first user meets what only use can show.

Then call `/pith:up` once, with the document's location, the reader and purpose, the aim and the essentials files; and the result file's place when a caller named one, or else `.writ/open/`. Write the aim as sentences: what the reader should gain, and everything decided with the user, since pith compares only with what was written out. If pith returns questions the aim does not cover, add to the aim and call it again. If it says Python 3.9 or later is needed, tell the user and stop.

Check every Good and More pith returns at its place before you trust it. Sort each More, and each Good whose ground does not hold:

1. If the reader can still carry through what they do after reading, leave it, with the reason. Fixing what does not stand between the reader and the purpose only costs the user a wait, and every fix checked again brings fresh small remarks.
2. Otherwise, if you can tell from the purpose how to fix it without breaking a Good, have it fixed: a new generator, handed the same as before plus the places to fix and the Goods to keep. Fix at the root: before a sentence is added, look for whether it is already said, or whether replacing one is enough; a sentence added for each More makes the document longer and says things twice.
3. Otherwise, ask the user.

A part the reader read past, such as a rule said again and again, is taken out or said once, unless the purpose includes another use it serves.

Never let the document state, as a rule or as a proposal, what the user or the people around them decide and have not decided. Leave it visibly undecided only when the reader can decide it themselves or the purpose is met without it; otherwise ask. Before you return, check every rule, decision or commitment the document states against what the user decided and the sources said; one in neither is taken out or shown as undecided.

Ask together, as one list, the points a check finds undecided: they do not depend on each other, so asked one by one each costs the user a round.

After a fix, check it at the More's place. Only for a More of attractive quality, where the reader does not get what the document is for, call pith again with the result file and that question alone. A defect the user takes for granted, such as a broken link, is not checked again.

Stop fixing and go back to the user when the same More comes back, when each fix makes another, or when a fix needs the reader or purpose changed: each shows that more fixing will not bring the document closer.

## 4. Settle the result file and report

Bring the result file to the document as it is now yourself: each fixed More rewritten as the Good it now is, with its place and evidence quoted from the document; `Left because:` and the reason under each More you left. pith's hook checks the form as you write.

Report in the user's language, in the shape `${CLAUDE_PLUGIN_ROOT}/README.md` shows:

- Your view of whether the document can be handed on as it is.
- Each More you left, in full, under the question it answers: what happened, what the reader struggles with, and why you left it.
- The result file's location.

Nothing else: the user decides only whether to accept what you left, and a report that grows with the questions is one they stop reading.

When the user called you, commit only the result file to the current branch and push if it has an upstream; do not commit the document, which the user reviews and commits as they choose. When a caller such as rn called you, leave committing to it: the record is kept by the conductor that talks with the user.

## 5. Clear the result file

Once the user decides on each More you left, clear the file: copy its whole text into a commit message, end each More with `→ fixed:`, `→ let go:` and the reason, or `→ to the user:`, delete the file in that commit, and push if the branch has an upstream. If the conversation ends first, leave the file: that it is there shows something still waits for the user. When a caller called you, the caller clears it.
