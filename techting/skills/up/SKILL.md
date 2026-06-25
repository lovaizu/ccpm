---
name: up
description: This skill should be used when revising or brushing up an existing technical document — an article/explanation, guide, reference, record/ADR, or evaluation — so it reads cleanly for its intended reader; it also applies when authoring such a document from scratch. It fires whether a human asks for the revision or Claude is drafting or revising one itself. It defines the reader first (who they are, what they must decide or do, how they read) and derives voice, diagrams, closing, and outline from that definition.
version: 0.1.0
---

# Brush a technical document up

Raise a technical document a level by deriving everything from one decision: **who reads it.** Voice,
diagrams, closing, and outline are not memorized per document type — they all follow from the reader
definition. The same procedure authors from scratch, but the primary mode is brushing up an existing
draft.

- **Input**: an existing draft to revise. With no draft, author from scratch through the same steps.
- **Output**: the revised document, plus a short **what was changed and why** note that ties each
  change back to the reader definition (step 1) or a house-style rule (the output rules below).

This file has two layers, kept separate on purpose:

- **The procedure** — what to do, step by step, when running this skill (process layer).
- **Rules for the produced document** — constraints on the document handed back (output-rules layer).

Run the procedure. Hold the produced document to the output rules. Do not confuse the two.

## The procedure

Steps run in order. The pre-output self-check gates delivery: on any failure, fix and re-check.

### 1. Define the reader — everything starts here

State each of these in one line before writing:

- **Who** is the reader of this document?
- **What** must the reader be able to decide or do after reading?
- **How** does the reader read — top to bottom in one pass, or looking up the part they need?

These three regulate the voice, diagrams, closing, and outline that follow. Derive the differences
between document types from this definition — do not memorize them as rules.

**Ask-or-infer gate.** If the reader cannot be pinned down, **do not guess.** Ask the user. When no
user is reachable — the skill fired model-invocably, or a headless run — infer the reader from the
draft's own context and **state that assumption in one line at the top** of the output before
writing. Ask when possible; infer-and-declare when not; never silently guess, never stall.

### 2. Pick the axis and outline

Use the outline matching the defined reader. The five axes and their outlines are in **The five
axes** (output rules) below. Read the axis off the reader definition, not from memory.

**Give each document a single role — do not mix axes.** Mixing is the biggest cause of a confusing
document. Adapt the headings to the content (don't paste them verbatim), but don't add items that
make the document heavier — push deep dives out to a separate document. Small-document exception:
when a split would cost the reader more than it saves, keep a minimal inline version (e.g. only the
required fields) and link the exhaustive one out, rather than spawning a file for a few entries.

### 3. Derive voice from the reader

Choose voice, closing, and diagram emphasis for the reader defined in step 1 — do not fix them as
rules. The **Voice by reader** table (output rules) is an example to derive from, not a list to
memorize; the reader definition is the source of truth.

### 4. Run the pre-output self-check

Run this before delivering. On any failure, fix it and re-check — do not ship until all pass.

- [ ] Do voice, diagrams, closing, and outline match the reader defined at the top?
- [ ] Does the document hold a single axis (axes not mixed)?
- [ ] If the reader was inferred (no user to ask), is that assumption stated at the top?
- [ ] Do the headings alone carry the argument?
- [ ] Are structure and flow shown as diagrams, with no diagram/prose duplication?
- [ ] Can the reader tell fact from hypothesis, with the unverified marked?
- [ ] Are hedging, boilerplate AI vocabulary, and noise all gone?

### 5. Deliver

Hand back the revised document together with the **what changed and why** note. Each entry names the
change and ties it to the reader definition (step 1) or a house-style output rule.

## Rules for the produced document

**These rules govern the document this skill produces — not this SKILL.md prompt.** They are
instructions to the output. Hold the delivered document to them; the self-check above tests them.

### House style — how the content is written

Holds across every axis.

- Write in Markdown.
- Order it so the reader understands reading top to bottom. Check that the **headings alone** carry
  the argument.
- Stay dry — don't explain the same thing twice.
- Cut anything the reader would feel as noise. If it isn't on the main line, remove it.
- Let the reader tell **fact from hypothesis and judgment.** Mark the unverified `[unverified]` —
  don't fill gaps with guesses; show how far you confirmed.
- Avoid hedging ("it is thought that…", "generally…") and boilerplate AI phrasing. If you can't
  assert it, give the evidence or write `[unverified]`.
- Don't hide what doesn't work, the costs, the limits. Honesty over the appearance of polish.

### Render structure and flow as mermaid

- Show **structure** (how components relate, hierarchy) and **flow** (order of steps, state
  transitions, dependencies) as a diagram so the reader grasps them at a glance — don't explain them
  in prose paragraph after paragraph.
- Write diagrams in **mermaid**. Don't repeat in prose what the diagram already shows — let the
  diagram carry it and keep prose to supplements.
- Choose by what's faster for the reader: a diagram for anything with order or branching, prose for a
  simple fact.

### The five axes

Each axis has a single role. **Do not mix axes** in one document.

- **Article / explanation** — for someone reading to understand.
  1. What you'll learn (subject and premise, in 1–2 sentences)
  2. The substance (one step at a time: stumbling point → why → what to do, each with its reason)
  3. In closing (what you gained, the limits, the next step)

  Don't cram in explanation. Link side-trips out to another article.

- **Guide / procedure** — for someone doing it right now.
  1. Goal and prerequisites (what gets accomplished, what you need)
  2. Steps (in order; each states its expected result; show branches as a diagram)
  3. Verification and troubleshooting (confirm it worked; common snags)

  Don't mix in teaching-style explanation.

- **Reference** — for someone looking things up.
  1. The whole picture (a structure diagram: components and relationships)
  2. Each element (easy to look up, unique, exhaustive: input / output / constraints / defaults)
  3. Errors and terms (conditions and behavior; leave no ambiguity)

  No intro, no story. Structure it for lookup, not for reading through.

- **Record / ADR** — for someone tracing how a decision was reached.
  1. Background and the decision (what was decided, and why)
  2. The options considered (the rejected ones and the reasons are the main act)
  3. The outcome (both the good and the bad)

  Don't list only the good outcomes.

- **Evaluation / survey** — for someone making a call.
  1. Conclusion / recommendation (what to choose, what not to)
  2. Criteria (what is measured, and why those criteria)
  3. Comparison (measurements stated neutrally; don't collect only the facts favoring one side;
     separate fact from judgment)
  4. Evidence and the next step

### Voice by reader

Derive the document's voice from the reader. This table is an example to derive from, not a fixed
rulebook — the reader definition (step 1) is the source of truth.

| Reader | Voice | Closing |
|---|---|---|
| Reads through (article / guide) | Warm and plain; put an easy motive before each term | What was learned, and the limits |
| Looks things up (reference) | Uniqueness and coverage first; drop warmth and intros | None — skip the closing generality |
| Traces the history (record / postmortem) | Separate fact from analysis; replace personal names with roles | Action items |
| Makes a call (evaluation / survey) | Separate measurements from judgment; lay them out neutrally | A recommendation |
