---
name: up
description: This skill should be used when brushing up, revising, polishing, or de-AI-ifying a technical document so it reads as if a person wrote it — an article/explanation, guide/procedure, reference, record/ADR, or evaluation/survey. It fires on requests like "brush this up", "make this not read like AI", "revise this doc", "polish this README/ADR", and it fires for Claude itself while drafting or revising such a document. It defines the reader first, then removes AI tells, then raises density and structure, returning the revised document plus a what-changed note.
version: 0.1.0
---

# Brush a technical document up

Input: a draft (or, with no draft, the topic to author). Output: the revised document plus a what-changed note. Run the procedure below in order. Each step has a gate; do not start a step until the prior step's artifact exists and its gate passes.

This file has two layers, kept apart:

- **The procedure** (next section) — operations to execute now, while this skill is active.
- **Output rules** (last section) — constraints on the document being handed back.

Execute the procedure. Hold the produced document to the output rules.

## The procedure

Order: **reader → floor → axis → voice → restructure → self-check → deliver.**

### 1. Define the reader

Write these three lines:

- WHO reads this document.
- WHAT they must decide or do after reading.
- HOW they read — straight through, or looking up one part.

Gate: if any line cannot be answered from the draft, stop and ask the user. If no user is reachable (headless / model-invoked run), infer each line from the draft and prepend one line to the output: `Assumed reader: <who> / <what> / <how>`. Never leave a line blank; never guess silently.

### 2. Clear the floor

Read **every sentence** of the draft against the seven tells in the [floor checklist](#floor-checklist-the-seven-ai-tells) (output rules). Produce this table — one row per tell, all seven present:

```
| Tell | Found? | Quote from draft | Fix applied |
```

Rules for the table: every one of the seven tells gets a row. `Found? = no` means the draft was read for that tell and it is absent (quote column: `—`). `Found? = yes` requires a verbatim quote and the concrete fix. A tell may not be marked `no` without having read for it.

Gate: all seven rows present; every `yes` row has a quote and a fix. Apply every fix to the draft before step 3.

### 3. Pick one axis

Match the reader (step 1) to exactly one of the five axes in [The five axes](#the-five-axes) (output rules). Write: `Axis: <name> — because the reader <quote the relevant part of step 1>`.

Gate: exactly one axis named, justified by the step-1 reader. Mixing axes is forbidden; route any out-of-axis material to a separate document and note it.

### 4. Set voice and closing

Derive voice and closing from the reader, using [Voice by reader](#voice-by-reader) (output rules) as a starting table, not a fixed answer. Write: `Voice: <one phrase>. Closing: <one phrase>.`

Gate: both named, consistent with the step-1 reader.

### 5. Restructure and lift the ceiling

Reorder the floor-cleared draft to the step-3 axis outline. Then apply the ceiling (defined in [The two tiers](#the-two-tiers), output rules): conclusion first, density and concreteness (names / numbers / examples), one load-bearing thread, earned diagrams and lists, one voice. Render structure and flow as mermaid per the output rules.

Artifact: the revised document.

Gate: the document follows the step-3 outline and obeys every output rule.

### 6. Self-check

Mark each line PASS or FAIL. Any FAIL → fix and re-run this step. Ship only when all PASS.

- [ ] Floor — every tell in the step-2 table is `no`, or its `yes` row shows a fix now applied.
- [ ] Order — floor was cleared (step 2) before axis / voice / restructure.
- [ ] Single axis — the document holds the one step-3 axis, no mixing.
- [ ] Reader fit — voice, closing, diagrams, outline match step 1.
- [ ] Assumed-reader line — present at top iff the reader was inferred (step 1).
- [ ] Headings — reading headings top to bottom carries the argument.
- [ ] Mermaid — structure and flow are mermaid; no diagram/prose duplication.
- [ ] Honesty — fact separable from hypothesis; unverified marked `[unverified]`.

### 7. Deliver

Hand back two things:

1. The revised document.
2. The **what-changed note**, in this order:
   - **Floor fixes** — the step-2 table (its `yes` rows).
   - **Ceiling lifts** — a list of step-5 changes, each tied to the reader (step 1) or a named output rule.

---

## Output rules

**These rules govern the document this skill produces — not this SKILL.md prompt.** The step-6 self-check tests them against the produced document.

### The two tiers

- **Floor** — the produced document contains none of the seven tells in the [floor checklist](#floor-checklist-the-seven-ai-tells). Any one present reads as machine-written.
- **Ceiling** — density and concreteness (names, numbers, examples; cut noise); a single load-bearing thread, conclusion first, headings alone carrying the argument; diagrams and lists only where each beats prose; one consistent voice.

Throughout: Markdown; mark the unverified `[unverified]` and do not fill gaps with guesses; do not hide what fails, the costs, or the limits.

### Floor checklist (the seven AI tells)

| # | Tell | Spot it | Fix |
|---|---|---|---|
| 1 | Padding / throat-clearing | Opener announces intent instead of stating the point | Cut it; lead with the finding |
| 2 | Restatement | The same thing said twice in different words | Keep one |
| 3 | Retreat into generalities | A vague claim where a name, number, or example belongs | Make it concrete, or cut |
| 4 | Flavorless connectives | "moreover" / "furthermore" / "in addition" with no real link | Remove, or write the real join |
| 5 | Reflexive bulleting | A list whose items are not genuinely parallel | Write it as prose |
| 6 | Wavering voice | Register or stance drifts mid-document | Hold one voice |
| 7 | Hedging | "it is thought that" / "generally" / non-committal qualifiers | Assert with evidence, or mark `[unverified]` |

### Render structure and flow as mermaid

- Show **structure** (how parts relate) and **flow** (order, transitions, dependencies) as a **mermaid** diagram, so the reader grasps them at a glance.
- Do not repeat in prose what the diagram carries.
- Choose by speed for the reader: diagram for order or branching, prose for a simple fact.

### The five axes

One role each. **Do not mix axes** in one document. Specialize the outline headings to the content; do not add items that bloat the document; route deep dives to a separate document.

- **Article / explanation** — for someone reading to understand.
  1. What you'll learn (subject and premise, 1–2 sentences)
  2. The substance (one step at a time: stumbling point → why → what to do)
  3. In closing (what was gained, the limits, the next step)

- **Guide / procedure** — for someone doing it now.
  1. Goal and prerequisites (what gets done, what is needed)
  2. Steps in order (each states its expected result; branches as a diagram)
  3. Verification and troubleshooting (confirm it worked; common snags)

- **Reference** — for someone looking things up.
  1. The whole picture (a structure diagram: parts and relationships)
  2. Each element (lookup-friendly, unique, exhaustive: input / output / constraints / defaults)
  3. Errors and terms (conditions and behavior; no ambiguity)

- **Record / ADR** — for someone tracing how a decision was reached.
  1. Background and the decision (what was decided, and why)
  2. The options considered (the rejected ones and their reasons are the main act)
  3. The outcome (the good and the bad)

- **Evaluation / survey** — for someone making a call.
  1. Conclusion / recommendation (what to choose, what not to)
  2. Criteria (what is measured, and why those criteria)
  3. Comparison (measurements stated neutrally; fact separated from judgment)
  4. Evidence and the next step

### Voice by reader

Starting point, not a rulebook — the step-1 reader is the source of truth.

| Reader | Voice | Closing |
|---|---|---|
| Reads through (article / guide) | Warm and plain; an easy motive before each term | What was learned, and the limits |
| Looks things up (reference) | Uniqueness and coverage first; drop warmth and intros | None |
| Traces history (record / ADR) | Separate fact from analysis; names → roles | Action items |
| Makes a call (evaluation / survey) | Separate measurement from judgment; lay them out neutrally | A recommendation |
