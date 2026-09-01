---
name: up
compatibility: Step 11 launches a fresh-context subagent to read the produced document. Where subagents are unavailable, the reader trial is skipped and the delivery note says so.
description: This skill should be used when brushing up, revising, polishing, or de-AI-ifying a document so it reads as if a person wrote it — an article/explanation, guide/procedure, reference, record/ADR, or evaluation/survey. It fires on requests like "brush this up", "make this not read like AI", "revise this doc", "polish this README/ADR", and it fires for Claude itself while drafting or revising such a document. It takes only the input's intent, defines the reader, and builds the document fresh through an ordered writing procedure so the AI tells never take hold, returning the rebuilt document plus a what-changed note.
---

# Brush a document up

Input: a draft to revise, or a topic to author. Output: the rebuilt document plus a what-changed note.

Do not edit the draft in place. Editing drags the old wording along, and the result reads as patched. Take from the input only its content and the one thing it must convey; then **build the document fresh** through the steps below, in order. Built this way, the AI tells get no foothold — step 9 is a net for stragglers, not the main tool.

Two layers, kept apart:

- **The procedure** (next) — what to do now.
- **Reference** (last section) — the outlines, voice, forms, and AI-tell list the steps draw on, and the bar the produced document must clear.

## The procedure

Order: **understand → reader → outline → fill → story-check → voice & form → write → brush up → clear the floor → self-check → reader trial & deliver.**

### 1. Understand the input

Say, in your own words: what the document is about, and the one thing it must convey. For an existing draft, read for intent — you will not reuse its sentences.

Then sort what the input asserts, by status: what is **in force** (already true, already built), what is **proposed** (put forward, not yet in force), what is a **hypothesis**. A proposal is not an error to correct against the world — carry its status forward, and never drop a point because reality has not caught up with it yet. Content leaves only through the step-3 admission.

Emit: `Subject: … / Must convey: … / Proposed, not in force: …`

### 2. Define the reader and the purpose

Write three lines about **one person in one reading stance**: WHO reads this, WHAT they must decide or do afterward, HOW they read (straight through, or looking one thing up). The purpose is what they can do after reading. With several implied audiences, the Gate below picks the primary; the step-3 admission keeps the others' needs out, and the what-changed note names them — a bundled reader admits everything.

Gate: if the input cannot answer a line, or answers it several ways, ask the user. On a headless run, infer it and prepend `Assumed reader: <who> / <what> / <how>` to the output. Never leave a line blank.

### 3. Build the outline from the purpose

Match the reader and purpose to exactly one axis (Reference → [the five axes](#the-five-axes)); its skeleton is your outline. Then test it against the step-2 reader **both ways**.

- **Slot → reader.** A heading stays only if that reader needs it to reach the purpose. One serving anyone else — a re-reader, a past reviewer, an approver — or off-axis material stays out; name it in the note (whose it is, where it belongs).
- **Reader → slot.** List what that reader must have to reach the purpose and name the slot carrying each; a slot that defers the thing elsewhere does not carry it. A need with no slot — most often the answer itself, which the ceiling puts first — is the same conflict in the other direction. Raise it as a **proposed slot**: where it belongs, and the reader evidence for it. Never absorb it as prose under the nearest heading; that is how the answer ends up at the back.

A user-supplied outline or format faces both tests. Either verdict is an axis conflict — raise it with the user; never fill an unjustifiable slot silently, never bury an unslotted need. Headless: leave that slot unfilled, place the proposed one where the reader needs it, and record both in the note.

When the content genuinely needs two axes — an argument to read through, plus an inventory to look things up in — it is two documents. Say so and split them: that is the first answer. If the owner keeps them in one file, declare the parts rather than blending them — each part carries its own step-2 reader line and its own axis at its head, and every admission below runs per part against that part's reader. Never blend two readers inside one part. A composite has to be two documents in fact: at step 5, walk each part alone — a part whose reader cannot reach its purpose without crossing into the other is not a part, and the split goes back to the owner as the answer. The what-changed note records the composite and why the split was refused.

Emit: the outline headings, specialized to this content.

### 4. Fill the outline with what you want to convey

Under each heading, drop the points it must carry as terse bullets — concrete (names, numbers, examples), one fact per bullet. Write every bullet in your own words; one that reads like the draft's own sentence was copied, not rebuilt. The step-3 admission holds per point: one the step-2 reader does not need goes to the what-changed note instead. Content, not prose yet. A heading with nothing concrete to hold gets cut.

### 5. Check the story in the reader's order

Walk the filled outline in the step-2 reader's order. Does it reach the purpose with no gap, no repeat, no detour? Fix order and gaps now, while still bullets and cheap to move. Then set the filled outline beside the input: a bullet carrying the input's phrasing was transcribed, not written — re-fill it from meaning now, where the fix costs one bullet instead of a whole render. The author's structure check — a real reader reads at step 11.

### 6. Decide voice and form from purpose and story

With the story standing, choose:

- **Voice and closing** — Reference → [voice by reader](#voice-by-reader).
- **The form of each part** — prose, list, table, diagram, or graph (Reference → [form](#form)).

Emit: `Voice: … / Closing: …`, and the form chosen per section.

### 7. Write it out

Close the input. From here the filled outline is your only source — the draft is not open, not consulted, not quoted. Render the outline into the document in the chosen voice and forms. Lead each part with its point. Rendering adds no content the filled outline does not carry — a sentence that appears only at this step faces the same step-3 admission.

### 8. Brush up to the ceiling

Raise the document to the ceiling (Reference → [the two tiers](#the-two-tiers), ceiling). Anything added here — an example, a number — faces the same step-3 admission.

### 9. Clear the floor (the net)

Read the finished document once against the seven AI tells (Reference → [floor checklist](#floor-checklist-the-seven-ai-tells)). For each tell present, name it, quote the line, apply the fix, and carry it into the what-changed note.

### 10. Self-check the mechanics

Mark each PASS or FAIL; any FAIL, fix and re-check.

- [ ] Reader is one person in one reading stance (step 2).
- [ ] One axis, no mixing (step 3) — a declared composite instead carries one axis and one reader per part, stated at its head.
- [ ] Nothing carried over from the input's wording but names, identifiers, defined terms, and material quoted on purpose — read the two side by side and confirm it. Having been told to rebuild is not evidence that you did.
- [ ] Every heading and point admitted by the step-2 reader, and every reader need carried by a slot (step 3, both directions); content kept out, and slots proposed, named in the note.
- [ ] Form fits content — mermaid for structure/branching, a list only when items are parallel (step 6).
- [ ] No prose repeats what a diagram carries (step 6, Reference → [form](#form)).
- [ ] Voice and closing fit the step-2 reader (step 6) — one wrong voice held throughout still fails.
- [ ] None of the seven tells remain (step 9).
- [ ] `Assumed reader:` line present iff the reader was inferred (step 2).
- [ ] Produced size against the input's is recorded and any growth named as something the step-2 reader needed. No bar — growth you cannot argue for is unadmitted fill.
- [ ] Every claim carries its status — fact with source, hypothesis marked and testable, decision with intent; no unmarked assertion (Reference → [the two tiers](#the-two-tiers)).

### 11. Reader trial, then deliver

The author cannot simulate ignorance. Launch a fresh-context subagent with **only** the produced document and the step-2 reader definition — no outline, no draft, no history. A declared composite gets one trial per part, each given only that part and that part's reader. It reads as that reader, top to bottom, and reports:

- Did it reach the purpose?
- Do the headings alone carry the argument?
- Where did it stumble — including anything that read as machine-written: a sentence you had already read, a figure that disagrees with the prose?
- What content did it not need — and, when it can tell, whom does that content serve?

Sort each stumble before touching it:

- **Prose defect** — the document says it badly. Yours to fix.
- **Subject defect** — the document reports the thing accurately and the thing itself is what the reader trips on: a count that does not add up, a rule with a hole, two claims that contradict each other. No rewrite removes it, and a clause that smooths it over only makes the document lie fluently. Do not patch it. Name it in the what-changed note for whoever owns the subject, and leave the claim standing — or strike it, if it was never this document's to assert.
- **Format defect** — the document is arranged as a supplied format demands, and the reader needs an arrangement that format cannot express; the answer stranded at the back is the standard case. Rewriting inside the slots cannot reach it, and renaming a heading moves nothing. Raise it as step 3's proposed slot, with the reader's own words as evidence.

Fix the prose defects; cut or move out reported unneeded content under the step-3 admission, named in the what-changed note. A fixed document re-passes step 10, then reruns with a new fresh reader. Delivery is gated on **no prose defect remaining** — subject defects, and a proposed slot the owner has not ruled on, ship named instead of blocking. Stop after three trial rounds either way: a prose defect that survives three rewrites is not going to be fixed by a fourth, so deliver and name it too. End on a trial, never on an edit — when the cap falls after a fix, hand a fresh reader the changed passages and only those; whatever that read cannot confirm ships named as unverified.

If this environment cannot launch a subagent, the gate cannot run. Do not stand in for it — reading it yourself is what this step exists to replace. Deliver, and say plainly in the note that the trial did not run, so the document is unverified against a fresh reader.

Deliver the rebuilt document and the **what-changed note** — the structure, story, and voice built, each tied to the reader or purpose; content kept out at any admission point, steps 3–4 or 7–8 (whose reader it served, where it belongs); any slot proposed or left unfilled, with its evidence; any tells step 9 caught. For a topic input, the note reports the choices instead: reader, axis, voice, each tied to why.

---

## Reference

**These rules govern the document this skill produces — not this SKILL.md prompt.** Steps 10–11 test them against the produced document.

### The two tiers

- **Floor (table-stakes)** — the document carries none of the seven tells in the [floor checklist](#floor-checklist-the-seven-ai-tells). Clearing it earns no praise; any one tell present reads as machine-written.
- **Ceiling (attractive)** — the reader reaches the purpose with minimal effort. Means, not ends: density and concreteness (names, numbers, examples; noise cut); a single load-bearing thread with the conclusion first; headings carrying the argument alone; the few load-bearing claims distinguishable at a glance — placement, a heading, a lead sentence, not decoration; figures and lists only where each beats prose; one consistent voice.

Throughout: Markdown; every claim carries one of three statuses — a **fact** is asserted plainly, with its source and the scope verified where the claim is non-obvious or load-bearing; a **hypothesis** is marked ("hypothesis" / `[unverified]`) with its grounds and what would confirm it; a **decision** is written as a choice with its intent, never dressed as a truth, and one not yet in force says so. Do not fill gaps with guesses; do not hide what fails, the costs, or the limits.

### The five axes

One role each. **Do not mix axes.** Specialize the headings to the content; deep dives stay out of scope. A tutorial is the guide/procedure axis specialized for learning (a visible result at every step; explanation linked out, not inlined); a postmortem, the record/ADR axis specialized for an incident.

- **Article / explanation** — for someone reading to understand.
  1. The question and its answer (the why-question this document answers, and the answer to it, in 1–2 sentences)
  2. The substance (per unit: claim → why → implications and connections; alternatives and background welcome, instructions are not)
  3. In closing (the limits, what it does not settle, pointers onward — not a recap of the answer)

- **Guide / procedure** — for someone doing it now.
  1. Goal and prerequisites (what gets done, what is needed)
  2. Steps in order (imperative, location before action, each states its expected result; one best path — branch only where the reader's context genuinely differs, branches as a diagram)
  3. Verification and troubleshooting (confirm it worked; common snags; cleanup or rollback when steps are destructive)

- **Reference** — for someone looking things up.
  1. The map (structure mirrors the product's own, so the reader navigates code and docs in parallel; a structure diagram where it helps)
  2. Each element (consistent fields: input / output / constraints / defaults; unique and exhaustive; neutral, terse examples allowed)
  3. Errors and terms (conditions and behavior; no ambiguity)

- **Record / ADR** — for someone tracing how a decision was reached.
  1. Status (proposed / accepted / superseded) and date; the context and the problem
  2. The decision and its drivers (the chosen option and why — the headline)
  3. Options considered (pros and cons of each — the rejected ones and their reasons are what the tracing reader came for)
  4. Consequences (the good and the bad)

- **Evaluation / survey** — for someone making a call.
  1. Conclusion / recommendation (what to choose, what not to)
  2. Criteria (what is measured, and why those criteria; state weights when they conflict)
  3. Comparison (measurements stated neutrally; fact separated from judgment)
  4. Evidence and the next step

### Form

Choose each part's form for the reader's speed.

- **Diagram (mermaid)** — for structure (how parts relate) and flow (order, branching, dependencies), so the reader grasps them at a glance; when prose reads faster — a short linear sequence, or a structure a sentence can carry — skip it. Do not repeat in prose what the diagram carries.
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
| Traces history (record / ADR) | Separate fact from analysis; names → roles | Consequences; action items when any follow |
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
| 7 | Hedging | "it is thought that" / "generally" / non-committal qualifiers | State it as fact, hypothesis, or decision |
