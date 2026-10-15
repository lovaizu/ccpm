# Writing the Plan

Each phase's execution plan. **One per phase — but a living document, re-planned while running.** One shared format across the three phases, and the single thing the human reviews at a Planning Gate. The whole point: **whether items may be bundled and run at the same time is decided mechanically, from the consumes lines — plus one guard: two items that write the same file are never bundled.**

## What each line is for

Each item is three lines, plus one optional.

**product — what exists once this item is done.**
One item, one product. Wanting to write two is the signal to split the item. When the product is a file, the product line names its path.

**consumes — the earlier products actually used as input.**
Mere ordering is not written. Approved phase documents (purpose / approach) are everyone's premise and are not counted. **Items whose consumes are empty may run at the same time.** One exception — two items writing the same file are dependent, whatever their consumes say, and must not be bundled.

**done when — this item's own pass condition.**
Written to be runnable. Do not restate the phase-wide success criteria here — that is the final verification's job (G3); this line is the smallest condition under which this item counts as done.

**viewpoints (optional) — domain concerns beyond done when and the yardstick.**
Each one listed gets its own independent verification. Use it for performance, thread safety, and the like; for a document item, "every cited source resolves" belongs here.

## Worked example (Delivery)

The scenario: adding CSV export of transaction history to an expense-tracking app.

```markdown
# plan — Delivery

## #1 export query and streaming base
- product: a query layer streaming transactions for a chosen period (memo field never fetched) + performance test
- consumes: —
- done when: 120,000 dummy rows fetched end-to-end within 30 seconds; memo field absent from query results
- viewpoints: memory ceiling under 3 concurrent runs (must not reproduce the approach's measured blow-up)

## #2 CSV serialization and encoding
- product: a serializer mapping one transaction to one CSV row (UTF-8 with BOM, ISO 8601 dates) + tests
- consumes: —
- done when: BOM check and date-format tests green; all 214 emoji merchant names output without loss

## #3 download UI on the history screen
- product: period picker and download button (built against the API shape fixed in the approach's Design)
- consumes: —
- done when: the screen issues a period-parameterized call (a mocked response is fine)

## #4 export API
- product: GET /export (period parameters, streaming response)
- consumes: #1's query layer, #2's serializer
- done when: all 5 count-and-amount reconciliation patterns green

## #5 integration and full-criteria verification
- product: the verification record for success criteria 1–4 at .aiya/csv-export/research/full-criteria-verification.md
- consumes: #3's UI, #4's API
- done when: all 4 criteria pass, evidence on the PR
```

From these consumes lines the bundling derives mechanically: **Wave 1 = #1 ∥ #2 ∥ #3** (all with empty consumes), **Wave 2 = #4**, **Wave 3 = #5**. #3 belongs in Wave 1 because the API's *shape* is already fixed by the approved approach — what creates a dependency is consuming #4's *implementation* (which #5 does), not referencing an approved shape.

## The Plan is a living document

The Plan is not written once. Every time a wave settles, the Conductor re-plans **from zero** out of the current position and the discoveries — a fresh plan that matches the current one means "proceed"; where it differs, the difference is the revision. Revisions append to a change log at the end: what changed, the discovery that grounded it, and the waves already fired. At the next checkpoint, you read the diff and the reasons.

```markdown
## change log
- v2: added #6 emoji normalization; added #6 to #5's consumes
  grounds: #2's Report (unsure: combining-character rendering in Excel unconfirmed). Wave 1 already fired
```
