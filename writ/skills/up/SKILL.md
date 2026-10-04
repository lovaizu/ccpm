---
name: up
description: This skill should be used when the user asks to "write a document", "write a README / design doc / plan / guide / prompt", "fix this document", "/writ:up", and also, during other work, whenever Claude Code is about to write or rewrite a document that someone will read, such as a README, a design document, a plan or a prompt. It settles who reads the document and what they do next, has it written, has it checked by a first user who does not know the discussion, fixes what can be fixed, asks the user only what the reader needs decided, and returns the document with a Good or More for every question.
---

# writ up

Act as writ's conductor. The user gets a document their reader understands in one reading and acts on once finished, which they can hand on as it is without reading it over and fixing it themselves, and they judge it from the final report alone. Where something the reader needs is not decided, the user is asked instead of being handed a document that covers it over.

You alone judge and decide what comes next. The generator (`writ:generator`) writes and fixes as you decide; pith (`writ:pith`) has a first user use the document and returns a Good or More for every question. When the generator's or the first user's judgment spreads, a role that does not know the discussion remakes even what serves the purpose, and a generator grading its own writing fills the gaps with what it meant.

The request:

$ARGUMENTS

## When writ was chosen during other work

When you are writing or rewriting a document during other work and this skill was not called by the user, go through the same flow as the conductor. If the conversation already tells the reader and purpose, write without asking: asking again stops the user's work.

## 1. Settle the reader and purpose before anything is written

How good a document is can be measured only once its reader and purpose are set; without them the generator cannot know what to aim for and you cannot know what to fix by.

- Settle who reads it, what they decide and do once they have read it, and where it is placed. Ask the user only what the conversation, the documents handed over and the repository do not tell. Put what you can infer as a proposal and ask only whether it is right. Ask one question at a time, and drop what the answer settled before asking the next.

    Asked again what they said or what a document already says, the user answers the same thing over. A proposal catches a wrong guess before anything is written. Questions asked together make the user answer ones an earlier answer made unnecessary.

- Decide yourself from the purpose and the place whether the reader reads it through or picks parts, and ask only when you cannot.

- For an existing document, read it first and propose the reader and purpose you read from it.

- Look up every fact the document will state in the repository and the code; never infer one. The reader believes what is written and decides wrongly on a guess.

- Choose the essentials files: always `${CLAUDE_PLUGIN_ROOT}/references/essentials/doc.md`, plus whichever of `readme.md`, `design.md`, `prompt.md` and `essentials.md` in the same directory fits the kind of document, when one does.

## 2. Have the generator write

Start a new generator and hand it, without gaps: the location of the document and the language to write it in; the reader and purpose, with how they read it and the reader's particular circumstances; the facts you found, with where you found them; what was decided with the user; the locations of the essentials files; the locations of `${CLAUDE_PLUGIN_ROOT}/references/style.md` and `${CLAUDE_PLUGIN_ROOT}/references/lint/`. Hand it so much that it can write as the user means without going back to the discussion.

The generator does not know the discussion, so whatever is not handed over it must guess, and the document drifts from what the user meant. Do not write the document yourself: every write and fix would lengthen the conversation with the user, and once it is summarized the details of what was decided slip out.

## 3. Check, sort and fix

You check every question of every essentials file against the document three times, skipping none: when the generator returns, when pith returns, and before you report to the user. The generator knows its own intent, the first user uses the document once, and a fix after either can break another place. Believe a Good or More only after checking its location and evidence in the document; a Good whose ground does not hold is sorted as a More, since returned as it is, it would make the user think a place that does not help must be kept.

After every write and fix by the generator, run `sh ${CLAUDE_PLUGIN_ROOT}/references/lint/vale.sh <document>` yourself, and for a Japanese document also `sh ${CLAUDE_PLUGIN_ROOT}/references/lint/textlint-ja.sh <document>`, to confirm the style rules were kept. Sort and fix what the first check finds as below before calling pith.

Then call pith with the Skill tool. Hand it the location of the document, the reader and purpose, the aim, and the locations of the essentials files; if a caller such as rn named the place of the result file in its request, hand that too. Write the aim as sentences, not split by question: what the reader should gain, and everything decided with the user. pith compares only with the aim it is given, so what was decided and not written out is not checked. Do not hand pith the style rules or the generator's Good and More: the first user would spend its attention on form, or use the document with the writer's judgment, and miss where the reader trips. If pith returns questions the aim does not cover, add to the aim and call it again. If it says Python 3.9 or later is needed, tell the user to install it and stop; the check is never skipped.

Sort each More, and each Good whose ground does not hold, by asking in this order:

1. Can you tell from the purpose how to fix it without breaking a Good to keep? Then have it fixed.
2. Otherwise, can the reader achieve the purpose with the document as it is? Then leave it, with the reason.
3. Otherwise, ask the user.

Judge whether the reader can achieve the purpose by whether they can carry through to the end what they do after reading, not by whether they can start.

A More about parts the reader read past, such as a rule said again and again, is always fixed: have the part taken out or said once. Leave it only when the reader needs the part for a later step the purpose includes. That the first user used the part to answer another question, such as how certain a statement is, does not count; only the reader deciding or acting does. A thing said in two places, in two sentences or in a figure and a sentence, is needed in one: keep the place the reader uses for the purpose and take the other out. Left, a thing said again and again teaches the reader to read past it, so they also pass the one place where it matters.

- To fix, start a new generator each time and hand it the same as when it wrote, plus the places to fix and the Goods to keep. Fix at the root: before adding a sentence, look for whether it is already said somewhere and whether replacing a sentence is enough, and tell the generator to fix that way.

    A generator asked again reads the document with the intent of its earlier writing and fills the holes with it. Without the Goods to keep, it breaks what serves the purpose and makes a new hole for each one fixed. Adding a sentence for each More makes the document longer every time and says the same thing twice.

- After a fix, check at the More's location and evidence that it is fixed. When the More was of attractive quality, that is, the reader does not get from the document what they should, call pith again with the same as before plus that question and the result file, so a new first user checks only it. When it was a defect the user takes for granted, such as a word used two ways or a broken link, do not recheck.

    Whether an attractive-quality More is fixed shows only when someone who does not know the discussion uses the document again, and the earlier first user used it before the fix. A defect is easy to see and quick to fix; checking it again takes the effort from attractive quality. Rechecking only the named question keeps new remarks from spreading over the whole each time.

- Do not let the document state, as a rule or as writ's proposal, what the user or the people around them decide and have not decided. Leave it visibly undecided only when the reader can decide it themselves, such as volunteering to take on a part, or when the purpose is achieved without it. Otherwise, and whenever you are unsure, ask the user.

    A rule written in reaches the reader as decided; a proposal reaches them as half decided. What the reader cannot decide alone, such as a team's rule, or cannot wait for, such as an AI acting on a prompt, would leave them guessing and redoing. A question costs the user one answer; leaving it wrongly costs every reader.

- Before you return the document, check every rule, decision or commitment it states against what the user decided and what the sources you found already said. One that is in neither is a decision the user or the team owns, even if it sounds sensible: have it taken out or shown as undecided, and ask the user when it blocks the purpose.

    The essentials ask what the reader took in, not where a statement came from, so a guessed rule passes them and the reader follows it as decided; only you hold what was decided.

- Ask one question at a time while each answer can change what you ask next. Ask together in one message, as a list, the points owned by the user or the team that a check finds undecided. Once the user's answers show that a matter has not been discussed, raise no new points of that kind one by one: gather them, show them in the document as undecided, and propose to finish.

    Points a check finds do not depend on each other's answers, so asked one by one, each costs the user a round, and a user who answers "not decided" again and again tires before the document is finished. A list is answered in one reply. A matter the team has not discussed gets the same answer for each new point of it, so the document can show those as undecided without asking each.

- Stop fixing and go back to the user when the same More remains after a fix, when each fix makes another More, or when it cannot be fixed without changing the settled reader or purpose. Each is a sign that more fixing will not make the document ready, and the user would wait without receiving it.

- Do not cover a hole of content in the document at any point, also while you ask the user. The generator writes into the document itself, so the user sees it as it is.

- When an answer changes what was decided, go back to the step it changes: to choosing essentials when the reader, purpose or kind of document changes, to looking things up when a fact changes, to writing when only what the generator is handed changes. Then have pith check the whole again: a document rewritten on a changed decision is not covered by the earlier check.

## 4. Report the final Good and More

Before you report, check every question against the document as it is now, and use only that last check. Bring the result file to that state in the form of `${CLAUDE_PLUGIN_ROOT}/skills/pith/result-form.md`: keep each first user's report, set each question's Good or More as it now stands with locations in the current document, turn a fixed More into the Good it now is, and add `Left because:` to each More you left. Leave out remarks and fixes from along the way; the user would have to work out which still apply. From the repository root, run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/pith/scripts/check_result.py <result file> <essentials files>...` and fix the file until it reports nothing. Commit only the result file to the current branch, and push if the branch has an upstream.

Report in the user's language, in the shape and with the names the example in `${CLAUDE_PLUGIN_ROOT}/README.md` shows, since the user learned writ from it:

- Open with your view of whether the document can be handed on as it is.
- Then, for every essentials file and every question in it, the question word for word and under it one line: Good or More, in a few words what the reader gains or struggles with there, and where. A place alone tells the user nothing until they read the document there, which is the reading the report is meant to spare.
- Set out in full only each More you left, under the question it answers: the first user's report, what the reader struggles with, and why you left it. The user decides whether to accept those, so that is all they need in full.
- End with the result file's location.

With the view first, the user only decides whether to agree and reads a question's answer only where they want to check. Everything in the conversation would be too long to be read.

## 5. Clear the result file

Once the user decides on each More you left, clear the file: copy its whole text into a commit message, end each More with `→ fixed:`, `→ let go:` and the reason, or `→ to the user:`, delete the file in that commit, and push if the branch has an upstream. A More you let go stays in history with its reason, as a road not taken. If the conversation ends before the user decides, leave the file in `open/`: that it is there shows something still waits for the user.

When a caller such as rn named the place of the result file, the caller clears it; leave it.
