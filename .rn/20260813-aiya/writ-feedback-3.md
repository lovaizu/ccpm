# Round-3 feedback to writ — the strengthened procedure was re-run, and the binding gap moved

Addressed to the writ session. **Input to think from, not a patch list** — weigh each finding against
writ's purpose before changing anything.

Findings 1 and 2 are new and load-bearing; they were not in the PR #15 comment posted 2026-08-30.
Findings 3–7 are that comment, restated here so this file stands alone.

## The run

`aiya/docs/design.md` was rebuilt **from a blank page** by `/writ:up` at 4787745, in a subagent, as a
**declared composite** (ch1–4 article / ch5–7 reference). The step-2 reader and the composite shape
were supplied as owner-ratified givens; the run-state proposal was supplied as step-1 status context.
Then both documents went to fresh-context readers under an identical, verbatim-recorded prompt with
neutral filenames — neither reader knew which document it held or that a second existed.

- **doc-A** — the current document, 6,557 words: writ-rebuilt in round 1, then patched over four
  reader-trial rounds.
- **doc-B-2** — this rebuild, 9,353 words.

**Result: both QUALIFIED, both effort 4, the rebuild 43% longer.** Round 1's effort-3 win does not
reproduce.

Evidence, all on branch `worktree-aiya` under `.rn/20260813-aiya/`:
`checks/4-rebuild2/trials.md` (head-to-head record, verbatim prompt) ·
`checks/4-rebuild2/note.md` (the rebuild's own what-changed note) ·
`checks/4-rebuild2/reader-A.md` · `reader-A2.md` · `reader-B.md` (raw reader reports) ·
`checks/4-rebuild2-eval.md` (the adoption evaluation).

## 0. First, the mechanism you added worked

Finding 1 of the last round asked whether "build fresh" could be made a mechanism. It can, and it was:
step 10's carryover item **failed this run's first render** and forced a rebuild.

| | First render | After rebuild-from-meaning |
|---|---|---|
| Maximal shared spans ≥ 8 tokens | **177** | **6** |
| Longest span | **312 tokens** | **13 tokens** |
| Document inside a shared span | **70.87%** | **0.64%** |

Note what that also says about round 1: the document that "won" on effort 3 had silently inherited most
of its predecessor's phrasing, so that number was never a measurement of writ. **This round's tie is the
first honest comparison**, and it is the ground for everything below.

---

## 1. The heading admission test is subtractive only — there is no rule for a slot the reader needs and the format lacks

This is the finding that decides what happens next on the aiya side, and it is the one to weigh first.

**Four fresh readers, across two rounds, on two documents written from different sentences, prescribed
the same single change in near-identical words: _put the discharge at the front._**

> doc-A's reader: "put the whole discharge in one place at the front — the two properties, all six
> carriers, *and the residual linear terms*."
>
> doc-B-2's reader: "put the §4.6 verdict at the front… Every mechanism after that would then read as
> evidence for a claim I already hold, instead of as promises I have to retroactively downgrade."

**writ detected this every single time.** Step 11 asks "do the headings alone carry the argument?", and
all three trial rounds reported the break — round 1's part-1 trial: "the two properties never appeared
in a heading until the last one." The ceiling says it too: "a single load-bearing thread with the
conclusion first; headings carrying the argument alone." Nothing was missed.

**What writ could not do was act on it**, and the reason is in step 3's wording:

> Every heading must earn admission from the step-2 reader: it stays only if that reader needs it to
> reach the purpose. A heading serving anyone else … stays out. … A user-supplied outline or format
> faces the same test slot by slot; an unjustifiable slot is an axis conflict — raise it with the user
> …, never fill it silently.

Every verdict this test can return is **removal**: keep the slot, or drop it / raise it and proceed.
There is no verdict for *"the reader needs a slot this format does not have."* So the run did what writ
says — recorded three axis conflicts in its note and proceeded — and the only structural repair
available to it was renaming a heading inside chapter 2. The reader's response to that rename:
"contradicted by its own second sentence."

The result is a defect that survives every round of a procedure that correctly diagnoses it, on two
independently written documents.

Worth considering: should the slot-by-slot test be **two-directional** — a reader need with no slot to
carry it is as much an axis conflict as a slot with no reader, and it should be raised as a *proposed
slot*, with the reader evidence attached, rather than absorbed as prose inside whatever slot is
nearest? Note this is the same shape as last round's finding 5, which you declined for content: a drop
rule with no add rule. Here the missing add rule is structural, and the evidence that it bites is four
readers converging on one prescription.

## 2. writ's own article skeleton is not conclusion-first

Related, and independent of any supplied format. The five axes give the article axis this skeleton:

> 1. The question (the why-question this document answers, 1–2 sentences)
> 2. The substance (per unit: claim → why → implications and connections …)
> 3. In closing (what was gained, the limits, pointers onward)

The answer to the question is distributed through *the substance* and summed in *in closing*. That is
question → middle → answer. The ceiling in the same file says "a single load-bearing thread with **the
conclusion first**."

**The skeleton and the ceiling disagree**, and a run that follows the skeleton faithfully lands where
both aiya documents landed: the reader builds a model on the framing and has to retroactively downgrade
it at the end. doc-B-2's reader called that "an inversion, not a nuance."

This does not affect the aiya design document — it uses a product-specific format, not writ's axis —
so it is offered purely as writ's own business, and it is the reason finding 1 may not be only about
supplied formats.

---

## 3. The carryover leak was in step 4, not step 7

The run's own diagnosis: the filled outline had been written **with the input open** and, for chapters
5–7, transcribed the source's sentences. Closing the input at step 7 protected nothing, because the
wording had already crossed into the outline. Step 4's "write every bullet in your own words" is the
load-bearing instruction and the one that broke — invisible until a whole document had been rendered
from it.

Worth considering: does the carryover measurement belong at **step 5**, run against the filled outline,
where a failure costs one re-fill instead of a re-render? Step 10 catches it, but by then the cost of the
fix is the whole document — and the second render is what a tired run would be tempted to skip.

## 4. The author-run floor check passes while a fresh reader finds floor-level tells

Step 10 recorded PASS on "no prose repeats what a diagram carries"; step 9 reported one restatement
found and fixed. A fresh reader then found, in the delivered document:

- `design.md:227` — "Whatever the project lacks becomes Steps on the Plan." and, **thirty words later
  in the same paragraph**, "whatever a project lacks becomes Steps on the Plan, written in aiya's
  formats." Verified. That is tell #2, surviving step 9, step 10, and three trial rounds.
- `design.md:91` — the chain diagram's first arrow, `PP["Plan"] -.->|"translated into Steps"| P`, runs
  Plan→Purpose while the other two run Purpose→Plan and the prose says the Plan converts a signed
  document into Steps. One arrow points the wrong way — **in the diagram round 3 had just edited.**

Steps 9 and 10 are the author checking their own prose, which is the thing step 11 exists to replace.
These two are exactly the class the curse of knowledge hides: the author reads the intended sentence,
not the written one. Worth considering whether the floor checklist and the form items belong in the
reader trial's brief as well as the author's.

## 5. A fix applied after the final trial is unverified by construction

The three-round cap did its job — the note names the residual honestly and says the width-versus-size
contradiction was repaired *after* round 3 reported it, with no fourth trial to confirm it.

The head-to-head then confirmed **the repair did not work.** The reader called it "the sharpest
confusion in the document", sitting "directly on top of the property I was asked to judge":

> `design.md:197` — a 2,000-byte ceiling "governs the file however wide the wave was — **it fails
> nothing**"
> `design.md:199` — growth is sub-linear "**under a ceiling that stays put**"

A fixed ceiling that holds is a constant bound; one that fails nothing is no bound at all.

Worth considering: should the loop be required to **end on a trial, not on a fix**? The cap is right,
but as written it permits the last action to be an unverified edit — at exactly the place that matters
most, since the last round's stumbles are the hardest ones.

## 6. D-10's counter-case has arrived

You declined the length measure on the evidence that round 1's 27% growth *bought* easier reading, and
wrote: "if a later run shows growth that the reader trial passes and a human still judges bloated, that
is the evidence that would reopen this."

Round 2 is stronger than that. The same procedure produced **+43%** and **no gain at all** — effort 4
against effort 4. Growth by chapter: ch1 +52%, ch2 +58%, ch3 +19%, ch4 +54%, ch5 +46%, ch6 +32%,
ch7 +11%. The story chapters grew fastest, so this is not contract detail either.

Your reasoning against a *bar* still holds — a number competing with reader effort is a bad instrument.
But the case for a **recorded ratio the author must argue for** is now supported: it would have surfaced
the growth during the run, when a fill could still be re-admitted, instead of after it. Reopening D-10
as "record and justify", not "cap", is what this evidence supports.

## 7. A composite whose parts cross-refer two dozen times is not two documents

The declared composite made the boundary explicit and did not make the parts separable. The document's
own head note promises neither part borrows the other's reader; the part-1 reader's **first stumble** is
that part 1 defers into chapter 5 continuously (§5.1, §5.3, §5.4, §5.5, §5.6, §5.7), "so I had to decide
on every deferral whether the argument was still complete without it." The note counts roughly two dozen
such pointers and flags them itself.

Both part-1 readers, in both rounds, then left chapters 1–4 to decide — precisely because the CCS's
bound is deferred to §5.4.

Worth considering: does the composite need an **admission test** of its own — a part that cannot be read
to its purpose without the other is the split answer, not the composite answer? As it stands, "declared
composite" is available as the cheaper option at exactly the moment the split is the right one.

---

## What the aiya side is waiting for

The owner has ruled that the aiya design document **stays as it is** and is not hand-patched. The next
rebuild happens **after** writ has taken whatever it takes from the above, and the resulting document is
then adopted or rejected on its own merits.

Finding 1 is the one that decides whether that next run can succeed. If the slot-by-slot test stays
subtractive, the next rebuild inherits the same inversion, because `aiya/references/design.md` assigns
chapter 1 "the properties the solution must guarantee" and assigns their **discharge to no chapter at
all** — and both documents therefore put it at §4.6, at the end of the story. A second instance of the
same shape: the format says of chapter 5 "Format definitions live here", both documents defer every
schema out of it, and both readers dead-ended at the identical place (the CCS's nine components,
unavailable in the document meant to be the reference).

Those two are the aiya format's defects, and the owner owns them. The question for writ is whether a run
should be able to **surface them as proposed slots with reader evidence**, instead of recording them as
conflicts and proceeding.
