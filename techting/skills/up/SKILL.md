---
name: up
description: This skill should be used when revising or brushing up an existing technical document — an article/explanation, guide, reference, record/ADR, or evaluation — so it reads cleanly for its intended reader; it also applies when authoring such a document from scratch. It fires whether a human asks for the revision or Claude is drafting or revising one itself. It defines the reader first (who they are, what they must decide or do, how they read) and derives voice, diagrams, closing, and outline from that definition.
version: 0.1.0
---

# Brush a technical document up

Raise a technical document a level so it reads as if a person wrote it, not an AI. Everything derives
from one decision — **who reads it** — and the work runs in a fixed order, each step emitting an
artifact you can check before the next begins.

Quality clears in two tiers. The **floor** is table-stakes: remove the AI tells, or the text instantly
reads as machine-written. The **ceiling** is what makes a cleared draft worth reading. Clear the floor
first — ceiling added onto an uncleared floor is wasted.

- **Input**: an existing draft. With no draft, author from scratch through the same steps.
- **Output**: the revised document plus a **what-changed note** — the floor scrub table (step 2) first,
  then the ceiling lifts (step 5), each tied to the reader (step 1) or an output rule.

This file is two layers, kept apart on purpose:

- **The procedure** — the operations you run while this skill is active.
- **Rules for the produced document** — constraints on the document you hand back.

Run the procedure; hold the produced document to the output rules. Do not confuse the two.

## The procedure

Run these in order: **reader → floor → axis → voice → restructure → self-check → deliver.** Each step
states what to emit. Do not start a step until the previous step's artifact exists.

### 1. Define the reader

Write these three lines before touching the draft:

- **Who** reads this document?
- **What** must they decide or do after reading?
- **How** do they read — straight through once, or looking up the part they need?

If the reader can't be pinned down, **do not guess.** Ask the user. When no user is reachable (a
model-invoked or headless run), infer the reader from the draft and state that assumption in one line
at the top of the output. Ask when you can; infer-and-declare when you can't; never silently guess.

**Emit**: the three lines (plus the inferred-reader line if you inferred).

### 2. Clear the floor

Inspect **every sentence** of the draft against these seven tells. This is the single definition of
the floor; later steps refer back here.

| Tell | How to spot it | Fix |
|---|---|---|
| Padding / throat-clearing | Opener announces intent instead of stating the point | Cut it; lead with the finding |
| Restatement | The same thing said twice in different words | Keep one |
| Retreat into generalities | A vague claim where a name, number, or example belongs | Make it concrete, or cut |
| Flavorless connectives | "moreover", "furthermore", "in addition" with no real link behind them | Remove, or write the real join |
| Reflexive bulleting | A list where the items aren't genuinely parallel | Write it as prose |
| Wavering voice | Register or stance drifts mid-document | Hold one voice |
| Hedging | "it is thought that…", "generally…", non-committal qualifiers | Assert with evidence, or mark `[unverified]` |

**Emit**: a scrub table, one row per tell you found — `| tell | quote from the draft | fix applied |`.
A tell with no row means you read for it and confirmed it absent. Do not proceed until all seven are
fixed or confirmed absent.

### 3. Pick one axis

Read the axis off the reader, not from memory. Choose exactly one of the five (their outlines are in
**The five axes**, output rules). **One document, one axis** — mixing axes is the top cause of a
confusing document. Push deep dives out to a separate document rather than padding this one.

**Emit**: the axis name, and one line on why it follows from the reader.

### 4. Derive voice

Choose voice, closing, and diagram emphasis for the reader from step 1. The **Voice by reader** table
(output rules) is an example to derive from — the reader is the source of truth, not the table.

**Emit**: one line naming the voice and closing you'll use.

### 5. Restructure and lift the ceiling

Reorder the draft to the axis outline, then add the ceiling: density and concreteness (names, numbers,
examples), a single load-bearing thread (conclusion first, headings that carry the argument), diagrams
where they beat prose, one consistent voice.

**Emit**: the revised document.

### 6. Self-check

Emit each line below with a **PASS/FAIL** verdict. Any FAIL → fix it and re-run this step. Ship only
when every line passes.

- [ ] **Floor**: the step-2 scrub table shows all seven tells fixed or confirmed absent.
- [ ] **Order**: the floor was cleared before any axis/voice/structure work.
- [ ] **Reader fit**: voice, diagrams, closing, and outline match the reader from step 1.
- [ ] **Single axis**: the document holds one axis, not a mix.
- [ ] **Inferred reader**: if you inferred the reader, that assumption is stated at the top.
- [ ] **Headings**: the headings alone carry the argument top to bottom.
- [ ] **Diagrams**: structure and flow are shown as mermaid, with no diagram/prose duplication.
- [ ] **Honesty**: fact is distinguishable from hypothesis; the unverified is marked.

### 7. Deliver

Hand back the revised document and the **what-changed note**: the step-2 scrub table (floor fixes)
first, then a list of ceiling lifts, in that order. Each entry names the change and ties it to the
reader (step 1) or an output rule below.

## Rules for the produced document

**These rules govern the document this skill produces — not this SKILL.md prompt.** They are
instructions to the output; the step-6 self-check tests them.

### The two tiers

- **Floor** — the produced document contains none of the seven AI tells the step-2 scrub removes.
  Failing any one reads as machine-written.
- **Ceiling** — density and concreteness (names, numbers, examples; cut what reads as noise); a single
  load-bearing thread (conclusion first; the headings alone carry the argument); diagrams and lists
  only where each beats prose; one consistent voice, derived from the reader.

Throughout: write in Markdown; let the reader tell fact from hypothesis (mark the unverified
`[unverified]`, don't fill gaps with guesses); don't hide what doesn't work, the costs, or the limits.

### Render structure and flow as mermaid

- Show **structure** (how parts relate) and **flow** (order of steps, transitions, dependencies) as a
  diagram, so the reader grasps them at a glance instead of from paragraph after paragraph.
- Write diagrams in **mermaid**. Don't repeat in prose what the diagram already carries.
- Choose by what's faster for the reader: a diagram for anything with order or branching, prose for a
  simple fact.

### The five axes

One role each. **Do not mix axes** in one document.

- **Article / explanation** — for someone reading to understand.
  1. What you'll learn (subject and premise, 1–2 sentences)
  2. The substance (one step at a time: stumbling point → why → what to do)
  3. In closing (what you gained, the limits, the next step)

  Link side-trips out to another article rather than cramming them in.

- **Guide / procedure** — for someone doing it right now.
  1. Goal and prerequisites (what gets done, what you need)
  2. Steps in order (each states its expected result; show branches as a diagram)
  3. Verification and troubleshooting (confirm it worked; common snags)

  Don't mix in teaching-style explanation.

- **Reference** — for someone looking things up.
  1. The whole picture (a structure diagram: parts and relationships)
  2. Each element (easy to look up, unique, exhaustive: input / output / constraints / defaults)
  3. Errors and terms (conditions and behavior; no ambiguity)

  No intro, no story. Structure it for lookup, not for reading through.

- **Record / ADR** — for someone tracing how a decision was reached.
  1. Background and the decision (what was decided, and why)
  2. The options considered (the rejected ones and their reasons are the main act)
  3. The outcome (the good and the bad)

  Don't list only the good outcomes.

- **Evaluation / survey** — for someone making a call.
  1. Conclusion / recommendation (what to choose, what not to)
  2. Criteria (what is measured, and why those criteria)
  3. Comparison (measurements stated neutrally; separate fact from judgment)
  4. Evidence and the next step

### Voice by reader

Derive the voice from the reader. This table is an example to derive from, not a fixed rulebook — the
reader definition (step 1) is the source of truth.

| Reader | Voice | Closing |
|---|---|---|
| Reads through (article / guide) | Warm and plain; an easy motive before each term | What was learned, and the limits |
| Looks things up (reference) | Uniqueness and coverage first; drop warmth and intros | None — skip the closing generality |
| Traces the history (record / postmortem) | Separate fact from analysis; names → roles | Action items |
| Makes a call (evaluation / survey) | Separate measurement from judgment; lay them out neutrally | A recommendation |
