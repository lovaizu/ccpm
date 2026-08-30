# Adoption evaluation, round 2 — the strengthened-writ rebuild against the current design

Decides the question held open on PR #19 since 2026-08-30: does `aiya/docs/design.md` become the writ
rebuild, or stay as it is?

Evidence: [`4-rebuild2/trials.md`](./4-rebuild2/trials.md) (head-to-head record, verbatim prompt),
[`4-rebuild2/note.md`](./4-rebuild2/note.md) (the rebuild's own what-changed note),
[`4-rebuild2/reader-A.md`](./4-rebuild2/reader-A.md) · [`reader-A2.md`](./4-rebuild2/reader-A2.md) ·
[`reader-B.md`](./4-rebuild2/reader-B.md) (raw reader reports).

## Recommendation: reject the rebuild, and do not patch the current document either

Neither document is the answer, and the reason is now measurable rather than arguable. **Adopt
neither; fix the format both are written to, then rebuild once against the corrected format.**

The one-line case: doc-B-2 costs 43% more words for the same reader effort, ships one confirmed
contradiction on the exact claim the reader was sent to judge, and carries two floor-level defects its
own self-check passed — while the single change all four readers across both rounds asked for is one
neither document is permitted to make.

## What this run measured that the last one could not

Round 1's comparison was void as a test of the procedure: the rebuild had been drafted straight after a
full read of the source, leaving 127 shared 8-token spans. Writ's new step-10 carryover item — a
mechanical side-by-side measurement with the bar "having been told to rebuild is not evidence that you
did" — **fired on this run and failed the first render**: 177 spans, longest 312 tokens, 70.87% of the
document inside a shared span. The run rebuilt from meaning and finished at 6 spans / 0.64%, every
survivor a citation, an identifier, or mermaid syntax.

That is writ's added mechanism doing exactly the work the feedback asked of it, and it is what makes
this round's result a statement about the procedure. The finding it enables is the next section.

## The result: the procedure's output no longer wins

| | Round 1 | Round 2 (this run) |
|---|---|---|
| Independence of the rebuild | 7.3% residue, unmeasured until after the fact | 0.64%, measured during the run |
| doc-A effort | 4 | 4 |
| Rebuild effort | **3** | **4** |
| Rebuild length | +27% | **+43%** |
| Rebuild verdict | QUALIFIED | QUALIFIED, **leaning NO** |

Round 1's headline — "the blank-page rebuild won" — does not reproduce. With the carryover actually
removed and three writ trial rounds run on the rebuild, the rebuild reads no more easily than the
document it was meant to replace, and costs 2,796 more words to read no better.

The honest reading is not "writ got worse." Round 1's win was measured on a document that had silently
inherited 70% of its predecessor's phrasing; that number was never a measurement of the procedure. This
round's tie is the first real one, and a tie against a hand-patched document is not a reason to adopt a
document 43% longer.

## The change every reader asks for is one neither document may make

Four fresh readers, two rounds, two independently-written documents, one prescription in near-identical
words: **put the discharge at the front.**

- doc-A's reader: "put the whole discharge in one place at the front — the two properties, all six
  carriers, *and the residual linear terms*."
- doc-B-2's reader: "put the §4.6 verdict at the front… Every mechanism after that would then read as
  evidence for a claim I already hold, instead of as promises I have to retroactively downgrade."

Neither document does it, and neither may. `aiya/references/design.md` gives chapter 1 "the properties
the solution must guarantee" and assigns the discharge of those properties to **no chapter at all**, so
both documents put it where it fits last — §4.6, at the end of the story. doc-B-2's reader named the
cost exactly: from the headings it predicted a document arguing the mechanisms work; the body argues
they are not enforced. "That is an inversion, not a nuance."

A second format finding has the same shape. The format says of chapter 5, "Format definitions live
here." Both documents defer every schema out of chapter 5, and both readers dead-ended at the identical
place — the CCS's nine components, unavailable in the document that is meant to be the reference, at
the moment they needed it to size the mechanism they were judging.

**Two defects, each independently confirmed by readers on two documents written from different
sentences. Neither belongs to writ or to either document. They belong to the format**, which is
`aiya/references/design.md` — a shipped artifact of the plugin, and the owner's.

This is why "adopt one of the two" is the wrong question. Whichever wins, the format re-imposes the
same inversion on the next rebuild.

## What each document does better, stated fairly

**doc-B-2 is better on three counts, all verified.**

1. *Status marking.* doc-A marks the run-state proposal `(proposed)` once across ten places that
   reference it; its reader stumbled precisely there ("I do not know whether resume works as described
   or is a proposal"). doc-B-2 marks all seven mentions and writes them in the conditional. Writ's new
   step-1 status pass produced this, and it fixed a defect a reader independently reported in the other
   document.
2. *Errors of fact corrected.* The reading wall stated so as to exclude documents the Conductor must
   read; "artifact" carrying three senses; the "structural" credit for the omitted spawn tool that §5.2
   discounts — all real defects in doc-A, all caught by the rebuild's trials, and the last of them is
   doc-A's reader's stumble 19.
3. *Honesty made explicit.* doc-B-2 states "none of the six legs is enforced" and walks all six. Its
   reader endorsed the call. doc-A leaves the arithmetic implicit, and both its readers did it by hand
   and lost confidence in the counts while doing so.

**doc-B-2 is worse on four, also verified.**

1. *One confirmed unfixed contradiction, on the decisive claim.* `design.md:197` says the 2,000-byte
   ceiling "governs the file however wide the wave was — it fails nothing"; `:199` says growth is
   sub-linear "under a ceiling that stays put." The reader: "the sharpest confusion in the document,"
   sitting "directly on top of the property I was asked to judge." The rebuild's note disclosed it as
   the one outstanding, unverified defect at the three-round cap; the head-to-head confirms it.
2. *Two floor-level tells its own self-check passed.* `design.md:227` duplicates a sentence
   near-verbatim thirty words later in the same paragraph — tell #2, and the self-check recorded the
   restatement item as fixed. `design.md:91`'s chain diagram has one arrow running Plan→Purpose while
   the other two run Purpose→Plan and the prose says the opposite — in the diagram round 3 had just
   edited. The author-run floor check passed both.
3. *The declared composite's promise is false.* Its head note says neither part borrows the other's
   reader; part 1 defers into chapter 5 roughly two dozen times, and the reader's first stumble is
   exactly that. The composite made the boundary explicit without making the parts separable.
4. *Length bought nothing.* +43%, spread across every chapter (ch1 +52%, ch2 +58%, ch4 +54%, ch5 +46%),
   for an identical effort score.

## Writ findings this run produced

Not for this session to act on — sent as feedback, as round 1's were.

1. **The carryover mechanism works, and the failure it caught locates the real leak in step 4, not
   step 7.** Closing the input at step 7 protected nothing because the outline had already transcribed
   the source. Step 4's "write every bullet in your own words" is the load-bearing instruction and the
   one that broke. Worth considering whether the carryover measurement belongs at step 5, on the filled
   outline, where a failure costs one re-fill instead of a whole re-render.
2. **The author-run floor check passes while a fresh reader finds floor-level tells.** A duplicated
   sentence and a reversed diagram arrow survived step 9, step 10, and three trial rounds — then a
   fresh reader found both. Steps 9–10 are the author checking their own prose, which is the thing step
   11 exists to replace; the tells that survive are the ones the curse of knowledge hides.
3. **The three-round cap shipped a confirmed defect on the document's decisive claim.** The cap did its
   job — the note names the residual honestly. But the repair landed *after* the last trial, so nothing
   verified it, and the head-to-head reader confirms it did not work. A fix applied after the final
   trial is unverified by construction; worth considering whether the last round must end on a trial,
   not on a fix.
4. **The declined length measure (D-10) has its counter-case now.** Writ declined it because round 1's
   growth bought easier reading. Round 2 is the same procedure producing more growth and no gain — the
   evidence the decline said would reopen it. The bar need not be a length cap; a recorded ratio the
   author must argue for would have surfaced this during the run rather than after it.
5. **A declared composite whose parts cross-refer two dozen times is not two documents.** Step 3's
   sanctioned composite requires each part to stand alone for its reader. This one does not, and its own
   note says so. Worth considering whether the composite needs an admission test — a part that cannot
   be read without the other is the split answer, not the composite answer.

## What survives either adoption, and still needs the owner

Ten design-level objections, reproduced across both rounds by readers who could not see each other's
document. They are properties of the design and no rewrite removes one. Listed in full in
[`4-rebuild2/trials.md`](./4-rebuild2/trials.md#what-survives-either-adoption); the ones that decide a
reader's verdict:

- The two-mechanisms framing versus the six legs the discharge needs.
- Drift's second form — the stale plan faithfully completed — has no detector and no trace.
- Bounded context is claimed for the working state; the transcript is outside it and is cut back by a
  human typing three commands, and the concession sits where an auditing reader will not look.
- The Verdict intake is linear in wave width, contradicting §4.2's "one bounded state per wave"
  (**new this round**, from doc-A's second reader).
- Nothing measures whether drift detection works.

## Proposed next steps, for the owner's ruling

1. **Reject doc-B-2 for adoption**; `aiya/docs/design.md` stays at `d7b63f9` for now.
2. **Fix `aiya/references/design.md`** — the format — on the two findings above: give the discharge of
   chapter 1's properties a home at the front of the argument, and settle whether chapter 5 holds format
   definitions or points at them. This is a shipped plugin artifact, so it is a design decision, not
   editing.
3. **Rebuild once against the corrected format**, and adopt or reject that result.
4. **Send the five writ findings** to PR #15, as round 1's were.
5. **Rule separately on the ten design-level findings**, which no document choice touches — and on R1
   and R3, still outstanding from round 4.

Step 2 is the one that needs the owner's decision before anything else moves; steps 1 and 4 need only
assent.

## Coverage of this evaluation

Checked: both documents read end to end by fresh readers under an identical, now-recorded prompt; every
quotation in the "worse" section verified by line against `4-rebuild2/design.md`; doc-A's `(proposed)`
count and its ten run-state references verified by grep; the format's chapter assignments read directly
from `aiya/references/design.md`; word counts and per-chapter growth measured.

Not checked: whether the corrected format would in fact reduce reader effort — that is what step 3
would measure, and it is a prediction here, not a result. Whether doc-B-2's length would fall to a
fourth trial round; the three-round cap stopped the loop. The rebuild's carryover figures are taken from
its own mechanical measurement and were not independently re-derived.
