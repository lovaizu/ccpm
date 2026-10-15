# Writing a Report

The first-person record a Turn(generate) leaves beside its product. **One per Turn(generate)** — a re-aimed item accumulates several. Name files so the item number and attempt are readable (e.g. `s02-a1.md`). Only Turn(brief) reads it — no human, no Conductor. So politeness is unnecessary; **only honesty is required**. An unwritten "unsure" never reaches the CCS, and the next Step falls into the same hole.

## What each heading is for

**did — what was done.**
Include product paths. An inventory of actions — neither a boast nor a defense.

**tried — what was attempted and abandoned, and why.**
The prime information that no product retains. It saves the next person from trying the same option and abandoning it for the same reason.

**unsure — what was left uncertain.**
The most important heading. Only what is written here lands in the CCS's uncertainty signal and can become a resolution Step. Unwritten, the uncertainty never existed.

Keep the whole thing bounded — about 20 lines. If it wants to be longer, product content is leaking into the Report.

## Worked example

The scenario: CSV export, item #2 (CSV serialization and encoding).

```markdown
## did
- Implemented the CSV serializer — src/export/serializer.ts
- UTF-8 with BOM output, ISO 8601 dates
- Added tests — tests/export/serializer_test.ts (BOM check, date format, all 214 emoji names lossless)

## tried
- The standard library's CSV writer — its quote-escaping disagrees with Excel; abandoned
- Emitting dates as Excel serial values — unreadable to humans; abandoned (a judgment within the approach's Design)

## unsure
- How Excel's column-width logic treats combining-character emoji (👨‍👩‍👧 etc.) — unconfirmed; possible rendering breakage
- Whether merchant names containing newlines exist in real data — unsurveyed; if they do, quote handling needs another test
```

Reading note: the two unsure lines are copied into the CCS by Turn(brief) and become the Conductor's re-planning input — the combining-character line is exactly what can turn into an added item "#6 emoji normalization." A Report is not a chore; it is the input that makes the Plan smarter.
