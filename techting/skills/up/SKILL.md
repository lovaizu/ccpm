---
name: up
description: This skill should be used when brushing up, revising, polishing, or de-AI-ifying a technical document so it reads as if a person wrote it — an article/explanation, guide/procedure, reference, record/ADR, or evaluation/survey. It fires on requests like "brush this up", "make this not read like AI", "revise this doc", "polish this README/ADR", and it fires for Claude itself while drafting or revising such a document. It takes only the input's intent, defines the reader, and builds the document fresh through an ordered writing procedure so the AI tells never take hold, returning the rebuilt document plus a what-changed note.
version: 0.1.0
---

# Brush a technical document up

Input: a draft to revise, or a topic to author. Output: the rebuilt document plus a what-changed note.

Do not edit the draft in place. Editing drags the old wording along, and the result reads as patched. Take from the input only its content and the one thing it must get across; then **build the document fresh** through the steps below, in order. Built this way, the AI tells get no foothold — step 9 is a net for stragglers, not the main tool.

Two layers, kept apart:

- **The procedure** (next) — what to do now, while this skill runs.
- **Reference** (last section) — the outlines, voice, forms, and AI-tell list the steps draw on, and the bar the produced document must clear. The steps point to it by name.

## The procedure

Order: **understand → reader → outline → fill → story-check → voice & form → write → brush up → clear the floor → self-check & deliver.**

### 1. Understand the input

Say, in your own words: what the document is about, and the one thing it must convey (伝えたいこと). For an existing draft, read for intent — you will not reuse its sentences.

Emit: `Subject: … / Must convey: …`

### 2. Define the reader and the purpose

Write three lines: WHO reads this, WHAT they must decide or do afterward, HOW they read (straight through, or looking one thing up). The purpose is what they can do once they have read it.

Gate: if a line cannot be answered from the input, ask the user. On a headless run, infer it and prepend `Assumed reader: <who> / <what> / <how>` to the output. Never leave a line blank.

### 3. Build the outline from the purpose

Match the reader and purpose to exactly one axis (Reference → [the five axes](#the-five-axes)); its skeleton is your outline. One axis only — off-axis material stays out of this document; name it in the what-changed note (what was left out, and where it belongs).

Emit: the outline headings, specialized to this content.

### 4. Fill the outline with what you want to convey

Under each heading, drop the points it must carry as terse bullets — concrete (names, numbers, examples), one fact per bullet. This is content, not prose yet. A heading with nothing concrete to hold gets cut.

### 5. Read it as the reader; check the story

Become the reader from step 2 and read the filled outline top to bottom. Does it reach the purpose with no gap, no repeat, no detour? Fix the order and the gaps now, while it is still bullets and cheap to move.

Gate: a reader reaches the purpose reading straight down.

### 6. Decide voice and form from purpose and story

With the story standing, choose:

- **Voice and closing** — Reference → [voice by reader](#voice-by-reader), as a start, not a verdict.
- **The form of each part** — prose, list, table, diagram, or graph (Reference → [form](#form)). Pick each for the reader's speed. Choosing form deliberately here is what stops lists from breeding and keeps a diagram where structure belongs.

Emit: `Voice: … / Closing: …`, and the form chosen per section.

### 7. Write it out

Render the outline into the document in the chosen voice and forms. Lead each part with its point. Render structure and flow as mermaid wherever step 6 chose a diagram.

### 8. Brush up to the ceiling

Raise what makes it worth reading (Reference → [the two tiers](#the-two-tiers), ceiling): density and concreteness, one load-bearing thread with the conclusion first, headings that carry the argument read alone, one voice held throughout.

### 9. Clear the floor (the net)

Read the finished document once against the seven AI tells (Reference → [floor checklist](#floor-checklist-the-seven-ai-tells)). For each tell present, name it, quote the line, apply the fix. Most should be absent — the procedure kept them out; this catches the stragglers.

### 10. Self-check and deliver

Mark each PASS or FAIL; any FAIL, fix and re-check. Ship only when all PASS.

- [ ] Single axis (step 3), no mixing.
- [ ] A reader reaches the purpose reading top to bottom (step 5).
- [ ] Form fits content — mermaid for structure/branching, a list only when items are parallel (step 6).
- [ ] No prose repeats what a diagram carries (step 6, Reference → [form](#form)).
- [ ] Voice and closing fit the step-2 reader (step 6) — one wrong voice held throughout still fails.
- [ ] None of the seven tells remain (step 9).
- [ ] Headings alone carry the argument.
- [ ] `Assumed reader:` line present iff the reader was inferred (step 2).
- [ ] Fact separable from hypothesis; the unverified marked `[unverified]`.

Deliver two things: the rebuilt document, and the **what-changed note** — first the substance (the structure, story, and voice you built, each tied to the reader or purpose), then a short line on any AI tells step 9 caught. When the input was a topic, not a draft, nothing changed — the note reports the choices made instead: reader, axis, voice, each tied to why.

---

## Reference

**These rules govern the document this skill produces — not this SKILL.md prompt.** The step-10 self-check tests them against the produced document.

### The two tiers

What "good" means, in two tiers the procedure builds toward.

- **Floor (table-stakes)** — the document carries none of the seven tells in the [floor checklist](#floor-checklist-the-seven-ai-tells). Clearing it earns no praise; any one tell present reads as machine-written.
- **Ceiling (attractive)** — density and concreteness (names, numbers, examples; noise cut); a single load-bearing thread, conclusion first, headings carrying the argument alone; figures and lists only where each beats prose; one consistent voice.

Throughout: Markdown; mark the unverified `[unverified]`, state the scope actually verified, and do not fill gaps with guesses; do not hide what fails, the costs, or the limits.

### The five axes

One role each. **Do not mix axes** in one document. Specialize the headings to the content; do not add items that bloat the document; route deep dives to a separate document.

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

### Form

Choose each part's form for the reader's speed.

- **Diagram (mermaid)** — for structure (how parts relate) and flow (order, branching, dependencies), so the reader grasps them at a glance. Do not repeat in prose what the diagram carries.
- **List** — only when the items are genuinely parallel; otherwise write prose.
- **Table** — for several items compared on the same fields.
- **Graph** — for a trend or distribution that lives in the numbers.
- **Prose** — for a line of reasoning.

### Voice by reader

Starting point, not a rulebook — the step-2 reader is the source of truth.

| Reader | Voice | Closing |
|---|---|---|
| Reads through (article / guide) | Warm and plain; an easy motive before each term | What was learned, and the limits |
| Looks things up (reference) | Uniqueness and coverage first; drop warmth and intros | None |
| Traces history (record / ADR) | Separate fact from analysis; names → roles | Action items |
| Makes a call (evaluation / survey) | Separate measurement from judgment; lay them out neutrally | A recommendation |

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
