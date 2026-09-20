# Task #1 — Verification (dry-run) expert review, round 3

Against `evidence/1-jsonl-behaviour.md` at `d77f9de`. **Verdict: Fail.** 36 of 38 command blocks
reproduce byte-identically or with upward-only drift; the scripts do what their docstrings say. It fails
on **coverage**, systematically in one direction: three scans are pointed at a narrower corpus than the
prose generalises to, and widening the *same command* to the named population produces a counterexample
each time.

## Per criterion

- **1. Location and liveness recorded with command + output — NG (partial).** Liveness reproduces
  (flush re-run 0.101 s; on the reviewer's own file 0.052 s with its own entry absent; append-only
  prefix hash constant across 554,921 B → 1,466,701 B). Several location facts carry no command —
  the three-stub type tally (`:445-451`), the `relocated` line positions (`:453-456`), `f96e5843`'s gap
  and parent uuid (`:595-596`), the persisted-output notice text (`:351`). All were verified true, but
  one asserted fact is false (finding 4).
- **2. An emission method lands, greppable while open — OK.** Re-derived rather than re-read: a fresh
  token emitted to Bash stdout at 11:40:30.019Z, grepped back 4 s later in the next call of the same
  turn, at `.message.content[0].content` and `.toolUseResult.stdout` of a `user` entry.
- **3. Hits attributable to the emission — OK.** `walk.py` reproduces byte-for-byte; the earliest hit is
  line 134 at 05:05:18.632Z and line 127 (`openssl rand -hex 8`) at 05:05:18.258Z is confirmed as the
  token's origin; the four preceding human prompts reproduce at 76/12/1/3 chars, 85.6 s gap.
- **4. Landed and not-landed separately recorded — NG.** Channel 5 is reported as working with a
  payload transformation limited to HTML entities; it is not (finding 1). The ~30 KB non-landing is
  stated for tool results generally when it holds only for Bash stdout (finding 2).

## Findings

- **F1 — Channel 5 mutates the payload beyond HTML escaping, and the document's own tool shows it when
  pointed at the whole corpus.** `scan.py escaping` was run on `555280be` only (n=2). Over
  `$PROJ_WT/*.jsonl` it returns 11 handoffs with `unescape(result)==report` **False on 4**. At
  `ef482a21` line 272 the `<result>` body is the report with a harness notice prepended and `<`
  rewritten to `<\`; 97 such prefixes exist machine-wide. This kills any angle-bracketed marker on
  channel 5 and falsifies `:231`. The other three mismatches are a separate defect: `scan.py:91` takes
  `load(sub)[-1]` as the report, which for an agent that died on a session limit is not the report.
- **F2 — The ~30 KB persistence threshold is a Bash-stdout property asserted as a tool-result
  property.** `corpus.py:58` filters `'stdout' not in r: continue`. Scanning the same corpus for
  non-stdout results: **280 `toolUseResult` objects exceed 30,000 characters and are kept inline**,
  including `Read` results at 52,393 chars and WebFetch at 99,151. Channel 4 carries far more than
  30 KB into the JSONL. `:379` also converts units silently (lower figure characters, upper bytes).
- **F3 — "no file on this machine carries real work *and* a `relocated` entry" is false.** The
  document's own `corpus.py entry-types` prints `relocated 14` on the page at `:738` — 14 = 7 files × 2,
  while the document knows only 3. The other four are under `-Users-kiyo-work-lovaizu-dotfiles`; three
  carry substantial work (`d9219a4d`: 510 entries, 116 assistant, 322 entries whose `cwd` is
  `…/worktrees/issue-9`). The misfiling consequence is far larger than the 3-entry stubs suggest
  (322/510 vs 3/11). None of the three contains a `/clear`, and both `relocated` entries sit at the very
  end — which separates "leaving a worktree" from "`/clear`" in exactly the way `:459-462` says the
  material cannot.
- **F4 — "Only one of those 254 hits is structural" is false, and it hides a backward pointer the
  document says does not exist.** Walking every string field of `555280be` for the predecessor's id:
  **183 of 254 hits sit at `.session_id`**, plus 11 at `.toolUseResult.outputFile`. Every replayed entry
  carries a snake_case `session_id` naming the predecessor alongside the restamped camelCase `sessionId`.
  So `:549` ("a forward pointer only; the successor carries no field naming the predecessor") is wrong.
  For the marker decision this is the cleanest per-entry discriminator between a replayed copy and a
  fresh one — better than the `uuid`-set dedup recommended at `:552-554`.
- **F5 — "replays every earlier entry verbatim" and "every entry carries `sessionKind: bg`" are both
  false.** Predecessor 370 entries / 229 uuids; successor 296 / 256. The replay copies the 229
  uuid-carrying entries and **drops 136 of the 141 uuid-less ones**. `sessionKind` on the successor is
  `{'bg': 256, None: 40}`. `:535`'s "27 further entries" counts new uuids; 67 entries actually follow.
  Marker consequence: channel 5's `queue-operation` copy has no `uuid` and **does not survive a
  continuation**.
- **F6 — The channel-5 wrapper description matches neither entry it cites.** The stated tag sequence
  includes `tool-use-id`; lines 242 and 278 do not have it. That tag exists on the *other* eight
  task-notifications in the same file, which the scan never reaches — two shapes, one reported, and the
  reported one is the shape the cited entries lack. Separately, `:208`'s "preceded by a
  `queue-operation` entry carrying the same text": for line 242 the paired enqueue is at **line 11**,
  231 lines earlier — the same −13,429.9 s inversion reported at `:697`, and the connection is never
  made. In a continued session a channel-5 marker's enqueue copy lands at the *top* of the file.
- **F7 — A subagent report can be enqueued and then removed, never becoming a `user` entry.**
  `queue-operation` line 249 `enqueue` / line 254 `remove`; that task-id appears in no `user` entry, and
  its 11,416-char report exists on disk only inside the two `queue-operation` entries. Channel 5's
  `user`-entry landing is not guaranteed, which the "Lands: yes" row does not qualify.
- **F8 — `:302-304` is hand-assembled and presented as recorded output.** `walk.py` never prints a
  `tool_result` label or that string. The underlying fact is true — entry 16's stdout does contain
  `lines:\n     160` at 05:06:46.849Z, so the 11.1 s figure survives — but the block is not output.
- **F9 — `:527` vs `:531`: a second output the command cannot produce.** The code prints `sessionId on
  the replayed entries:`; the pasted output reads `sessionId stamped on the replayed entries:`. Values
  reproduce; the label was edited.
- **F10 — `:32` quotes a superseded figure** (76 of 268) beside current ones, unmarked as frozen.
- **F11 — `:355` "the first such entry on this machine" is an ordering claim `glob.glob` does not
  make.** It happens to reproduce; it decides which numbers get quoted.
- **F12 — `:614`'s "still running" annotation is now on the wrong version.** `2.1.263`'s last is
  unchanged; `2.1.265` advanced.

## Unreported facts observable in the trees already walked

- **No conversation file on this machine carries an `isSidechain: true` entry** (0 of 137). The negative
  at `:328-338` rests on 2 files; the corpus supports it far more strongly than claimed.
- **Non-ASCII is stored raw, not `\u`-escaped** — `agent-name` entries hold literal UTF-8 Japanese
  (10 of 40 sampled files). The open item at `:838` is partly closable from disk: a byte-wise grep for a
  non-ASCII marker works.

## Drift, not mismatch

Upward-only growth throughout: `c763d0be` 167 → 213 entries, its no-`isSidechain` count 48 → 61,
`entry-types` totals up with the type count still 19 and `continued-in` still 1, self-reference matrix
`c763d0be: ef482a21` 0 → 8 (caused by this review reading the document — the hazard the section
describes). Every frozen `ef482a21` / `555280be` figure reproduced byte-identically.

**Block tally: 38 blocks. 36 reproduced exactly or with upward-only drift. 2 mismatched (F8, F9). 1
further block (`:265-266`) presents a paraphrase inside a `$` fence.**

## Not verified

- The 2026-09-06 frozen readings at `:112` and `:140-141` — that conversation is closed and those states
  are gone. Limit of the material; correctly labelled.
- `:511` "`555280be` was in that state too" — a past observation with no command and no surviving
  artefact, presented as fact in a section otherwise built on commands.
- Whether the `<` → `<\` mutation fires deterministically on a given marker shape. The mutation and its
  trigger name were confirmed; the pattern's boundary was not probed. That is task #2's measurement, and
  the document should record that it exists.
