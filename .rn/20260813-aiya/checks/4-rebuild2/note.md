# What changed — aiya design, blank-page rebuild (writ `up`, round 2)

Input: `aiya/docs/design.md` (6,557 words). Output: `design.md` in this directory (9,353 words, 43% longer than the input — three rounds of reader trials added what four fresh readers said they could not decide without).
Not an edit of the input. The input was read once for intent and status, an outline was built and
filled, and the input was closed before a word of the document was rendered.

## What was built, and why

**Structure.** The seven-chapter Design format (`aiya/references/design.md`) supplies the chapter
skeleton; the gists after each em dash are specialized to this content. The file is a **declared
composite**: chapters 1–4 are one document and chapters 5–7 another, each carrying its own reader and
axis at its head. The split is what the format itself describes — "chapters 1–4 are a story read top
to bottom; 5 onward are reference to be consulted" — and the owner keeps one file, so writ's
sanctioned composite applies rather than two files.

**Story (part 1).** Ordered so a first-time reader can decide the one thing they are here to decide.
Two failure modes name two owed properties (ch1) → the roles and walls that answer them, plus the one
wager the whole design rests on (ch2) → what exists and who owns it (ch3) → how it moves, from a
single Step outward to a suspended run (ch4), closing at §4.6 with the discharge stated leg by leg
and its limit named. The CCS's operating detail lives in part 2, which this reader never opens, so
§4.2 carries the minimum a reader needs to judge boundedness for themselves — new file per wave, not
extended; written after the rulings by a party with no stake; artifacts by location.

**Story (part 2).** No story. Entries in the product's own order (Turn contract, then the four roles,
then the Plan, then the Conductor), each with the same two fields: the promise, and the evidence a
violation leaves. Chapters 6 and 7 are lookup tables of measures, rejected shapes, and accepted costs.

**Voice.** Part 1 is warm and plain with a motive before each term, and closes on what the design
bought and what it does not settle. Part 2 drops warmth and intros, states coverage first, and has no
closing. The two voices are why the parts are declared rather than merged.

**Form.** Four mermaid diagrams, all structure or branching: the two roles (ch2), the two-layer chain
(§3.1), the Step pipeline (§4.1), the wave (§4.2). The input's gate-sequence diagram was **dropped** —
six stops in a fixed order is a linear sequence a sentence carries faster, and the phase table beside
it already holds the content. Three tables (ownership ledger, phases, ratios) for items compared on
the same fields. One code block, the directory tree, appearing in §3.3 and nowhere else, as the format
requires of physical layout.

## Step 1 status pass

`Subject:` aiya's foundational design — a Claude Code plugin where one person names a goal, a
directing agent runs many fresh-context subagents to reach it, and the person appears only at six
approval stops.

`Must convey:` naive delegation fails in two ways (the director's state swells; work stops answering
to the goal), those two failures name two properties the design owes, and each property is paid by one
lead mechanism plus two supports — laid out so a first-time reader can judge the discharge themselves.

`Proposed, not in force:` **the run-state file `state.yaml`** — the file itself; its four facts
(backend in force, run branch, each gate's ruling, open/closed); the Conductor as its sole author; its
three write points (`on`, every gate ruling, G3); Turn(record) carrying it into storage without ever
editing it; its seat in the resume set and in the wave-close and gate-ruling record dispatches; a
Planning-Gate approval becoming durable only at the next dispatch point; and resume reading the gates'
standing instead of deducing it.

- Status source: given as input context — the design deliberately runs ahead of the build and is
  awaiting the owner's verdict, with the ripple into the plugin deferred until that verdict.
- Confirmed against the shipped plugin: what ships is a one-line `backend` file
  (`aiya/skills/conductor/SKILL.md:26`, and `aiya/skills/up/SKILL.md:15` locates a run by it), and the
  shipped resume re-presents a pending gate when the disk cannot tell approved from awaiting
  (`aiya/skills/conductor/SKILL.md` §9). Nothing under `aiya/` mentions `state.yaml`.
- **Carried forward, not dropped.** The input marked only the first of its `state.yaml` mentions as
  proposed and let the remaining seven read as shipped. The rebuild marks **every one of its seven
  mentions** (§3.2 table row, §3.3, §4.4, §4.5 ×2, §5.5, §5.7) and uses the conditional mood wherever
  it describes behaviour that does not yet exist.

`Hypothesis:` three, each marked in the document as such —
- that prose alone can hold the cycle, the attempt ceiling and the gates, to be settled by using aiya
  on itself (ch7, first rejected shape);
- that below a 50% keep rate the loop costs more than it saves — written as a starting rule of thumb
  "to be sharpened by use rather than treated as measured" (ch6);
- the factor of ten itself, declared out of scope for measurement (ch1).

Everything else in the input is in force and was carried as fact, with sources verified against the
shipped plugin where the claim is checkable there (the six agent definitions under `aiya/agents/` and
their `tools:` lines; the six skills under `aiya/skills/` and their invocation flags; the run directory
layout and the three backends in the conductor skill; the nine-component CCS schema and its 2,000-byte
soft cap in `aiya/agents/turn-brief.md`; the five dispatch points in the three record adapters).

## Step 10 self-check

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Reader is one person in one reading stance | PASS | Declared composite: one reader line per part, at its head (l.12–14 and the part-2 header). Neither part addresses the other's reader. |
| 2 | One axis, no mixing | PASS | Part 1 declares `article / explanation`, part 2 declares `reference`, both at the head. No reference-style entry list inside ch1–4; no argument thread inside ch5–7 beyond each entry's own rationale. |
| 3 | Nothing carried over but names, identifiers, defined terms, deliberate quotation | PASS (after FAIL) | Measured mechanically — see the next section. First render FAILED at 177 spans / 70.87%; the document was rebuilt and, re-measured after every trial round, ends at 6 spans / 0.64%, every one of them a name, an identifier, mermaid syntax, or the cited paper. |
| 4 | Every heading and point admitted by its part's reader | PASS | Content excluded at the admission points is listed under "Content kept out" below. The one heading the input carried that no reader here needed — the gate-sequence diagram's narration — was cut with its diagram. |
| 5 | Form fits content | PASS | Four mermaid diagrams, all structure or branching. Three tables, each comparing several items on identical fields. Lists are parallel throughout: the vocabulary list (term → gloss), the five contract rules, the five record dispatch points, the four Plan viewpoints, the rejected shapes, the accepted costs. Reasoning runs as prose. |
| 6 | No prose repeats what a diagram carries | PASS | The prose after each diagram adds what the diagram cannot hold: after ch2's, the two walls and why they hold; after §3.1's, what heavy versus dotted arrows mean; after §4.1's, the AND, the merged gap, and the two paths off the attempt counter; after §4.2's, why one brief per wave and why record commits alone. No sentence restates a node label. |
| 7 | Voice and closing fit the reader | PASS | Part 1 warm and plain, closing at §4.6 on the discharge and its limit, then pointing onward to chapters 6 and 7. Part 2 has no introduction and no closing; entries open on the promise. |
| 8 | None of the seven tells remain | PASS | Step 9 pass recorded below, re-run after the last round of fixes. |
| 9 | `Assumed reader:` line present iff inferred | PASS | The reader was ratified by the owner, not inferred, so no line is present. |
| 10 | Every claim carries its status | PASS | Facts asserted plainly with their source verifiable in the plugin; the run-state design marked proposed at all seven mentions and written in the conditional; three hypotheses marked as hypotheses (ch6, ch7, ch1); decisions written as choices with their intent (the wager in ch2, every entry in ch7). |

### Step 9 — the seven tells

Nothing was caught that required a fix at this pass, which is what building fresh is supposed to buy.
What was checked, and how:

1. **Padding** — every chapter and section opens on its point. Scanned each opener; no announcement of
   intent survives.
2. **Restatement** — one instance found and fixed. The file's opening bullets described each part's
   reader, and each part's header then declared the same reader. The bullets were replaced with a
   single line that says only that the file is a composite; the reader lines carry the readers.
3. **Generalities** — claims carry names and numbers (six skills, six definitions, three backends,
   three attempts, nine components, five dispatch points, three ratios, 50%).
4. **Flavorless connectives** — grep for `moreover|furthermore|in addition|additionally`: zero hits.
5. **Reflexive bulleting** — every list checked for parallelism; see self-check item 5.
6. **Wavering voice** — the two voices are declared and confined, one per part.
7. **Hedging** — grep for `it is thought|generally speaking|arguably|somewhat|it is worth noting`:
   zero hits. Uncertainty appears only where it is labelled a hypothesis.

## Carryover measurement (step 10)

Measured, not judged by impression. Script: `ngram.py` in the run scratchpad — tokenizes both files
(word characters, plus `.`/`/`/`@`/`-` inside tokens, lowercased), indexes every 8-token window of
`aiya/docs/design.md`, and for each position in the rebuild extends the longest match found anywhere in
the source, then keeps only maximal (non-contained) spans.

The skill's own line is the bar:

> Nothing carried over from the input's wording but names, identifiers, defined terms, and material
> quoted on purpose — read the two side by side and confirm it. Having been told to rebuild is not
> evidence that you did.

**First render — FAIL.**

| | |
|---|---|
| Maximal shared spans ≥ 8 tokens | **177** |
| Longest span | **312 tokens** |
| Rebuild tokens inside a shared span | **4,783 of 6,749 — 70.87%** |

The cause was mechanical and worth recording: the filled outline had been written with the input open,
and for chapters 5–7 it transcribed the source's sentences instead of restating them. Closing the input
at step 7 then protected nothing, because the source's wording had already crossed into the outline.
Step 4's "write every bullet in your own words" is the load-bearing instruction, and it was the one
broken. The document was rebuilt from meaning — every sentence re-expressed, diagram node labels and
table cells included.

**After rebuild — PASS.**

| | |
|---|---|
| Maximal shared spans ≥ 8 tokens | **6** |
| Longest span | **13 tokens** |
| Rebuild tokens inside a shared span | **59 of 9,166 — 0.64%** |

The measurement was re-run after each round of trial fixes; the span count never rose above 8 and the
survivor set never changed.

All six survivors, classified:

| Span (length) | What it is | Legitimate? |
|---|---|---|
| `from bousetouane ai agents need memory control over more context https arxiv.org/abs/2601.11653 2026` (13) | A cited paper's author, title, URL and year | Deliberate quotation — a citation cannot be paraphrased |
| `a turn performs mermaid flowchart lr wo work order g turn generate br` (13) | Three words of prose ("a Turn performs") abutting mermaid syntax and node identifiers (`flowchart LR`, `WO["work order"]`, `Turn(generate)`) | Identifiers and diagram syntax |
| `three purpose why approach how delivery execution plan step` (9) | The phase names with their one-word glosses, and the terms Plan and Step | Defined terms fixed by the vocabulary section |
| `aiya design aiya is a claude code plugin` (8) | The document title and what the product is | Name plus product identity |
| `return t t reads and writes a c` (8) | Mermaid node ids and the edge label `reads and writes` | Diagram syntax |
| `turn record br commit push r s conductor` (8) | Mermaid node ids and the labels `Turn(record)`, `commit + push` | Identifiers and diagram syntax |

No span is a surviving clause, sentence, or argument. The prose is independent of the source, which is
the property that lets the two documents be compared at all.

## Step 11 trials

Two fresh subagents per round, one per part, each given only its part and its part's reader line — no
outline, no input document, no history, and no sight of the other reader's document. The parts were
extracted to standalone files so neither reader could see the other's.

### Round 1 — part 1 (first-time reader, evaluating the design)

**Verdict: reached the purpose only halfway.** Bounded context: decidable, and the reader followed the
argument to the point of granting it for the working state, with the transcript caveat left
unreconciled between §1's property and §4.6's discharge. Drift detection: **undecidable**, for three
reasons the reader stated precisely — the chain leg's central object ("a Step whose parent link fails
to account for it") was a metaphor with no artifact, writer, or location; the version-pinning leg was
cited as catching unrequested work, which the reader could not see it doing; and the replanning leg is
an unenforced default argued in §4.6 with a `since` clause that assumes the rebuild really happened.

Headings: the thread held, with one break — the two properties never appeared in a heading until the
last one, so "Discharging the two properties" referred to two things the heading list had never named.

**Prose defects fixed (22).** The reader's stumbles, triaged and repaired:

- "Two mechanisms produce that" in §1 used *mechanism* for the failure modes twelve lines before §2
  used it for the design's devices → recast to "Two things go wrong."
- §1 promised bounded "live state", §4.5 delivered "working state" and excluded the transcript → §1
  now names working state, defines it, and points at §4.5 for the transcript.
- §4.6 asserted "none of which lengthens as the work does" without naming what falls outside → it now
  states the boundary and says who does the flushing.
- "CCS" was used in §2's vocabulary with no expansion and no definition until §4.2 → expanded at
  first use.
- §2's enforcement paragraph — the fact that nothing is enforced — sat *after* the walls had already
  been described as prohibitions → the enforcement section now precedes the walls, and each wall
  states its own class (wall 1 a default with its trace; wall 2 structural, with the Bash gap named).
- "Guarantees do not enter into it" was unparseable three ways → replaced with what it meant.
- The lead-mechanism/legs sentence, load-bearing for the reader's whole task, was buried at the end of
  a philosophy section → promoted to its own section, "What carries the two properties".
- "a **Planning Gate**", singular, read as one gate for the whole run → now three, one per phase.
- `on` / `dn` / `up` were used in §3.3 and §4.2 and only implied in §4.5 → glossed where the vocabulary
  is fixed.
- §3.1's "parent link" → replaced with the inspectable object it actually is: the Plan's derivation
  from the document above it, which the fourth fixed Plan viewpoint tests and whose Verdict is on disk.
- §3.3's tree comment said the CCS chain is "one per run, overwritten never extended" while §4.2 said
  a new file per wave → the comment now says one file per wave, chain per run.
- §3.2's "complete list, given once" contained a row for an unbuilt proposal → the lead-in now says so.
- §3.2's human-owner column used a bare em dash for two rows and a dash-plus-prose for three → all
  five now read the same way.
- §3.3 addressed the reader directly about what they did not need ("not this reader's") → removed.
- §3.4's heading listed four things where the body counted three → renamed to the counts it holds.
- §4.1's "no more than three gaps" could not be reconciled with an uncapped viewpoint count → now the
  history of the three attempts, one merged gap apiece.
- §4.4 named UX and Design as preconditions for all generation without ever saying what they are →
  each now has a clause.
- §4.4's version invalidation left the search unassigned, and the Conductor may not read → now names
  the Conductor grepping `verdicts/`, and says why rulings are inside its permitted inputs.
- §4.5's "**Four things are enough to resume**" counted the unbuilt run-state file → three today, with
  the proposal adding a fourth.
- §4.4 described the Conductor writing gate rulings in the present tense alongside record's real
  behaviour, so the proposal read as shipped → recast into the conditional.
- §4.6 said "a few legs structural, the rest defaults" and named only two, asking the reader to
  subtract at the exact moment the split decided their verdict → §4.6 now walks all six legs, labels
  each, and states the count.
- §4.6 credited version-pinning with catching unrequested work → separated: verification against the
  phase's signed document catches it; version-pinning keeps that check current.

**Self-correction after the round**, from re-reading my own §4.6: I had labelled the one-brief-per-wave
leg "structural" and totalled "one leg of six is structural". Neither is true — nothing stops a
Conductor dispatching two briefs. §4.6 now says none of the six legs is enforced, and names what is
actually structural underneath them (the empty context, the return-only boundary, the withheld spawn
tool). I also fixed a count of my own making: "one leg for each way work diverges" over three legs,
where §1 names two ways.

### Round 1 — part 2 (implementer or auditor, looking one thing up)

**Verdict: four of five lookups answerable, one not.** What a Turn must return, when a commit happens,
what a Plan item contains, and who may write what were all findable; the record and brief entries did
not restate their own returns, and the version-invalidation rule lives in §4.4, outside this part.

Headings navigated well at the entry level (`Turn(name) — gloss`) and badly at the chapter level,
where §6 was a question and §7 a bare category.

**Prose defects fixed (13).**

- §5.2, §5.3, §5.4 and §5.5 stated promises without the return and, in three cases, without the
  violation evidence the chapter's own lead-in promises for every entry → each now carries both.
- The CCS soft cap was called a "soft ceiling" with no value → 2,000 bytes, from the shipped
  definition.
- The attempt ceiling was referenced in §5.7 and §6 with no number → three attempts, with the pointer.
- `evidential-soundness` was named as what stands in for a document with no definition anywhere in the
  part → the four-part gloss now sits in §5.3, where the verifier that applies it is defined.
- "each of which is serial by construction" was asserted with no reason → the reason is now in the
  clause.
- §5.6's breach trace said "what the file's own history says", which points at git history under one
  backend and the `history/` directory under another → both named.
- §6's keep-rate parenthetical sat after the denominator and read as a gloss on the numerator →
  rewritten so the ratio reads in one pass.
- §6 said "the two properties" with a definite article, and part 2 never names them → named.
- "Elicit items" appeared only in a metrics parenthetical → glossed there.
- §5.5's run-state paragraph did not say whether the proposal is in force, so an auditor could not tell
  whether a missing file is a violation → now says it is not in force and nothing about it is
  auditable today.
- §5.4 and §5.5's headings were epigrams that did not say what the entry holds → renamed to labels.
- §6's and §7's chapter headings were a question and a category → renamed to what they contain.

### Round 2 — part 1

**Verdict: still half.** The drift-detection side flipped to decidable — the reader followed §3.1's now-concrete link (a Step derivable from its Plan, the Plan from the document above it, tested by the fourth fixed viewpoint, Verdict on disk) and ruled that it discharges the *first* of §1's two forms of divergence and not the second, which rests on §4.6's weakest leg. That is the document reporting the design accurately and the reader deciding on it, which is the trial working.

The bounded-context side went the other way: **the reader could not decide**, and named the blocker exactly. Everything load-bearing about the CCS had been deferred to §5.4, which this reader does not have, and what part 1 did say was internally inconsistent — §3.3's tree said "one file per wave, each a complete state", §4.2 said "a new file per wave rather than an accumulating one", §4.6 said "overwritten instead of extended", while the `tNNN` filenames plainly accumulate. And a "complete state" of a lengthening run reads as a growing object, which is the opposite of the claim.

**Prose defects fixed (18).**

- The CCS is now described in §4.2 in enough detail to be judged there: a new numbered file per wave, none ever appended to or edited, only the newest read, everything by path, the 2,000-byte ceiling explained as a diagnostic rather than a limit, no running summary beside it, and the claim stated as sub-linear rather than constant. The three inconsistent phrasings are gone.
- "Neither class is a promise that a rule was actually kept — the structural ones cannot be broken, the defaults can" was self-contradictory → rewritten.
- "Every rule falls into one of two classes and no third" collided with wall 2 being "structural, with one gap" → the text now says a rule can be structural for one party and a default for another, and names which definitions are which.
- **The reading wall was stated wrongly.** "Nothing from the artifacts reaches the Conductor... no products" contradicted the Conductor planning from a Purpose it must read. §2 now gives the closed input list in full and says the signed documents and the Plan are *in* it — the ban is on the work under construction and the maker's Report. The reader had found the resulting hole ("how does it compose a Plan derived from a Purpose it may not read?") and it was a real error in my prose, not in the design.
- §4.4's "so it writes nothing" contradicted the ledger's Conductor-authored Plans → scoped to phase products, with the Plan's status named.
- "Artifact" carried three senses (work under construction / everything in the ledger / files the plugin ships) → the ledger column is now "Product or record", §3.4 says "three kinds of file", and rule 3 in §5.1 says "the work under construction".
- §1 promised sub-linear growth, §4.6 claimed "none of which lengthens as the work does", which is constancy → §4.6 now states sub-linear and says so.
- §3.1's "Drift detection is nothing more than this two-layer arrangement" contradicted §4.6's three legs → scoped to making divergence visible.
- The chain diagram showed two Plan nodes for three Plans → the Purpose phase's Plan is now in the picture.
- "Four things must exist before anything can be generated" was circular, since the Purpose is itself generated → scoped to building the Deliverable, with the earlier phases' lighter prerequisites named.
- §4.5's "a resolved gate sets two parties writing" versus "approving a Planning Gate writes nothing" → reconciled in the text rather than left for the reader.
- "A viewpoint the Conductor notices missing" sat against the reading ban with no explanation → it now says what the Conductor compares (the Plan's declared viewpoints against the rulings), both already its own.
- "Deciding pass or fail is mechanical" versus "the final pass of verification is left to the model" → reconciled: what can be run is run first, and a model makes the last call against the same fixed yardstick.
- `wave` and `Verdict` were used in §3.1–3.3 and defined in §4.2 and a table cell → both now defined where the vocabulary is fixed.
- Turn(record) was glossed as "anything the platform must be asked to do" → named: commits, pushes, the pull request.
- Three families / four roles was left for the reader to reconcile → stated.
- The 10× ambition was stated in §1 and disowned four paragraphs later → the scope note now sits in the same sentence.
- Two restatements removed: the backend gloss duplicated between the tree comment and the paragraph below it, and the gate arithmetic duplicated between §2 and §4.4.
- Two headings that carried no claim were renamed ("Enforcement, said once" → "Nothing enforces this — two classes of rule instead"; "What carries the two properties" → "The CCS and the chain carry the two properties"), and §4.2's heading now names the CCS, which no heading had.

### Round 2 — part 2

**Verdict: three of five lookups fully answerable, two partial.** Navigation improved markedly — the reader reached the commit points, the version-writing rule and the verifier's inputs straight from the headings. What remained partial: the CCS's nine component names and what escalation actually does, both deferred out of the part.

**Prose defects fixed (10).**

- The chapter's own promise — "each entry gives a promise and the evidence a violation leaves" — was not kept: rules 1, 3 and 5 of the Turn contract had no evidence, and two of the CCS's operating rules had none. Every rule now carries its class and its trail, **including the two that have none**, said plainly: rule 2's evidence is unreachable through the loop's own returns, and nothing distinguishes brief paraphrasing a Report from brief reading the product.
- Rule 2 was listed as absolute and demoted to a default a paragraph later → each rule now carries its class inline, with the four Bash-carrying definitions named.
- Rule 3's "no other role may [handle the real work]" collided with the Conductor running interviews → the one exception is stated in the rule.
- "Platform" meant the agent runtime in §5.1 and the git host in §5.5 and §5.7 → disambiguated in both, with "writing a file to disk is not one of those" said outright.
- The local adapter's "same five points, same return" collided with "its single write" → it now says what it does at the other four.
- "Serial by construction" did not cover `on` and `dn`, which sit outside any wave → all five points now have their reason.
- "the identifiers of the dispatch" was a field with no shape → the three identifiers are named.
- A refused verify dispatch was "rejected, logged as a failure" with no actor → the verifier refuses and records a failed Verdict, and the schema has no separate refusal value.
- The 2,000-byte ceiling did not say whether anything fails → nothing fails; it is reported.
- Escalation was referenced with no content → §5.7 now says what it does. §5.2's heading now advertises the version line, which no heading did.

### Round 3 — part 1

**Verdict: one property decidable, one still blocked, and the blocker was mine.** Drift detection closed — the reader followed §3.1's link, agreed the chain makes divergence inspectable, and accepted §4.6's own statement that nothing makes it *detected*. Bounded context did not close, on a contradiction round 2's fix had introduced: §4.2 said "every product, file and log the wave touched appears in it as a path" while §4.6 leg 3 said "twice as many Steps in a wave does not mean twice as much for the Conductor to read." One brief per wave bounds the number of returns, not the size of the one return, and the reader said so.

**Prose defects fixed (14), the last round of fixes.**

- The width claim is now stated accurately in both places: the CCS does not shrink to a constant as a wave widens, six Steps naming more paths than one; what it does is grow far slower than the width, under a ceiling that does not move — the sub-linear claim §1 made, and no stronger one. §4.6's legs 2 and 3 were rewritten to match.
- "none of which grows with the number of Steps in flight" asserted constancy in the sentence before one that forbade it → both now say sub-linear.
- "overwritten instead of extended" (§4.6) versus "no file is ever appended to or edited" (§4.2) described two different operations → one phrasing in both.
- "What keeps that object from growing with the run, since judging bounded context means judging exactly this" was a question without its question mark, leading the most important paragraph in the bounded-context case → rewritten as a sentence.
- Part 1 never said what aiya is; the reader had to infer a Claude Code plugin from "subagent" and `gh` → §1 now opens with it.
- The vocabulary section came *after* the walls, so the document's central restriction ran on four nouns defined ten lines later → the words now precede the walls.
- "No supervising program runs anywhere" (§2) versus "the only executable piece anywhere in the design" (§3.4) → reconciled: nothing supervises the loop, and what runs is a model carrying out prose.
- §2 said the no-nest wall is structural for "the two definitions that ship without Bash" without naming them, and §4.6 then flattened it back to a blanket structural fact → both now name brief and the local record adapter, and say what remains for the other four.
- The chain diagram's new "reason the work exists" node implied a fourth Plan and collided with "the Purpose heads the chain with nothing above it" → removed; the Purpose phase's Plan is shown translating into Steps, like the other two.
- "The latter two" had its antecedent two sentences back, past an intervening pair → rewritten.
- "this document being one of those" made the reader stop and re-ask what kind of document they were holding → recast.
- "A resolved gate sets two parties writing" was general and retracted a page later → scoped to the numbered gates where it is first said.
- "chapter 6's arithmetic" was named as if already introduced → "chapter 6's three ratios".
- The part ended on a handoff with nothing addressed to the reader who has to decide → §4.6 now closes on what a reader can settle here (both properties are checkable) and what no reading of the document can settle (whether they are kept), before pointing at chapters 6 and 7.

### Round 3 — part 2

**Verdict: three of five lookups complete, one partial, one refused by the file itself.** Headings navigated on every attempt. The refusal was the CCS's nine component names, deferred to the Turn definition.

**Prose defects fixed (6).**

- `on`, `dn`, `up`, `gm`, "bare `gm`" and the gate identifiers G1–G3 were used throughout part 2 and defined only in part 1, which this reader does not have → chapter 5 now opens with both rosters, the six gates and the five command words, compactly.
- Attempts and re-aims were used in two ratios with no stated relation, leaving the arithmetic off by one → §6 states it: one attempt is one Turn(generate), the first is not a re-aim, so a Step that exhausts the cap has three attempts, two re-aims, three generates.
- Elicit items were excluded from all three ratios with no way to identify one → they are identifiable by absence, having no Report and no Verdicts.
- The 2,000-byte ceiling was "reported" with no destination, in an entry whose stated return is a path and nothing else → the swelling is visible in the CCS the Conductor reads next; it needs no channel.
- The local adapter "archives" with no shell → it reads the document and writes a copy.
- Verdict paths had no directory, and escalation's relationship to record was left to cross-reading → `verdicts/` is named, and §5.7 says no record dispatch attends an escalation.

### Delivery gate

**Three rounds run per part, the cap the skill sets. Delivery gate: open on part 2, closed on part 1 — and the skill's three-round rule delivers it anyway, named.**

Part 2 finished round 3 with no unfixed prose defect: every stumble it reported was either repaired above, or is one of the subject defects below.

Part 1 finished round 3 with **one prose defect outstanding and unverified**: the width-versus-size contradiction in the bounded-context case was fixed after round 3 reported it, and no fourth trial exists to confirm the fix reads as intended. The reader that reported it could not close bounded context; whether the corrected text closes it for the next reader is untested. Per the skill — "a prose defect that survives three rewrites is not going to be fixed by a fourth, so deliver and name it too" — this is delivered and named.

Two further residuals on part 1, both left standing deliberately:

- The reader's remark that "§4.6 answered my question for me… my job collapsed into checking the document's own self-assessment." That is the document being honest about an unenforced design rather than a defect in the prose; softening it would make the document lie more comfortably.
- Roughly two dozen pointers from part 1 into chapters 5–7. Inside a declared composite this is the composite working as designed, but it does mean part 1's reader is repeatedly sent to a part they were not given. Named here because the composite boundary is the owner's, not mine.

## Subject defects for the owner

Reported accurately by the document and **not patched**. Each is a property of the design or of its ratified format, and no rewrite removes one.

1. **"Two properties → two mechanisms" is not what the design does.** §2 names a lead mechanism per property; §4.6 needs three legs per property. Both part-1 readers hit it, one saying the framing "quietly declines" the question they were sent to answer. Either the lead-mechanism framing goes, or the document has to show why one leg of three leads. Left standing, with §2 saying plainly that neither mechanism carries its property alone.
2. **Five of the six legs are unenforced, and the sixth only partly.** Two independent readers reached the same place: the design is checkable but not enforced, and the wall against nesting is absolute only for the two definitions without a shell. This is chapter 2's stated choice, priced in chapter 7; it is a subject fact, not prose.
3. **Drift's second form has no mechanism.** Replanning from zero is an instruction to the Conductor with no trace when it is disobeyed — a Conductor that lightly edits the standing plan and calls it a rebuild leaves nothing behind that says so. Named by both part-1 readers as the weakest leg. The document says this outright.
4. **Bounded context is claimed for the working state; the transcript is outside it** and is cut back by a person typing `dn` → `/clear` → `up`. The property's name is broader than its discharge.
5. **Two load-bearing rules have no auditable trail** — Turn contract rule 2 for the four Bash-carrying definitions, and the CCS's "the product outranks the account", where nothing distinguishes brief paraphrasing a Report from brief reading the product. The part-2 reader called the first "not auditable, dressed as evidence."
6. **Whether an escalated Step counts in the keep rate's numerator is undefined.** The numerator is "Steps"; a Step stopped at the cap never settles. The arithmetic relation between attempts and re-aims is now stated, but this one is a definition the design has not made.
7. **Whether a verifier's refusal consumes an attempt is unspecified.** A refusal is recorded as a failed Verdict, and aggregation is an AND over Verdicts, so it appears to consume one — but nothing says so, and the consequence differs.
8. **Elicit items are exempt from verification, from the attempt cap and from all three ratios.** An unmeasured class of work sits inside a loop whose whole argument is that work is measured.
9. **Chapter 5 defers every schema, while the ratified format assigns them to it.** `aiya/references/design.md` says of chapter 5: "Format definitions live here." The document says the opposite: "Schemas, controlled vocabularies and filled examples live in the Turn definitions and references/; nothing here repeats them." Both part-2 readers hit the consequence — the Verdict's fields, the CCS's nine components, and the work order's contents are unavailable in the document that is supposed to be the reference. This is a conflict between the format and the document, and the owner owns both.
10. **The run-state proposal cannot be audited against.** An auditor cannot tell whether a missing run-state file is a violation, and "boundary event" is a trigger with no definition. This resolves when the owner rules on the proposal.

## Axis conflicts recorded (step 3)

The ratified Design format and the ratified composite boundary each put material in front of a reader who does not need it. Raised here rather than filled silently or deleted.

- **Chapter 3's physical layout and inventory sit in part 1.** The format requires the directory tree in Structure and the product inventory in the same chapter; three of the four part-1 trials named §3.3 and §3.4 as the largest blocks of content they did not need, one calling them "implementer material." They cannot move to part 2 without breaking the format's chapter assignment, and cannot be cut without emptying a mandated slot.
- **Chapters 6 and 7 are argument, in the part declared reference.** Both part-2 readers said §7 answers no question an implementer or auditor arrives with, and that two operational facts are buried inside the argument. The composite boundary at 5/7 is the owner's ratified decision; chapter 7's genre is the format's.
- **Content is stated twice across the boundary by design.** The CCS is described for judgement in §4.2 and for implementation in §5.4; the gate and command rosters appear in §2 and again at the head of chapter 5. Inside a declared composite each part must stand alone for its reader, so this is not restatement within a part — but it is duplication in the file, and it is the composite's price.

## Content kept out

Excluded at the step-3 heading admission, the step-4 point admission, or the step-7/8 rendering
admission. Each with the reader it serves and where it belongs.

| What | Whose reader | Where it belongs |
|---|---|---|
| The mnemonics behind the five command words (`on` = power on, `dn` = down for the day, `up` = back up, `ty` = thank you, `gm` = gimme a change) | A first-time *user* deciding what to type — neither the design evaluator nor the implementer | `aiya/README.md`, which already carries them; the input itself deferred them there |
| Installation and the worked walkthrough (marketplace add, `/plugin install`, the csv-export console transcript, the progress-board example output) | A prospective user | `aiya/README.md` |
| The aiya-versus-`rn` choosing guidance | A prospective user picking a tool | `aiya/README.md` |
| The proposed run-state file's literal YAML sample and field-by-field schema | An implementer building it — and not even that one yet, since the proposal is unresolved | With the conductor skill and `aiya/references/`, once the owner rules on the proposal. Part 1 names the four facts the file would hold, which is what an evaluator needs to judge §4.5's claim |
| Per-Turn dispatch parameter lists, the CCS's nine component names and their sources, the Verdict schema, the concurrency cap and wave slicing, the `type` vocabularies | An implementer with the code open | `aiya/agents/*.md` and `aiya/references/`. Chapter 5 states promises and violation evidence and explicitly defers schemas — the same line the input drew |
| The input's gate-sequence diagram | Nobody — six stops in a fixed order is a linear sequence | Cut, not relocated. The phase table in §4.4 carries the content, and the sentence beside it carries the ordering |
| The claim that investigation Steps are "where compression and independent checking pay most" | A reader already persuaded of the mechanisms — it argues their value, in a chapter about gates | Cut at round 2, after a reader named it as a bounded-context argument dropped far from the bounded-context case. It belongs with §4.6 if it belongs anywhere, and §4.6 does not need it |

No template slot was left unfilled: all seven chapters of the ratified Design format carry content, and
every one earned its place against its part's reader.
