# The five axes

One role each. **Do not mix axes.** The numbered items under an axis are its slots; specialize their headings to the content, and keep deep dives out of scope. A tutorial is the guide/procedure axis specialized for learning (a visible result at every step; explanation linked out, not inlined); a postmortem, the record/ADR axis specialized for an incident.

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
