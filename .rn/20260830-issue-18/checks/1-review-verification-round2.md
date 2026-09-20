# Task #1 — Verification (dry-run) expert review, round 2

Against `evidence/1-jsonl-behaviour.md` at `9f5f413`. **Verdict: Fail.** 27 of 35 re-executed claims
came back byte-identical; the other 8 are clean append-only drift. It fails on two unreported facts and
one false generalisation, not on reproducibility.

## Per criterion

- **1. Location and liveness recorded with command + output — NG.** Two assertions have no command
  behind them and one is false as worded: F1 (version-scan scope) and F4 (the document's own text's
  field paths). F2 and F3 are observable in the trees the recorded commands already walk, but the
  prose does not report them.
- **2. An emission method lands, greppable while open — OK.** Four methods reproduce exactly at the
  claimed field paths (lines 138/139/142/144); the 05:06:46.849Z grep read them out of a conversation
  still open now.
- **3. Hits attributable to the emission — OK.** The field-path walk reproduces byte-identically; the
  work order (9697 chars) and the final report (2962 chars) each contain zero occurrences of all four
  tokens.
- **4. Landed and not-landed separately recorded — OK with qualification.** No untried method is
  claimed to work. Qualification is F2: a case where the Bash-output method demonstrably *fails*
  exists on disk and is not recorded as a limit.

## Findings

- **F1 — false as worded, load-bearing.** "No file on this machine spans two versions" — the script
  scans only the 64 ccpm files while the prose generalises to the machine. Machine-wide: **1 / 95**.
  `…dotfiles--claude-worktrees-herdr4mac/1b4dd5b8…` carries `2.1.239` (488 entries) then `2.1.240`
  (16), seam at line 662 / 2026-08-24T00:24:29Z after a 14-minute gap, same `sessionId`, no compaction,
  **`parentUuid` chain unbroken across it**. So a restart **appends to the existing file** under the
  same id with **no seam record** — only the version stamp changes. That answers part of a bullet the
  document files as unanswerable. (The `bridge-session` entry at line 661 is a cloud-bridge record,
  present in 24 files machine-wide — checked before concluding, not a resume marker.)
- **F1b.** A cross-file version timeline points at *left open*, not *resumed*, for `eded9b12`'s 90-hour
  gap: its post-gap entries are stamped `2.1.251` while the machine had been writing `2.1.252` since
  four days earlier. Circumstantial, but it is material the document says cannot distinguish the two.
- **F2 — unreported mechanism, materially important.** The conversation directory has a second child
  the document never mentions: `…/<conversation-uuid>/tool-results/`. **A Bash result above roughly
  43.5 KB is not written into the JSONL at all** — the entry carries `<persisted-output>` with a ~2 KB
  preview plus `toolUseResult.persistedOutputPath`, and the full text goes to
  `tool-results/<id>.txt`. This is a hard boundary on the "Bash command output" emission point and a
  sixth place a string can land. The document's own `find` would have shown it; `| grep adcd0d76`
  narrowed it out.
- **F3 — unreported escaping.** The subagent report inside `<result>` is **HTML-entity-escaped**:
  diffing the report against entry 164's payload gives similarity 0.9909, the edits being `<`/`>` →
  `&lt;`/`&gt;`. The fifth channel does **not** carry a marker verbatim if it contains angle brackets,
  and the untested-character list omits `<` and `>`.
- **F4 — asserted from reasoning and wrong.** The closing bullet says the document's own text now sits
  at `.message.content[0].content` and `.toolUseResult.file.content`. Observed:
  `.message.content[0].content` and **`.toolUseResult.stdout`** — it arrived via Bash stdout, not a
  Read result. The hazard is real; the second field path is not.
- **F5 — internal inconsistency.** The 88.2 s figure measures from line 134, which the document itself
  excludes as the incidental `cat`. From the first actual probe (05:05:24.735Z) it is **82.1 s**. The
  headline 79.7 s bound is unaffected.
- **F6 — overstated inference.** The compaction measurement runs one direction (27 of 39 summary-quoted
  strings appeared earlier); the body concludes the converse. Measured the actual direction on the same
  file: **35 of 156 (22.4%)**. The closing bullet's conditional phrasing is accurate; the body sentence
  is not.
- **F7 — minor unreported.** `worktreeSession.originalCwd` equals `relocatedCwd` in all three stubs —
  directly relevant to the relocation trigger the document leaves open. `<output-file>` in a
  task-notification is a symlink back to the subagent JSONL, not a copy. Drift surfaced two entry types
  absent from the document's lists (`cost-state`, `agent-name`).

## Drift, not mismatch

Every count on the still-open conversation grew monotonically and consistently (entries 268→370,
no-timestamp 76→100 at a stable ~27%, inversions 2→3, `leafUuid` 7→18, ccpm files 62→64). No type or
field disappeared. The dating discipline holds: earlier-round figures are labelled 05:05–05:07Z and
every re-measured block carries its own time.

## Not verified

Nothing was left unchecked for lack of access. Two items are unverifiable in principle from this
material and the document says so correctly — the relocation *trigger* (no relocated file carrying real
work exists on this machine) and same-turn read-back (needs fresh probes from the conversation itself,
which neither round emitted).
