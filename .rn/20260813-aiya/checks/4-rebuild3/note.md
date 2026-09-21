# What changed — round-3 blank-page rebuild of the aiya design

Produced by `writ` `up` at commit `397ff9d`, run blank-page over `aiya/docs/design.md` at `d7b63f9`
(6,557 words). Output: `design.md` in this directory. `aiya/` was not touched.

---

## Step 1 — Understand the input

**Subject:** aiya's foundational design — a Claude Code plugin in which one person aims many
parallel AI agents at a single goal without watching them work.

**Must convey:** that the design's two mechanisms (the CCS, and the two-layer yardstick chain)
actually deliver the two properties chapter 1 requires (bounded context, drift detection), leg by
leg, with the qualifier that makes the delivery conditional.

**Proposed, not in force:** the run-state file `state.yaml` and everything attached to it — the file,
its four facts (backend in force, run branch, each gate's ruling, open/closed), the Conductor as its
sole author, its three write points (`on`, every gate ruling, G3), Turn(record) carrying it into
storage without ever editing it, its seat in the resume set and in the wave-settle and gate-ruling
record dispatches, a Planning-Gate approval becoming durable only at the next dispatch point, and
resume reading the gates' standing rather than deducing it. Carried forward as a proposal and marked
*(proposed)* at each of its eight appearances in the document; the one-line `backend` file that
ships in its place is stated beside it in §3.3, with file:line. Nothing else in the input was
treated as anything but in force.

## Step 2 — Reader and purpose

The reader was supplied by the run brief, not inferred, so no `Assumed reader:` line is present.

- **WHO** — a first-time reader who has never seen the product, evaluating its design.
- **WHAT they decide** — whether the two mechanisms discharge the two required properties.
- **HOW they read** — chapters 1–4 straight through; later chapters only if the decision needs them.

## Step 3 — Axis, the both-ways admission test, and the composite

### Axis

One reader reading through to reach a judgment → **article / explanation** (question and its answer
→ substance → limits). Under the supplied format (`aiya/references/design.md`, seven fixed chapters,
1–4 a story and 5 onward reference), the article skeleton was specialised onto chapters 1–4.

### Slot → reader (the subtractive direction)

Every heading was tested against the step-2 reader. What the format's slots carried for that reader:

| Format slot | Verdict |
|---|---|
| 1 Problem — goal, failure modes, required properties, out of scope | Admitted whole. The properties are the thing being judged. |
| 2 Core — roles, walls, vocabulary, one diagram | Admitted whole. The walls are a bounded-context leg; the vocabulary is unavoidable. |
| 3 Structure — inventory, ownership ledger, physical layout | Admitted, with the ledger re-purposed. The chain (§3.1) is the drift mechanism. The ledger earns its place for this reader only as evidence of independence (no writer measures its own work) — one sentence added under it saying so. |
| 4 Behavior — the loop | Admitted in part; see the removals below. |
| 5 Rules | Not this reader's — moved wholly into Part II, except the two facts the decision needs (below). |
| 6 Observability | Not this reader's. The document itself says the ratios measure the loop's efficiency and not the two properties. Serves an operator running a run. |
| 7 Trade-offs | Not this reader's as a list. The one item that bears on the decision — enforcement is not guaranteed — was pulled into §1.4 as the qualifier. The rest serves a design reviewer tracing decisions, and an operator pricing the shape. |

**Content kept out at this admission, and whose it is:**

- **The "Typical Steps" column of the phase table** (§4.4) — a planner's content; it tells you what to
  put on a Plan, which is not part of judging the discharge.
- **Dispatch rounds and the console progress board** (input §4.4) — an operator's content; it describes
  what the run looks like while it runs.
- **The platform's 20-concurrent-subagent cap and wave slicing** (`skills/conductor/SKILL.md:72`, not in
  the input document) — an operator's content, and explicitly throughput rather than correctness.
- **The full costs list** (chapter 7) — a design reviewer's and an operator's. Part I carries only the
  enforcement qualifier and the unbounded-transcript limit, both of which bear directly on the two
  properties.
- **Schemas, component vocabularies, worked examples** — the builder's; they stay where the format
  puts them, referenced by path.

### Reader → slot (the additive direction) — one proposed slot

Listing what the step-2 reader must have, and naming the slot that carries each, produced one need
with no slot in the supplied format:

> **The discharge itself** — the argument that mechanism M delivers property P, leg by leg, with
> what qualifies it.

The format gives chapter 1 "the properties the solution must guarantee (all later design is verified
against these)" and assigns their **discharge to no chapter at all**. In the input document it landed
at §4.6, at the end of the story part, after four chapters of mechanism.

**Proposed slot: chapter 1 gains a closing section carrying the discharge, before any of the design
that supports it.** Rendered here as **§1.4 "The answer — the CCS bounds context, the chain catches drift,
and nothing enforces either"**: two tables, three legs per property, each row giving what the leg
bounds or catches, how it holds (structural / traced / nothing), and where its machinery is — then
the intake-shape paragraph and the qualifier. Position: last section of chapter 1. The alternative considered and rejected was a new
numbered chapter between 1 and 2, which breaks the format's fixed seven harder for no gain — the
format's letter permits subsections, and it is the *content map* that has no slot, so the lighter
change is enough. **This is a proposal on `aiya/references/design.md`, not a change to it; the format
file was not touched.**

Reader evidence for it (supplied with the run brief): four independent readers, across two prior
rounds and two independently written documents, prescribed the same single change in near-identical
words — put the discharge at the front — and neither document could make it.

**Consequence: the input's §4.6 has no counterpart here.** With the discharge stated once at §1.4,
a §4.6 would be restatement (tell 2). Chapters 2–4 now supply the machinery each leg names and point
back at §1.4 rather than re-arguing it.

**Two further needs whose carrying slot deferred them**, resolved without proposing a second slot:

1. *What actually bounds the CCS.* The format says of chapter 5 "Format definitions live here", and
   the input's §5.4 carries the bound — outside the part this reader reads. A slot that defers does
   not carry. Resolved by putting the concrete bound (one file per wave, replaced not appended, real
   work by path, the 2,000-byte soft ceiling and what an overrun means) into §1.4's table, with
   §5.4 keeping the schema, the five operating rules, and the worked-example pointer for the
   reference reader. Not a deferral in either direction: each part carries what its own reader needs.
2. *What makes the verifier independent.* §1.4's second drift leg rests on the word "independent",
   whose content (never given the Report, never given the expected answer, writes its ruling before
   returning) sat only in §5.3. One paragraph now states it in §4.1; §5.3 keeps dispatch parameters,
   provenance, refusal behaviour, and sizing.

### The composite

The content genuinely needs two axes — an argument to read through, and an inventory to look things
up in. **The first answer is the split: these are two documents**, and that recommendation stands
for the owner. It was not taken here because the supplied format fixes seven chapters in one file
for a product's Design document, which makes splitting the owner's call rather than this run's.

So the parts are **declared**, at the head of the file and again at each part's head, each with its
own reader line and its own axis:

- **Part I (ch 1–4)** — the step-2 reader; article/explanation.
- **Part II (ch 5–7)** — someone building or operating aiya, arriving by search; reference.

**Separability walk (step 5), verdict: both parts pass — but only after the moves above.**

- *Part I alone.* Before the proposed slot, it did not pass: the CCS bound and the meaning of
  "independent" both sat in Part II, and the reader would have had to cross to decide. That is the
  failure the SKILL's walk is there to catch, and it fired. After §1.4 and the §4.1 paragraph, Part I
  reaches the decision without crossing: properties (§1.3), mechanisms and legs (§1.4), the bound
  (§1.4), independence (§4.1), the qualifier (§1.4), and the transcript limit (§4.5) are all inside it.
- *Part II alone.* Passes with one stated dependency: it uses chapter 2's vocabulary and says so at
  its head. A defined term referenced by name is not the argument being deferred.

## Step 4 — Fill

Every bullet written in my own words from the understanding of the input, not from its sentences.
Result measured at step 5, below.

## Step 5 — Story check and carryover measurement

**Story walk (Part I reader's order).** Two fixes made at bullet cost:

- *Gap.* §1.4 introduces Conductor / Turn / human before chapter 2 defines them. Fixed by a one-
  sentence sketch of the three parties at the head of §1.4, with chapter 2 then answering *why exactly
  two roles and what separates them* rather than re-introducing them.
- *Repeat risk.* The enforcement principle appeared in both §1.4 and chapter 2. Fixed by stating it
  once, in §1.4 where the reader needs it, and leaving chapter 2 only the two terms as vocabulary
  with a pointer.

**Carryover, measured mechanically** (maximal shared spans of ≥ 8 whitespace-alphanumeric tokens
against the input; script in scratch, same method both times).

| Reading | Spans ≥8 | Longest | % of produced tokens in a shared span |
|---|---|---|---|
| Step 5, filled outline, **first fill** | 58 | 24 | **17.01%** |
| Step 5, filled outline, **after re-fill** | 18 | 18 | **3.71%** |

**A re-fill was forced.** The first fill leaked heavily in the sections that would become chapters
5–7 and §4.4–§4.5 — whole clauses reproduced. Those bullets were re-written from meaning before any
rendering happened.

## Step 6 — Voice and form

**Voice (Part I):** plain and direct, a motive before each term, one claim per paragraph with its
status attached. **Closing (Part I):** §4.5's last paragraph — the limits, stating what the
boundedness claim does *not* cover, pointing at chapter 7. Not a recap of §1.4.

**Voice (Part II):** terse, uniqueness and coverage first, no warmth and no intros. **Closing:** none.

**Form per section:** §1.4, §3.2, §4.4, §6 — tables (several items on the same fields). §2, §3.1,
§4.1, §4.2, §4.4 — mermaid (structure and flow), with no prose repeating what a diagram carries.
§1.3, §2 vocabulary, §5.1, §5.4, §5.5, §7 — lists (genuinely parallel items). Everything else prose.
§3.4's "three kinds" is deliberately prose paragraphs rather than a list: the three are not parallel
in weight.

## Step 7 — Write

The input was closed at this step and not reopened for wording. It was reopened once, at step 10's
measurement, to run the side-by-side check — which is what caught the leak below.

## Steps 8–9 — Ceiling, and the seven tells

**One claim was struck at step 8, not softened.** The first render said two of the six legs are
structural, citing fresh contexts and the absent delegation tool. Held against `agents/*.md` and
against §5.1/§5.7, that is false: those two platform facts hold the **Turn contract**, and none of
the six legs is among them — §5.7 states outright that the no-reading wall cannot be made physical.
The document now says so. **The input's §4.6 makes the same attribution** ("some legs structural
(fresh contexts, the omitted spawn tool), the rest default and observable"); it is recorded below as
a subject finding for the owner and was not patched there.

**Tells found and fixed:**

| Tell | Where | Fix |
|---|---|---|
| 2 restatement | The Conductor's closed intake stated three times (§1.4 cell, §2, §5.7) | §2 now points at §5.7 instead of paraphrasing it |
| 2 restatement | The CCS soft ceiling's meaning given in both §1.4 and §5.4 | §5.4 keeps the diagnosis, §1.4 keeps the bound |
| 6 wavering voice | Part II carried warm asides: "at some point, looking into it yourself will feel faster"; "is telling you the Step is oversized" | Both recast flat, for the reference register |

Tells 1, 3, 4, 5, 7 were absent on a full scan (grep for the connective and hedging vocabularies
returned nothing; no list in the document holds non-parallel items).

## Step 10 — Self-check

| Item | Result |
|---|---|
| Reader is one person in one reading stance | **PASS** — per part, under the declared composite |
| One axis, no mixing | **PASS** — composite declared, each part carrying its reader line and axis at its head |
| Nothing carried over but names, identifiers, defined terms, deliberate quotation | **FAIL, then PASS** — see below |
| Every heading admitted, every reader need slotted | **PASS** — one proposed slot (§1.4), removals named above |
| Form fits content | **PASS** |
| No prose repeats what a diagram carries | **FAIL, then PASS** — round 1's reader reported §2's role paragraph and §4.4's phase diagram as restatements; the paragraph was cut back to the reason for two roles, and the phase diagram moved below the sentence it illustrates |
| Voice and closing fit the reader | **PASS** — per part |
| No tells remain | **PASS** |
| `Assumed reader:` iff inferred | **PASS** — absent, and the reader was supplied rather than inferred |
| Produced size recorded, growth argued | **PASS on record, and the argument does not fully hold** — see below |
| Every claim carries its status | **PASS** — see below |

### Carryover — the step-10 reading, and the re-render it forced

| Reading | Spans ≥8 | Longest | % in a shared span |
|---|---|---|---|
| Step 10, **first render** — prose only | 105 | 47 | **21.02%** |
| Step 10, **second render** — prose only | 53 | 27 | 8.45% |
| Step 10, after targeted de-carryover — prose only | 27 | 17 | 3.88% |
| **Delivered document — prose only** | **23** | **17** | **2.79%** |
| Delivered document — whole file, code fences included | 34 | 68 | 7.37% |

**A re-render was forced at step 10.** The step-5 outline measured 3.71%, and the first render came
back at 21.02% — the leak entered at rendering, not at filling: writing out chapters 5–7 from a terse
bullet, I reached for the input's sentence instead of expanding my own. Step 7's "close the input"
did not prevent that, because what re-entered came from memory rather than from the open file. The
second render, done strictly from the outline, plus a targeted pass over every remaining span, brought
it to 2.79%.

What remains at 2.79% is names, identifiers, file paths, ratio formulae, and the Bousetouane citation.
The 7.37% whole-file figure is the same prose plus the mermaid diagrams and the directory/YAML blocks,
which are reproduced deliberately: the graph *is* the design fact, and the run-state sample is the
proposal's own schema.

### Size

Input 6,557 words; delivered 8,156. **Ratio 1.24×.**

Where the growth went, and whether it was earned:

| Addition | Words | The reader need behind it | Earned? |
|---|---|---|---|
| §1.4, the proposed slot — two discharge tables with the "how it holds" column, the intake-shape paragraph, the qualifier | ~750 | The step-2 reader's entire decision. Four prior readers named its absence | **Yes.** Round 3's reader reached a leg-by-leg verdict from it and called its heading "the best sentence in the file" |
| §5.4's nine-component table | ~130 | Both round-1 readers dead-ended on a mechanism they were never shown | **Yes** for Part I; round-3's Part II reader says it served no lookup |
| Breach traces for §5.2, §5.3, §5.4 | ~150 | Chapter 5's own promise was false without them | **Yes** |
| The local adapter at its other four dispatch points | ~130 | Round 1's Part II reader failed lookup (c) on exactly this | **Yes** |
| The composite declaration and the two part heads | ~120 | The SKILL requires them | **Yes** |
| Round-2 and round-3 clarifications spread across §1.3, §2, §4.4, §5.1, §5.7 | ~350 | Named stumbles | **Partly** — see the finding below |
| Removed: §4.6 (the discharge, now at §1.4), the phase table's "Typical Steps" column, the dispatch-round progress board | −380 | Not this reader's | — |

**The honest reading of the ratio: the growth is defensible line by line and it bought no measured
reduction in reader effort.** Effort came back 4 in all three Part I rounds and 4 in all three Part II
rounds, on 6,919 → 7,695 → 8,156 words. That is the same shape as round 2's standing counter-case
(43% longer, effort 4 against 4), at 24% instead of 43%. What did move is not on the effort scale:
Part II's clean lookups went 3/5 → 4/5, and the Part I verdict sharpened from "the leg-3 claim is
false" to a precise, leg-by-leg QUALIFIED that the reader could defend. Whether that is worth 1,600
words is the owner's call, and the number is here so it can be made.

### Claim statuses

Checked exhaustively over the delivered document. Every claim carries one of the three:

- **Facts with sources.** Verified against the shipped plugin as drafted: the six Turn definitions'
  `tools:` lines carry no delegation tool, and exactly four carry Bash (`agents/*.md`); the 2,000-byte
  soft ceiling and the nine CCS components (`agents/turn-brief.md`); the local adapter's five dispatch
  points and its single `history/` write (`agents/turn-record-local.md`); the verifier's dispatch
  parameters, mandatory `evidence`, and refusal behaviour (`agents/turn-verify.md`); the version
  header written only by generate (`agents/turn-generate.md`); the four fixed Plan viewpoints, the
  three ratio definitions, the 50% heuristic, the three-attempt ceiling, and "aiya never merges"
  (`skills/conductor/SKILL.md`); six skills, five of them explicit-invocation only
  (`skills/*/SKILL.md` frontmatter); the shipped `backend` file at `skills/conductor/SKILL.md:26` and
  its use at `skills/up/SKILL.md:15`.
- **Decisions**, written as choices with their intent — every §7 entry, and the design's allocation
  between code and model in §2.
- **Hypotheses**, marked as such — that prose alone holds the six legs ("a wager, and it is
  untested"), and the 50% keep-rate threshold ("an opening heuristic, meant for tuning by use").
- **Proposal**, marked at every appearance — the run-state file.

**One claim carried from the input could not be verified against the shipped plugin and is stated on
the input's authority:** that the product's UX and Design documents live at `docs/ux.md` and
`docs/design.md` by default. `skills/conductor/SKILL.md` requires the two documents as prerequisites
and names no default location. Reported below, not patched.

## Step 11 — Three trial rounds, then delivery

Six trials, all fresh-context subagents given only a neutral-named copy and a reader definition.
Part I used the run brief's verbatim prompt every round, so the rounds are comparable to each other
and to prior rounds. Part II is the composite's per-part trial, with a lookup-shaped prompt held
constant across its three rounds. Every report is in this directory, verbatim and unedited.

| Round | Part | Decision | Effort | Stumbles | The one change the reader named |
|---|---|---|---|---|---|
| 1 | I | QUALIFIED | 4 | 25 | State the real shape of the Conductor's intake in §1.4's table |
| 1 | II | QUALIFIED, 3/5 lookups clean | 4 | 38 | Make every entry answer without leaving the page |
| 2 | I | QUALIFIED | 4 | 27 | Give §1.4's tables a third column: structural / traced / nothing |
| 2 | II | QUALIFIED, 3/5 lookups clean | 4 | 22 | A fixed fact card at the head of each §5 entry |
| 3 | I | QUALIFIED | 4 | 39 | Name the reader of every trace |
| 3 | II | QUALIFIED, 4/5 lookups clean | 4 | 28 | Stop bolding claims the following prose retracts |

Rounds 1 and 2 each named a change that was taken and that the next round confirmed as landed: round
1's intake-shape correction, and round 2's third column, which round 3's reader called the best
sentence in the file. **The cap fell at round 3, so nothing was edited after it and the run ends on a
trial rather than on an unverified edit.** Round 3's named changes ship unmade, below.

### Every stumble, sorted

Sorted across all six reports; the count is of distinct findings after merging duplicates across
rounds and parts.

| Sort | Count | Disposition |
|---|---|---|
| **Prose defect** | 41 | 30 fixed in rounds 1–2; **11 survive**, listed below |
| **Subject defect** | 9 | Named here, never patched |
| **Format defect** | 4 | Raised as proposed or unfilled slots |

**Prose defects surviving at delivery** — all named by round 3, after the cap:

1. **"Traced" has no named reader.** Five of the six legs rest on the word, and the document never
   says who inspects a trace or when. Round 3's Part I reader called this the largest hole and made it
   their one change. Partly a subject defect — see below — but the document could at least say that
   nothing in the loop reads a trace, and it does not.
2. **§4.3 does not carry §1.4's verdict on its own leg.** The table says "Nothing"; §4.3 states
   re-planning from zero in bold, as a rule in force, with no mention that nothing distinguishes it
   from an edit.
3. **The three-way vocabulary is not closed in practice.** §2 fixes structural / traced / nothing;
   §1.4's tables use "Traced only indirectly" and "Partly structural".
4. **A dangling cross-reference.** §3.3 says a Planning Gate may redirect the UX and Design documents
   "(§4.4)"; §4.4 does not carry that.
5. **Two things are called "the bet".** §1.4's wager (prose holds the legs) and §2's bet (model
   progress). §7's first bullet welds them; nothing earlier separates them.
6. **"Sub-linearly" in §5.4 has no named variable.**
7. **Four different sixes** — halts, skills, Turn definitions, legs — with nothing warning that the
   coincidence is a coincidence.
8. **§7 says "the four operating rules"; §5.4 prints six bullets.**
9. **§5.7 has no labelled breach trace**, and §5's "two of the seven leave none" therefore does not
   resolve by counting.
10. **Bold claims that the following prose retracts** — "A ceiling of 2,000 bytes" under "three things
    keep it small", and a "Measure | Definition" table above "Nothing is instrumented".
11. **Chapter 2's subheadings are unnumbered** while chapters 1, 3, 4 number theirs.

**Subject defects — for whoever owns the design, left standing, not patched:**

1. **The property does not answer the failure it was derived from.** §1.2 names context bloat as state
   piling up in proportion to the size of the job; §1.3's property covers the wave-to-wave
   carry-forward only. The transcript, which is precisely state proportional to job size, is excluded
   and reclaimed by a human typing `dn` → `/clear` → `up`. Both Part I readers, rounds 2 and 3,
   independently. The input has the same gap: its §1 and its §4.5.
2. **Drift's second shape has no detection.** Re-planning from zero is the leg that catches it, and
   §5.6's four breach traces do not distinguish a re-derived Plan from an edited one.
3. **The unmeasured artifact feeds the untraced leg.** Nothing measures the CCS (§3.2), and the CCS
   is what steering reads (§4.3), which is the leg with no trace. Round 3's reader: "their product is
   not stated."
4. **A trace nobody reads.** The Turn-contract wall's breach trace is a nested session's transcript
   that no bounded return reports. Two readers called this operationally identical to "nothing".
5. **Elicit answers are exempt from measurement** (§3.2), while drift detection claims *any* piece of
   work traces to the purpose. The exception and the claim are never reconciled.
6. **Nothing has been measured.** Chapter 7 is entirely future tense; there is no dogfooding result
   anywhere. The design's central wager is unresolved, which caps every verdict at QUALIFIED.
7. **The input's §4.6 attributes structural status to legs that are not structural** — "some legs
   structural (fresh contexts, the omitted spawn tool)". Those two facts hold the Turn contract;
   §5.7 says the no-reading wall cannot be made physical, and none of the six legs is platform-enforced.
8. **The default location of the product's UX and Design documents** (`docs/ux.md`, `docs/design.md`)
   appears in the input's §3.3 but nowhere in the shipped conductor skill, which names the two as
   prerequisites without a location.
9. **The keep-rate name reads against its formula** — Steps ÷ generates rewards fewer generates, so
   the name says "keep" and the ratio says "passed first time". Carried from the shipped conductor
   skill, unchanged.

**Format defects — raised, not resolved inside the slots:**

1. **The discharge has no slot** — the proposed §1.4, above. Raised for the owner.
2. **Chapter 5's "Format definitions live here" was being deferred.** The format has this slot; the
   input left it empty and pointed at the Turn definitions, and both round-1 readers dead-ended there.
   Filled here with the nine-component table. No new slot needed — the slot existed and was unfilled.
3. **Chapter 3's "physical layout, exactly once" is a slot the step-2 reader does not need.** The
   format requires it; every Part I reader across three rounds listed the directory tree and the
   `state.yaml` sample among content that did not serve the decision. It was kept, because leaving it
   unfilled would break the format's own contract, and it is named here instead.
4. **The composite does not earn its declaration, and the split is the answer.** Detailed below.

### The composite, re-judged after the trials

Step 5's separability walk passed both parts. **Three rounds of trials overturned that for Part II.**

- Round 1: "an entry that ends in '(§4.3)' for the actual rule is not a lookup answer; it is a pointer."
- Round 2: "line 5... is an announcement that entries are **not** complete on their own... the single
  thing that most breaks lookup use."
- Round 3: "the answer to 'is each entry complete on its own' is *no, by design*", and the reader's
  second change was to cut chapters 6 and 7 out of the file entirely.

Adding the vocabulary and *(proposed)* conventions at Part II's head, which round 1 asked for, did not
move the effort score and round 3 read the disclosure as the confirmation of the flaw rather than its
mitigation. Under the SKILL's rule — a part whose reader cannot reach its purpose without crossing
into the other is not a part — **Part II is not a part, and the split goes back to the owner as the
answer**: aiya's Design belongs in two files, an argument and a reference, with the vocabulary at the
head of the reference rather than cross-referenced into it. It was not split here because
`aiya/references/design.md` fixes seven chapters in one file, which makes the split the owner's
change and not this run's.

Part I passed its own walk and held: round 3's reader reached a leg-by-leg verdict, and the four
places they still crossed into Part II (§5.1's Bash admission, §5.3's independence argument, §5.4's
ceiling, §5.7's intake list) are named by that reader as "the ones that most changed my decision,
which means the argument half is under-carrying its own case." That is the residue of the same split.

### What the procedure asked for and could not be done

- **The SKILL's per-part trial and the run brief's fixed prompt do not compose.** The brief mandates
  one verbatim prompt on the whole document, for comparability with earlier rounds. That prompt is
  Part I's reader. Part II therefore got its own prompt, written for this run and held constant across
  its three rounds — so Part II's numbers are internally comparable but not comparable to any earlier
  round, and the Part I numbers alone carry the head-to-head.
- **Round 3's Part I reader could not partition its read.** Its tool returned the whole file in one
  call, so chapters 5–7 were in front of it from the start. It disclosed this and listed every
  consultation; the reading order it reports is still its own. Recorded rather than corrected, since
  correcting it would have meant a fourth trial past the cap.
