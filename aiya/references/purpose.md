# Writing the Purpose

The document that fixes *why we are doing this* and *how we will know we got there*. **One per unit of work.** You approve it at G1, and it becomes the yardstick for every verification afterward. Four chapters, reading in order as fact → pain → value → judgment.

## What each chapter is for

**Situation — align the reader on the facts.**
Facts only, with numbers and sources. No interpretation, no wishes. Later chapters may ground themselves only in facts written here — if a new fact appears downstream, move it back here. Most numbers come from the Purpose phase's investigation Steps.

**Pain — prove why now.**
Who hurts, when, on what, and how much. And the cost of leaving it alone. Rooted in the Situation's facts.

**Benefit — state the value as the Pain inverted.**
One-to-one against the Pains. A Benefit with no matching Pain is a scope-creep signal — cut it, or add the Pain that grounds it.

**Success Criteria — fix the yardstick for verification.**
Written to be runnable: these sentences are executed as-is at the final verification (G3). Every criterion traces to a Benefit or to an explicitly stated prohibition. Phrasings no mechanical check could ever decide — "easy to use", "clean" — are not yet finished being written.

## Worked example

The scenario: adding CSV export of transaction history to an expense-tracking app. The `version` header line is the edition's identifier — written as `v1` by the drafting Turn(generate), and bumped (+1, fresh timestamp) by the rewriting Turn(generate) on each rework after a send-back.

```markdown
# purpose — CSV export of transaction history

version: v1 (2026-08-15 09:41:07)

## Situation

- The app stores up to 120,000 transactions across 3 years (as of 2026-08, largest user; investigation #2)
- Transactions are viewable only inside the app; there is no way to take the data out
- "I want to export my data" requests: 47 in the last 12 months, 41 of them in tax season (investigation #1)
- Merchant names containing emoji exist in real data: 214 rows (investigation #2)

## Pain

- Users hand-copy transactions every filing season — hours per year, with copy errors
- Accountants want Excel files but there is no way to hand one over; they receive screenshots
- "Can't get my data out" appears in recorded reasons for considering cancellation — left alone, it repeats every season

## Benefit

- Users export a chosen period in one click (hand-copying disappears)
- Accountants open the received file in Excel as-is (the exchange takes one round trip)
- Cancellation consideration citing "can't get my data out" disappears

## Success Criteria

1. For any chosen period, the exported CSV's row count and amount totals match the in-app aggregate for the same period
2. Opened in Excel (Windows / macOS), Japanese field names and merchant names — emoji included — are not garbled
3. Exporting 120,000 rows completes within 30 seconds
4. The private memo field is absent from the output — a full row-and-column scan finds 0 occurrences
```

Reading note: criteria 1–3 each trace to one of the three Benefits. Criterion 4 comes not from a Benefit but from a prohibition stated in the interview ("the memo field must never be exported") — prohibitions, too, are converted into runnable criteria like this.
