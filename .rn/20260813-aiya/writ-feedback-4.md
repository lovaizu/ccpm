# Round-4 feedback to writ — the additive slot worked; three mechanisms behind it did not

The round-3 changes were run blank-page on the aiya design (input 6,557 words → 8,156). Artifacts:
`.rn/20260813-aiya/checks/4-rebuild3/` (document, note, six verbatim reader reports) and
`checks/4-rebuild3-eval.md`.

## 0. What worked

**Step 3's additive direction fired on its first field run, on exactly the defect it was built for.**
One proposed slot — the discharge, absent from the supplied format — raised with its position and
reader evidence, realized as §1.4, format file untouched. Round 3's reader called its heading the best
sentence in the file, and it is the reason the aiya side is recommending adoption after two rounds of
"adopt neither". The whole round-3 exchange paid off here.

## 1. Closing the input at step 7 protects nothing — the render leaks from memory

The carryover readings on this run:

| Point | Spans ≥8 | Longest | % of tokens in a shared span |
|---|---|---|---|
| Step 5, first fill | 58 | 24 | 17.01% |
| Step 5, after re-fill | 18 | 18 | 3.71% |
| **Step 10, first render** | **105** | **47** | **21.02%** |
| Delivered | 23 | 17 | 2.79% |

The outline was clean at 3.71% and the render came back at **21.02%**. The input was closed. What
re-entered came from the author's memory of it, which step 7's instruction does not touch. Moving the
measurement to step 5 was right and it did not remove the need at step 10 — this run needed **two**
re-fills, and the expensive one was the second.

Worth considering: step 7 currently forbids consulting the input. The failure is not consultation, so
the remedy is not a stronger prohibition. A cheap guard is a per-section reading during the render
rather than one whole-document reading after it — a section that comes back hot is re-rendered while
it is one section.

## 2. The step-5 separability walk is too weak to grant a composite

The run declared a composite (Part I argument / Part II reference), the step-5 walk passed both parts,
and **three trial rounds then overturned Part II** — every round found entries incomplete without
chapter 2, and round 1's mitigation (the vocabulary convention at Part II's head) moved nothing.
Round 3's reader read the disclosure as confirmation of the flaw rather than its mitigation.

So the author's own walk granted a composite that a reader refuted three times. The walk is the author
simulating ignorance, which is the thing step 11 exists to replace. Either the composite should not be
granted before a reader trial supports it, or the walk needs a test the author cannot pass by knowing
the other part.

## 3. A supplied prompt and the per-part trial do not compose

Step 11 requires one trial per part with that part's reader. The aiya brief supplies one verbatim
prompt for comparability across rounds — and that prompt is Part I's reader. Part II therefore ran on a
prompt written for this run, so its numbers are internally comparable and comparable to nothing else.
Writ should say what happens when a fixed prompt and a declared composite meet.

Related trial hygiene: round 3's Part I reader's tool returned the whole file in one call, so chapters
5–7 were in front of it from the start. A per-part trial needs the part in its own file, not a part of
a file the reader is asked not to read.

## 4. D-11's counter-case, again — and the effort scale may be the wrong instrument

Effort came back **4 on all six trials**, across 6,919 → 7,695 → 8,156 words. Round 2's counter-case was
43% longer for no effort movement; this is 24% for no effort movement. Two rounds, two documents, same
result.

What did move is off that scale: Part II's clean lookups 3/5 → 4/5, and the Part I verdict sharpening
from "the leg-3 claim is false" to a defensible leg-by-leg QUALIFIED. If the trial's job is to tell a
better document from a worse one, effort 1–5 is not doing it — three rounds of real fixes never moved
a point. Consider asking the reader for something that can move: what they can now conclude that they
could not before, or which specific question they can answer unaided.

## 5. The cap and the "end on a trial" rule interact badly with round 3 finding the most

Rounds 1 and 2 each named one change that was taken and confirmed. Round 3 — the cap — produced **39
stumbles, the most of any round**, and by rule none of them could be fixed. Eleven prose defects ship
unfixed, including the largest one found in the whole run ("traced" is the word five of six legs rest
on, and the document never says who reads a trace). The rule is right that a run must not end on an
unverified edit; the cost is that the sharpest reading is the one that cannot be acted on. The
changed-passages-only re-read exists for exactly this and was not reachable here, because the fix list
was not one passage.
