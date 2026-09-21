# Round-3 evaluation — adopt the rebuild, ratify the slot it proposes

Compares `aiya/docs/design.md` at `d7b63f9` (6,557 words — the current document, unchanged since
2026-08-26) against `.rn/20260813-aiya/checks/4-rebuild3/design.md` (8,156 words — a blank-page
rebuild by the round-3-strengthened writ, `origin/worktree-writ` at `397ff9d`), and answers the
question round 2 left open.

## Recommendation

**Adopt the rebuild**, and ratify into `aiya/references/design.md` the one slot it proposes: chapter 1
closes with the discharge, before any of the design that supports it.

Two conditions attach, neither of which the run could discharge itself:

1. **A decision audit before the file is swapped.** Round 1's rebuild was cleared by an old-vs-new
   audit that confirmed zero ratified decisions lost. No such audit has been run on this rebuild. It
   is a precondition of replacing `aiya/docs/design.md`, not of the adoption decision.
2. **The split is a separate ruling.** The run's own trials say the file should become two documents
   (below). Adoption does not settle that, and the rebuild works as a single file in the meantime.

## Why the answer changed from round 2's "adopt neither"

Round 2 rejected both documents for one stated reason: the single change four independent readers
prescribed across two rounds and two independently-written documents — *put the discharge of the two
properties at the front* — was one **neither document was permitted to make**, because
`aiya/references/design.md` gives chapter 1 "the properties the solution must guarantee" and assigns
their discharge to no chapter at all.

The user's 2026-09-01 ruling was to fix that through writ rather than by hand. Writ took the feedback
(`397ff9d`) and made step 3's admission test run in both directions: a reader need that no slot
carries is now raised as a **proposed slot** with its position and reader evidence, instead of being
absorbed as prose under the nearest heading.

**The mechanism fired on its first field run, and it fired on exactly the defect it was built for.**
The rebuild raises one proposed slot — the discharge — realizes it as §1.4, and leaves the format file
untouched. Round 2's blocking reason is therefore discharged for the rebuild and still stands for the
current document.

§1.4 is two tables, three legs per property, each row giving what the leg bounds or catches, **how it
holds** (structural / traced / nothing), and where its machinery lives — then the qualifier: *"Read the
third column before the first two. Not one of the six legs is enforced."* Round 3's reader called that
heading the best sentence in the file.

## What the measurements say

| | current (`d7b63f9`) | rebuild (round 3) |
|---|---|---|
| Words | 6,557 | 8,156 (**1.24×**) |
| Reader verdict | QUALIFIED (2 readers, round 2) | QUALIFIED (3 readers) |
| Effort, 1–5 | **4** | **4** (all three rounds) |
| Verdict quality | "the leg-3 claim is false" | a defensible leg-by-leg QUALIFIED |
| Carries the prescribed discharge-first structure | no | yes |

**Effort is tied for the second round running, and the prescribed change did not move it.** §1.4
existed from the rebuild's first trial; effort came back 4 at 6,919, 7,695 and 8,156 words. Adoption
cannot be justified by measured reader effort, and this evaluation does not try to. What the readers
stopped complaining about is the discharge — each round named a *different* next change (the intake
shape, the third column, naming the reader of every trace), which is what a solved complaint looks
like on a scale that appears saturated for a document of this difficulty.

**The carryover is clean, independently.** The run reports 23 maximal shared 8-token spans, longest 17,
2.79% of its tokens inside a shared span. Recomputed here by the coordinator with an independent
tokenizer (code spans stripped): **13 spans, longest 14, 1.77%**. The longest survivors are the
Bousetouane citation URL, a tool-name enumeration, and fixed vocabulary. No clause, sentence or
argument survives — the comparison is between two independently written documents, as round 2's was
and round 1's was not.

**Two re-fills were forced**, one at step 5 (17.01% → 3.71%) and one at step 10 (21.02% → 2.79%). The
step-10 leak matters for writ: the outline was clean and the *render* pulled the input's phrasing back
in from memory, so closing the input at step 7 protected nothing. Sent to writ as round-4 feedback.

## What adoption costs

- **+1,599 words.** The note argues the growth line by line and the largest item — §1.4 at ~750 words —
  is the reader's entire decision. The honest counter-case stands: it bought no measured effort
  reduction, the same shape as round 2 at 43%.
- **11 known prose defects ship**, all raised by round 3 after the three-round cap and none patched
  afterwards (the run ends on a trial, never on an edit — writ's new rule). The largest: "traced" is
  the word five of six legs rest on and the document never says who reads a trace.
- **A format ruling is required** before the rebuild is legitimate rather than a deviation.

## The two format decisions this round produced

Both are the owner's, and both outlive whichever document is adopted.

1. **Chapter 1 gains a closing discharge section.** Evidence: four readers across rounds 1–2 on two
   documents prescribed it; round 3's readers confirmed it landed. The lighter of the two shapes
   considered — a subsection rather than a new numbered chapter — so the format's fixed seven survives.
2. **The Design document should be two files, an argument and a reference.** The rebuild declared the
   composite writ sanctions and passed the step-5 separability walk; **three trial rounds then
   overturned it for Part II** — every round found entries incomplete without chapter 2, and the
   round-1 mitigation (vocabulary at Part II's head) moved nothing. Under writ's own rule a part whose
   reader cannot reach its purpose without crossing into the other is not a part. Not done in the run
   because `aiya/references/design.md` fixes seven chapters in one file.

## What neither adoption fixes: nine defects in the design itself

Named by the readers, never patched — they are holes in aiya, not in the prose, and each needs its own
disposition:

1. §1.3's bounded-context property does not answer §1.2's failure — the transcript is exactly state
   proportional to job size, and it is excluded from the claim and reclaimed by a human typing
   `dn` → `/clear` → `up`. Both readers, independently. **The current document has the same gap.**
2. Drift's second shape (the stale plan) has no detection — nothing distinguishes a re-derived Plan
   from an edited one.
3. The unmeasured artifact feeds the untraced leg: nothing measures the CCS, and the CCS is what
   steering reads.
4. The Turn-contract wall's breach trace is a nested session's transcript that no bounded return
   reports — operationally identical to "nothing", per two readers.
5. Elicit answers are exempt from measurement while drift detection claims *any* work traces to the
   purpose; never reconciled.
6. Nothing has been measured at all — chapter 7 is entirely future tense, which caps every reader
   verdict at QUALIFIED.
7. The current document's §4.6 credits "structural" status to legs that §5.1/§5.7 show are not.
8. The default location of the product's UX and Design documents is in the design and **not** in the
   shipped conductor skill.
9. The keep-rate name reads against its formula (Steps ÷ generates says "passed first time", not
   "keep") — carried unchanged from the shipped skill.

Items 7–9 are build-side and land in the ripple whichever document is adopted.

## Scope of this evaluation

- **Verified by the coordinator**: §1.4 read in full against the note's description of it; carryover
  recomputed independently; `aiya/docs/design.md` and `aiya/references/design.md` confirmed untouched
  since `d7b63f9`; the rebuild's chapter structure read end to end at heading level; the run's four
  commits confirmed pushed and scoped to `checks/4-rebuild3/`.
- **Not verified**: the six reader reports were not re-read in full — their numbers are taken from the
  note, which quotes them; the rebuilt document was not read line by line; **no old-vs-new decision
  audit was run**, which is condition 1 above.
