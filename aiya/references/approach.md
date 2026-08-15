# Writing the Approach

The document that fixes *how we will get there*. It consists of **one body per unit of work** and **zero or more Decision annexes** (references/decision.md). At G2 the human reads only the body — keep it graspable in minutes and put the grounds for each decision in an annex. Small jobs may fold everything into the body; split out an annex once the body stops being a minutes-long read — bloat is the signal to split.

Three chapters, with **Testing first** — fixing how quality will be assured *before* choosing the means of building prevents the technology's convenience from bending the verification (a technology that cannot be verified becomes unchoosable).

## What each chapter is for

**Testing — the strategy for assuring the purpose's quality.**
Declare the kinds and methods: what is covered by automated tests, what by performance measurement, what by hands-on checks. Individual test cases and threshold numbers do not belong here — they descend into the Plan's done when and into the verification implemented before generation.

**Technology — the choice of means.**
Reuse or build; which method, which library. The body carries one conclusion line and a link per decision; rejected options and grounds are closed inside the Decision annex.

**Design — the shape of what is built.**
What changes, and what does not. Constraints — anything written here is carried through every implementation Step and becomes a verification viewpoint.

## Worked example

The scenario: adding CSV export of transaction history to an expense-tracking app. The `version` header line is the edition's identifier — written as `v1` by the drafting Turn(generate), and bumped (+1, fresh timestamp) by the rewriting Turn(generate) on each rework after a send-back.

```markdown
# approach — CSV export of transaction history

version: v1 (2026-08-16 14:22:48)

## Testing

- Correctness (counts and amounts) is assured by automated tests reconciling output against the aggregate API, weighted toward period boundaries
- Excel compatibility is assured by a mechanical check on the output plus per-OS hands-on open checks
- Performance is assured by measurement on production-scale data, with a scaled-down proxy threshold in CI
- The exclusion requirement (memo field) is assured by a full output scan plus structure (→ Design)

## Technology

- Encoding: UTF-8 with BOM — decision in decisions/csv-encoding.md
- Generation: streamed writes — decision in decisions/csv-generation.md
- Date format: ISO 8601 — too light for an annex; confirmed on real Excel that dates are recognized

## Design

- Changes: a new export API (GET /export, period parameters, streaming response);
  a period picker and download button on the history screen
- Unchanged: the transaction schema; the existing aggregate API
- Constraint: the memo field is excluded at the query level — never fetched, rather than filtered at output
```

Reading note: Testing declares only kinds and methods — the five boundary patterns and the 30-second number live in the Plan's done when and in the verification implementation. Technology is conclusions plus links; the grounds are closed by the annexes. A light decision like the date format needs no annex. The Design constraint (never fetched) satisfies the exclusion requirement by structure rather than by output scanning alone — exactly the kind of judgment worth writing down.
