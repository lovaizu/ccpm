# Writing a Decision

An annex fixing one Approach decision on one page. **Zero or more per unit of work** — fold decisions into the Approach body while it stays a minutes-long read; split out once it bloats. Verification can put a viewpoint on each annex — one decision, one independent check.

## What each heading is for

**question — what is being decided.**
Phrased as a question with more than one possible answer. Something that raises no question is not a decision — it is a Design statement.

**decision — the option taken.**
The conclusion in one or two lines. This line is all that appears in the Approach body.

**rejected — the options discarded, and why.**
Every reason carries grounds — a number, a hands-on check, a source. Not writing "just because" is this heading's reason to exist.

**grounds — why the taken option holds.**
Measurements, spikes, sources. Investigation-Step products are cited by path — the grounds close inside the document, so "why this?" is answerable later from the annex alone.

## Worked example

The scenario: CSV export; the encoding decision.

```markdown
# decision — output encoding

## question
Which encoding opens in Excel as-is?

## decision
UTF-8 with BOM.

## rejected
- Shift_JIS — safe on old Excel, but 214 merchant names containing emoji (research/data-survey.md) hit unconvertible characters
- UTF-8 without BOM — Excel on Windows garbles it by default (confirmed on a real machine)

## grounds
- Confirmed on real machines that BOM'd UTF-8 opens ungarbled in Excel on both Windows and macOS
- The emoji row count comes from the tally in research/data-survey.md
```
