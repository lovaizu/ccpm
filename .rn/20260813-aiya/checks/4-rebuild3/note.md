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
that supports it.** Rendered here as **§1.4 "The answer — two mechanisms, six legs"**: two tables
(three legs per property, each with what it bounds or catches and where its machinery is), then the
qualifier. Position: last section of chapter 1. The alternative considered and rejected was a new
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
