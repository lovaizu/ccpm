---
name: accuracy
check: accuracy
version: 0.1.0
---

# Accuracy

A deliverable, a document or code, is relied on by a reader who does not have the sources it was
made from: the decisions, the files they name and the product it tells of. Whoever holds those
sources can tell from them that the reader is given what was decided and what the product does,
no more and no less, and so acts on it without checking it again.

Each item is answered against the sources, which the reader does not have; what the reader gets
using the deliverable is asked by `usability.md`.

A deliverable is made accurate by checking it against its sources, in this order:

1. Gather the sources: the decisions, the files they name, and the product where the deliverable
   tells how it behaves.
2. For each statement the deliverable makes of its subject, find what it rests on: a decision, in
   the sources' own words; how the product behaves, in a run of it.
3. Say each statement that rests on neither as what it is, such as an assumption or a proposal, or
   take it out.
4. Hold the whole against the decisions, so each is carried out in full.
5. Hold each thing it says against the other documents and the product, so it is said in one place.

A deliverable keeps its kind's template; this checklist adds no part to it.

## Benefit

### B-1: How far to rely

Scope: each part

Can the reader take each statement as what it is, because one said as a checked fact rests on the
sources, and one that is not, such as an assumption, a proposal, a decision or a check that reached
only so far, says so where it stands?

Look for: a statement of how something behaves, such as what a command prints or what it changes,
said as fact where only its code or the decisions about it say so, not a run of it.

Why: the reader takes a statement said flatly as a fact; an assumption or an unchecked claim said
so is acted on as fact, and a check whose reach is not told is taken as having checked everything.

### B-2: What was decided carried out in full

Scope: whole

Does the deliverable carry out what its sources decided for it, neither narrowed nor widened?

Look at: each part against the decisions' words for the same thing; a part that holds less or more,
such as one case where a decision names a kind of case, fails.

Why: a deliverable narrower than what was decided still reads well, so it passes every item of
`usability.md`; the reader then gets less than the rest of the product counts on, and no one
reading the deliverable alone sees it.

### B-3: Said in one place across the product

Scope: whole

Is each thing the deliverable says said there alone, not also in another document or by the
product itself?

Why: two places that say one thing come to disagree as one of them changes, and the reader cannot
tell which holds.

### B-4: The picture as meant

Scope: whole

After one reading from the top, does the reader hold the same picture of the subject as its
sources give?

Why: the reader acts on the picture they took in; where it differs from what was decided, they act
otherwise without noticing.
