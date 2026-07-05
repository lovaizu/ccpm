# design.md template

Read when creating a session's `design.md` — the whole-structure design doc that `steering.md` points
to from its top `Design:` line. **Not read at runtime**: it records decisions and how the parts fit so
whoever maintains the work can judge whether a change is still right.

The h2 sections below are the canonical design-document sections; under each, the h3 headings are the
questions that section must answer — a section is done when its questions are answered, not when its
heading merely exists.

## Steps

1. **Copy the template block below verbatim.** Keep every heading, numbering, and section order — the
   five h2 sections and the h3 questions under them are the contract (Detailed design's `4.N` repeats
   per mechanism — see step 3).
2. **Answer every h3 question with a decision and the reasoning behind it** — not just what is, but why
   it is that way. If a question does not apply, say so **and say why** — "not applicable" is itself an
   answer, and it gets the same decision-plus-reasoning treatment as any other. Nothing here licenses a
   section with a question left silently unanswered.
3. **In Detailed design, repeat `4.N` once per mechanism or component the design introduces** — not a
   fixed four; add or drop subsections to match what the design actually contains.
4. **Treat the whole document as optional, not any section within it.** If there is no design to record
   at all, write no `design.md` (an empty file is worse than none). But once you are writing one, no
   section may be skipped for having "nothing to record" — an empty-seeming section still owes step 2's
   decision-plus-reasoning answer, even if that answer is "not applicable."

---

```markdown
# <name> — design notes

Not read at runtime — for whoever maintains the design and needs to judge whether a decision is still
right when requirements change.

<every h3 below needs a decision-plus-reasoning answer — "not applicable" is an answer only when it says why>

## 1. Background & Goals

### 1.1 What is the goal?

### 1.2 What goes wrong without this?

### 1.3 What does reaching it require?

### 1.4 What is out of scope?

## 2. Assumptions & Constraints

### 2.1 What do we take as true?

### 2.2 What binds the solution?

## 3. Design overview

### 3.1 What is the core idea, and why does it solve the problem?

### 3.2 What are the pieces, and what is each responsible for?

### 3.3 How does work move?

## 4. Detailed design

<one 4.N subsection per mechanism/component the design introduces — repeat, do not cap at a fixed count>

### 4.1 What does <mechanism> guarantee, and how is a breach caught?

## 5. Alternatives considered

### 5.1 Why this shape, and not another?

### 5.2 What did we trade away?
```

---

## Per-section guidance

- **Background & Goals** — the goal (1.1), what fails without it (1.2), what achieving it demands
  (1.3), and what is deliberately out of scope (1.4). This frames every decision below; a reader who
  reads only this section should already understand why the rest of the design exists.
- **Assumptions & Constraints** — what is taken as true without re-litigating it (2.1), and what fixed
  limits bind the solution (2.2 — platform limits, resource bounds, no-extra-infrastructure rules,
  whatever actually constrains this design). This is the ground the Design overview stands on.
- **Design overview** — the core idea and why it solves the problem (3.1), the pieces and what each is
  responsible for (3.2), and how work moves between them (3.3). Answer at the level of the whole design,
  not implementation detail — that belongs in Detailed design.
- **Detailed design** — one `4.N` subsection per mechanism or component the design introduces (a queue, a
  cache, a state file, a retry policy — whatever this design actually contains). Every subsection asks
  the same pair of questions of its mechanism: what does it guarantee, and how is a breach of that
  guarantee caught?
- **Alternatives considered** — why this shape was chosen over another (5.1), and what was knowingly
  traded away by choosing it (5.2). This is where costs the design does not solve get named as accepted
  decisions, not left to be discovered later as oversights.
