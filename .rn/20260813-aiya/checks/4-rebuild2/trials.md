# Head-to-head reader trials, round 2 — current design vs. the strengthened-writ rebuild

Both documents went to a fresh-context reader under the **same** prompt (verbatim below), the same
ratified reader definition, and neutral filenames (`doc-A.md` / `doc-B.md` in a scratchpad), so no
reader could tell which document it held or that a second one existed. No reader could read any other
file.

- **doc-A** = `aiya/docs/design.md` at `d7b63f9` (6,557 words) — the current document: writ-rebuilt in
  round 1, then refined and patched over four reader-trial rounds and the eight round-4 residual fixes.
- **doc-B-2** = `.rn/20260813-aiya/checks/4-rebuild2/design.md` (9,353 words) — a blank-page rebuild by
  the **strengthened** writ (`origin/worktree-writ`, 4787745), run in a subagent.

Raw reports, unedited: [`reader-A.md`](./reader-A.md), [`reader-A2.md`](./reader-A2.md),
[`reader-B.md`](./reader-B.md).

## Why this run measures the procedure and the last one did not

Round 1's rebuild disclosed, after the fact, that it had been drafted directly after a full read of the
source: **127 maximal shared 8-token spans**, reduced by two rewrite passes to a 7.3% identifier-only
residue. It therefore answered "is this document better", not "does blank-page writ produce a better
document".

The strengthened writ makes the carryover check a step-10 item with a stated bar. The rebuild ran it
mechanically, and it **caught a live failure**:

| | First render | After rebuild-from-meaning |
|---|---|---|
| Maximal shared spans ≥ 8 tokens | **177** | **6** |
| Longest span | **312 tokens** | **13 tokens** |
| Rebuild tokens inside a shared span | **70.87%** | **0.64%** |

The cause the run recorded: step 4's outline had been filled **with the input open**, transcribing its
sentences, so step 7's "close the input" protected nothing. All six surviving spans are the Bousetouane
citation, mermaid node ids, the fixed phase vocabulary, and the title. No clause, sentence or argument
survives.

**So doc-B-2 is genuinely independent of doc-A, and this comparison is about the procedure.** That is
the one thing round 1 could not deliver, and the mechanism writ added is what delivered it.

## Result at a glance

| | doc-A (current, 6,557w) | doc-B-2 (rebuild, 9,353w) |
|---|---|---|
| Verdict | QUALIFIED (both reports) | QUALIFIED, **leaning NO** |
| Effort (1 effortless – 5 struggle) | **4** | **4** |
| Stumbles reported | 23 / 24 | 22 |
| Headings alone carry the argument | 3 breaks / 2 breaks | 3 breaks |
| Had to leave chapters 1–4 to decide | yes (§5.1, §5.2, §5.4, §5.7, §6) | yes (§5.4, §5.6) |
| Reader's single most valuable change | "put the whole discharge in one place at the front" | "put the §4.6 verdict at the front" |

**Round 1's margin is gone.** There, doc-B scored effort 3 against doc-A's 4. Here, with the carryover
actually eliminated and three writ trial rounds run on the rebuild, both documents land at 4. The 43%
of extra words bought no measured reduction in reader effort.

## The finding both rounds keep producing, now from four independent readers

Across two rounds, four fresh readers, and two independently-written documents, the single most
valuable change is prescribed in near-identical words:

> doc-A's reader: "put the whole discharge in one place at the front — the two properties, all six
> carriers, *and the residual linear terms*."
>
> doc-B-2's reader: "put the §4.6 verdict at the front… Every mechanism after that would then read as
> evidence for a claim I already hold, instead of as promises I have to retroactively downgrade."

Neither document does this, and neither *can* while following the ratified format. `aiya/references/design.md`
gives chapter 1 "the properties the solution must guarantee" and assigns the discharge to no chapter at
all; both documents therefore put it at §4.6, at the end of the story chapters. doc-B-2's reader named
the consequence precisely: reading the headings, it predicted a document arguing the mechanisms *work*,
and the body argues they are *not enforced* — "an inversion, not a nuance."

**This is a format defect, upstream of both writ and either document.** It is the first finding of this
run that neither adoption fixes.

The second is the same shape. The format says of chapter 5: "Format definitions live here." Both
documents defer every schema out of chapter 5 to the Turn definitions, and both readers hit the same
dead end — doc-A's stumble 23 and doc-B-2's stumble 21 are both the CCS's nine components being
unavailable in the document that is supposed to be the reference, at the exact moment the reader needs
them to size the mechanism they were sent to judge.

## Where doc-B-2 is better, measurably

1. **Status marking.** doc-A marks the run-state proposal `(proposed)` **once**, across ten places that
   reference it, and doc-A's reader stumbled exactly there: "I do not know whether resume works as
   described or is a proposal. This directly affects §4.5, which I would otherwise credit." doc-B-2
   marks all seven of its mentions and writes them in the conditional. Writ's new step-1 status pass
   produced this, and it repaired a defect a reader independently reported in the other document.
2. **Errors of fact corrected.** The rebuild's trials caught and fixed several real errors in doc-A's
   prose that four earlier rounds had not: the reading wall stated as excluding documents the Conductor
   must read; "artifact" carrying three senses; the "structural" credit given to the omitted spawn tool
   that §5.2 then discounts. doc-A's reader hit the last of these as stumble 19.
3. **Honesty made explicit.** doc-B-2 states "none of the six legs is enforced" outright and walks all
   six. Its reader called that the right call — "the document says so, and it is right to." doc-A leaves
   the arithmetic to the reader, and both its readers had to do it by hand and lost confidence in the
   counts doing it.

## Where doc-B-2 is worse, measurably

1. **The width/size contradiction is confirmed unfixed.** The rebuild's own note disclosed this as one
   outstanding, unverified prose defect after the three-round cap. The head-to-head reader confirms it
   independently and calls it "the sharpest confusion in the document," sitting "directly on top of the
   property I was asked to judge" — §4.2 says a 2,000-byte ceiling "governs the file however wide the
   wave was — it fails nothing" and, two lines later, that growth is sub-linear "under a ceiling that
   stays put." A fixed ceiling that holds is a constant bound; one that fails nothing is no bound. Both
   claims stand at `design.md:197` and `:199`.
2. **Two floor-level defects that the author's own step 9/10 passed.** The self-check recorded PASS on
   "no prose repeats what a diagram carries" and found one restatement to fix. A fresh reader then
   found, in doc-B-2:
   - `design.md:227` — "Whatever the project lacks becomes Steps on the Plan." and, thirty words later
     in the same paragraph, "whatever a project lacks becomes Steps on the Plan, written in aiya's
     formats." Verified: near-verbatim duplication inside one paragraph. That is tell #2.
   - `design.md:91` — the chain diagram's first arrow, `PP["Plan"] -.->|"translated into Steps"| P`,
     runs Plan→Purpose while the other two run Purpose→Plan and the prose says the Plan converts a
     signed document into Steps. One arrow points the wrong way, and this is in the diagram the round-3
     fix had just edited.

   **The author-run floor check passes while a fresh reader finds floor-level tells.** That is a writ
   finding, not a document finding.
3. **The composite's promise is false to its reader.** doc-B-2's head note says the parts do not borrow
   each other's reader; its reader's stumble 1 is that part 1 defers to §5.1, §5.3, §5.4, §5.5, §5.6 and
   §5.7 continuously, "so I had to decide on every deferral whether the argument was still complete
   without it." The rebuild's own note counts roughly two dozen such pointers and flags them. The
   declared composite made the boundary explicit and did not make the parts separable.
4. **Length bought nothing.** +2,796 words, +43%, for the same effort score. Growth by chapter:
   ch1 +52%, ch2 +58%, ch3 +19%, ch4 +54%, ch5 +46%, ch6 +32%, ch7 +11%. It is not concentrated in
   contract detail; the story chapters grew fastest. Writ declined the length measure (D-10) on the
   evidence that round 1's growth *bought* easier reading. Round 2 is the counter-case that decline was
   waiting for: the same procedure, more growth, no gain.

## What survives either adoption

The design-level objections both rounds' readers raise are properties of the design, not of either
document's prose. Round 1 produced six raised by both readers; round 2's readers reproduce them and add
detail:

1. **The two-mechanisms framing is not what the design does** — §2 maps one mechanism per property,
   §4.6 needs three legs each. Every reader in both rounds hit it. doc-B-2 says so out loud and its
   reader still calls the §2 heading "contradicted by its own second sentence."
2. **Five of six legs are unenforced**, and the sixth only for the definitions shipping without a shell.
3. **Drift's second form — the stale plan faithfully completed — has no detector.** Both round-2 readers
   independently: a Conductor that lightly edits the standing plan and calls it a rebuild leaves no
   trace. doc-A's reader adds that §5.6 lists traces for four other breaches and none for this one.
4. **Bounded context is claimed for the working state; the transcript is outside it**, cut back by a
   person typing `dn` → `/clear` → `up`, and the concession sits in the suspend/resume section where a
   reader auditing the discharge will not find it. Both round-2 readers, independently.
5. **The Verdict intake is linear in wave width** — doc-A's second reader, new this round and not raised
   before: §4.2 claims "one bounded state per wave" while §5.7's intake list also admits bounded
   Verdicts, one per Step per viewpoint, which the Conductor must read to aggregate. "Doubling a wave's
   width does not double what the Conductor reads" is false on the document's own terms.
6. **The verifier's aim is chosen by the party whose drift it is meant to catch.** Raised in round 1 by
   one reader, raised again this round.
7. **Nothing measures whether drift detection works** — §6's three ratios all measure cost.
8. **"Sub-linear in what" is never answered**, in either document.
9. **The CCS's schema is a citation**, unavailable in the document that is supposed to be the reference.
10. **The run-state proposal cannot be audited against** until the owner rules on it.

## The prompt (verbatim, both readers)

```
You are reading one document, cold. Read only the file named below. Do not read any other file,
do not search the repository, and do not look anything up. What the document does not tell you,
you do not know.

FILE: {{FILE}}

Read as this person, and only this person:

- WHO you are: a first-time reader who has never seen this product, evaluating its design.
- WHAT you must decide afterward: whether the two mechanisms the document proposes actually
  discharge the two properties it says are required.
- HOW you read: chapters 1–4 straight through, in order. Later chapters serve a different reading
  stance (looking one thing up); read them only if you need them to reach your decision, and say
  when you did.

Do the headings-only pass FIRST: read only the headings, top to bottom, and write down what
argument you think the document is making. Then read the body.

Report, in this order:

1. **The decision.** YES / NO / QUALIFIED — do the two mechanisms discharge the two properties?
   State the reasoning that got you there, and if QUALIFIED, exactly what qualifies it.
2. **Headings-only pass.** Did the headings alone carry the argument? Where did the thread break?
3. **Every stumble**, numbered, in reading order. A stumble is any point where you had to re-read,
   jump out of order, hold a question open, or guess. Quote the line. Say what you expected and
   what you got. Do not filter for importance — report all of them.
4. **Content you did not need.** Which sections or blocks did not serve your decision? Where you
   can tell, say whom that content does serve.
5. **Effort score**, 1 (effortless) to 5 (struggle), plus the one change that would most reduce it.
6. **The path you actually took** — the order you read in, including every jump and re-read.

Be blunt. Do not be polite, do not praise, do not soften. A report that flatters the document is
useless. If something is confusing, say it is confusing and why.
```

Round 1's prompt was recorded only by description, not verbatim, so its exact wording could not be
reused. This one is fixed here so any later run is exactly reproducible. The two rounds' prompts are
therefore *comparable in intent but not identical in text*; round 1's is described in
[`../4-rebuild/trials.md`](../4-rebuild/trials.md).

## Anomaly: the doc-A trial returned two reports

The doc-A reader task delivered two complete, differently-worded reports. Only one was requested and
the agent was not resumed. Both are recorded verbatim ([`reader-A.md`](./reader-A.md),
[`reader-A2.md`](./reader-A2.md)) rather than one being discarded, because discarding either would be
selecting evidence after seeing it.

They corroborate rather than conflict: both QUALIFIED, both effort **4**, both naming the transcript
concession's misplacement, the unanswered "sub-linear in what", the absent CCS schema, the missing
trace for amend-vs-rebuild, and the two properties' absence from every heading before §4.6. Report 2
additionally finds the §4.2 / §5.7 Verdict-intake contradiction, which report 1 does not; report 1
additionally finds §6's ratios measuring only cost, which report 2 (having not read §6) does not.
Where the two differ, this evaluation counts the finding as raised by one reader, not two.

## Coverage of this record

Checked: both documents read end to end by fresh readers under an identical prompt; every quotation in
the "worse" section verified against `design.md` by line; the word counts and per-chapter growth
measured with `wc -w` and a chapter-splitting script; the carryover figures taken from the rebuild's own
mechanical measurement, not re-derived here.

Not checked: whether doc-B-2's 43% growth would fall to a fourth trial round — the skill's three-round
cap stopped the loop, and no fourth reader saw the corrected width text. The one outstanding prose
defect in doc-B-2 is therefore confirmed present but its repair is untested.
