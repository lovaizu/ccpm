# Writing the Design

The document that fixes a product's foundational design. **One per product** — never one per unit of work. A feature's design judgments belong in that unit's Approach and Decisions. This format is used twice only: when a product is founded, and when a revision touches the foundation — its invariants and rules.

Generation needs yardsticks — only when purpose, UX, design, and plan exist can anything be built or verified. If a project has no design, write one in this format before running.

Seven fixed chapters — Problem / Core / Structure / Behavior / Rules / Observability / Trade-offs — each titled "Chapter — a product-specific gist." Headings are English words; the body may be any language. **Verify that the headings alone tell the story.** Chapters 1–4 are a story read top to bottom; 5 onward are reference to be consulted. Write the body in logical names, with the physical layout appearing exactly once, in Structure.

## What each chapter is for

**1. Problem — what is aimed at, and what breaks.**
The goal. The failure modes if left alone. The properties the solution must guarantee (all later design is verified against these). Out of scope.

**2. Core — the skeleton of the answer.**
The roles, and the invariants and walls to be kept. The whole visible in one diagram. Vocabulary is fixed here too.

**3. Structure — what exists, and who owns it (static).**
The inventory of products and their relations. The ownership ledger — who writes, who verifies, who approves. Physical layout, exactly once.

**4. Behavior — how it moves (dynamic).**
Start from the smallest unit's lifetime, then widen: bundles, steering, gates, suspension. One diagram, one claim.

**5. Rules — what each part promises.**
Per part: the rules, and how a breach is caught. Format definitions live here.

**6. Observability — how health is known.**
The measures, how they are read, and why they are readable (what is recorded where).

**7. Trade-offs — shapes discarded, costs paid.**
Discarded alternatives and the reasons. The costs accepted with this shape — stated so they read as accepted, not overlooked.

## Worked example

The worked example of this format is aiya's own design document — [docs/design.md](../docs/design.md). Its chaptering, diagram discipline, ownership ledger, and rule format can be used as the template directly.
