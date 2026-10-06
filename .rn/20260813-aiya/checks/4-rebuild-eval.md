# Current design vs. writ rebuild — adoption evaluation

Written by the coordinator from `checks/4-rebuild/trials.md`, `checks/4-rebuild/note.md`, and direct
measurement of both documents. It answers one question: **does the blank-page rebuild replace
`aiya/docs/design.md`, or does the current document stay and take what the rebuild proved?**

- **doc-A** — `aiya/docs/design.md` at `d7b63f9`, 6,557 words. The current document: writ-rebuilt at
  `486a1af`, refined at `edcf1b4`, re-run at `b2712f2`, eight round-4 residuals fixed at `d7b63f9`.
- **doc-B** — `.rn/20260813-aiya/checks/4-rebuild/design.md`, 8,334 words. Built blank-page in a
  subagent by the writ `up` procedure, steps 1–10, from doc-A's intent plus the shipped files.

## The bar this is judged against

The 2026-08-19 density ruling, not coverage: **the document's job is understanding.** Few load-bearing
principles stated once, final decisions reading simply from them; contract detail that serves lookup
lives in the shipped artifacts, not restated in prose. "Decisions kept" was explicitly withdrawn as the
bar in that same ruling.

A second purpose sits underneath: this rebuild is the honest re-run of the step-7 deviation disclosed
in `checks/4-writ-rerun-note.md`. It was meant to measure **the writ procedure**, blank-page, not just
to produce another draft.

## What the exercise measured — and the one thing it could not

The head-to-head is sound as a readability comparison. Both documents went to a fresh-context reader
under an identical prompt, the ratified reader definition, and neutral filenames; neither reader knew
which document it held or that a second existed.

It is **not** a clean measurement of the procedure. doc-B's own step-9 disclosure records that it was
written directly after a full read of doc-A, producing 127 shared 8-token spans — whole clauses
reproduced verbatim — reduced over two rewrite passes to a 7.3% residue in which every span of 10+
tokens is an identifier. That is disclosed honestly and the residue is now benign, but the draft was
influenced at the sentence level by the document it was supposed to be independent of. **The re-run
answers "is this document better", not "does blank-page writ produce a better document."** The
step-7 deviation is therefore narrowed, not closed.

## The rebuild reads easier — and not for the reason `trials.md` records

The reader result stands: both QUALIFIED, doc-B at effort 3 against doc-A's 4, doc-B's headings-only
pass "above average — I could reconstruct the machine" against doc-A's three breaks. Reader A's named
drivers for doc-A's extra point of effort are all verifiable in the file:

- **Front-loaded term density.** §2's `Vocabulary, fixed here` block defines ten items in one run, and
  `Step`, `Plan`, the attempt cap and the return contract are all used in the walls paragraphs above
  it (`design.md:41`). doc-B glosses each term where it first appears instead.
- **The changing count** — two properties → two mechanisms → "two supports each" → §4.6's three legs.
- **Compression into ambiguity** on four lines past the point a first reader can recover the parse.
- **Load-bearing content deferred off-document.**

One claim in `trials.md` does not survive measurement. It records the rebuild's +1,777 words as
including "contract detail the density ruling puts in the shipped artifacts", which would make the
length a defect of kind. Per-chapter counts show the growth is **uniform prose expansion**, not a
contract dump:

| | §1 | §2 | §3 | §4 | §5 | §6 | §7 | total |
|---|---|---|---|---|---|---|---|---|
| doc-A | 195 | 795 | 1,056 | 2,003 | 1,633 | 240 | 608 | 6,557 |
| doc-B | 311 | 985 | 1,240 | 2,631 | 2,053 | 339 | 736 | 8,334 |
| growth | +59% | +24% | +17% | +31% | +26% | +41% | +21% | **+27%** |

§5 — the contract chapter — takes 23.6% of the growth while holding 24.9% of doc-A: exactly its share.
doc-B is not doc-A plus contracts; it is doc-A said at 1.27× the words throughout. That reframes the
trade honestly: **doc-A buys density and pays in ambiguity; doc-B spends words and is read more
easily.** Against a bar that says *understanding*, doc-B's spend is the defensible side of that trade —
which is a finding about doc-A's compression, not a reason to swap documents.

## What no adoption fixes: the findings belong to the design

Six objections were raised **independently against both documents** by readers who could not see the
other. They are properties of the design, not of either prose:

1. The stated property (bounded width) is narrower than the pain that motivates it (cumulative growth);
   §4.5 concedes linear transcript growth and hands the remedy to the human's `dn` → `/clear` → `up`.
   Neither document admits the scoping at §1.
2. The CCS's bound is a soft cap, and its schema is a citation the reader cannot open. "Sub-linear in
   *what*" is unanswered.
3. The no-reading wall is not structural, and nobody reads the trace — there is no auditor role and §6
   counts no wall breaches.
4. Nothing measures whether drift detection **works**. §6 counts cost only: no drift-caught rate, no
   false-negative signal.
5. The 1:1 mechanism map does not survive §4.6. Reader B prescribes the fix: strike §2's
   one-mechanism-each sentence and let §4.6's three-legs account stand.
6. The two properties appear in no heading before §4.6 announces their discharge.

Four more were raised once each and are equally design-level: drift's second form — a stale plan
completed faithfully — has no named trace (a Conductor re-emitting yesterday's Plan is
indistinguishable from one that rebuilt it), and it compounds with the CCS defending against
over-claim but not omission; whether Turn(brief) reads the previous CCS is never stated, and either
answer costs something; the verifier's aim is set by the party that would drift; and Turn(generate)'s
"what it tried and abandoned" reaches only Turn(brief), after the wave settles — so attempts 2 and 3
cannot see what attempt 1 abandoned.

**Ten findings, and the adoption decision moves none of them.** That is the exercise's largest output.

## What the rebuild drops is context, not fact

doc-B omits the run-state file (`state.yaml`) entirely, on the correct fact that no shipped file
carries it — the plugin ships a one-line `backend` file (`conductor/SKILL.md:39`, `up/SKILL.md:15`),
confirmed by grep. But the run-state revision is **deliberately ahead of the build**: it is the object
of the pending PR #19 gate, with the ripple into the plugin explicitly deferred until after approval.
doc-B, built from the shipped files, could not know that. The drop is a rebuild error of context.

The finding underneath it does stand, and is doc-A's to fix: `state.yaml` appears at eight places in
doc-A and only the first (`design.md:122`) is marked `(proposed)`; the other seven assert it as
shipped. An evaluating reader cannot tell which parts of the document are live and which are pending.

Two of the eight round-4 fixes applied at `d7b63f9` were also read as defects and need re-ruling before
the gate: **R3 backfired** — the added "two supports" clause made the count more visible without making
it true, and sent reader A out of order to §4.6 — and **R1 is half-right** — dropping the blanket
"structural" was correct, but the examples it kept (fresh contexts, the omitted spawn tool) are
Turn-contract properties, not legs of either discharge, and §5.2 discounts the spawn tool itself since
every working Turn carries Bash. **R8 is contested**: naming the Conductor as the party that notices a
missing viewpoint is faithful to `conductor/SKILL.md:79`, so the tension is in the design.

## Recommendation: keep doc-A as the base, port what doc-B proved

Adopting doc-B wholesale costs three things and buys one. It buys the easier read. It costs the
sentence-by-sentence owner ratification doc-A carries; it costs the run-state revision that is the
pending gate's own object; and it re-opens FB3, the format-cost cluster both readers rejected
identically, against a document nobody has ratified. The single win is portable; the three costs are
not recoverable.

Port into doc-A:

- **P1** — strike §2's `Each mechanism carries two supports alongside it` (the R3 clause) and let
  §4.6's three-legs account be the only statement of the discharge. Reader B's prescription, reader A's
  stumble 5, and the withdrawal of a fix that made things worse.
- **P2** — re-do R1's examples so the structural claim names things that are actually legs of a
  discharge, or drop the examples.
- **P3** — gloss terms where they first appear rather than in §2's ten-item block, and move
  `Step`/`Plan` ahead of their first use at `design.md:41`.
- **P4** — mark all eight `state.yaml` mentions as proposed-pending-PR-#19, so the document's live and
  pending layers are distinguishable.

**One win is not portable from the evidence in hand.** Reader A's "compression into ambiguity" names
four specific lines, and the raw trial outputs were not saved — `trials.md` summarizes them without
quoting them. Fixing that driver needs a fresh targeted pass, not a port.

Not recommended as ports: doc-B's chapter ordering (§5.1 Conductor first) and its uniformly longer
prose — the first is a preference neither reader raised, the second is the +27% itself.

## Coverage of this evaluation

Read in full: `trials.md`, `note.md`, doc-A §2, doc-A's eight `state.yaml` sites, the shipped
`backend` sites in `conductor/SKILL.md` and `up/SKILL.md`. Measured directly: per-chapter word counts
for both documents, the `(proposed)` marker count, the shipped-file grep for `state.yaml`. **Not**
independently re-read end to end by the coordinator: doc-B's 8,334 words — its content is taken from
its note, its self-check, and reader B's trial, all three of which are the rebuild's own account.
