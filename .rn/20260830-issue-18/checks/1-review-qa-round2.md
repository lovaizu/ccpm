# Task #1 — QA expert review, round 2

Against `evidence/1-jsonl-behaviour.md` at `9f5f413`. **Verdict: Fail** — 2 of 4 criteria NG, plus
three substantive claims that would change what task #2 decides.

## Per criterion

**1. Location and liveness recorded with command + output — NG.**
- `:443` heading "Three files prove the directory diverges from the `cwd` on **every entry**" is false
  and its check cannot falsify it: the command filters to entries carrying a `cwd`
  (`if 'cwd' in e`). Measured: 3 of 11, 3 of 13, 3 of 13 entries carry one. The document catches this
  exact overstatement at `:574-576` and then commits it in a heading.
- `:45` "The log is append-only, so re-running any count returns a larger number" is the premise every
  re-measured figure rests on, and no command tests prefix stability. It does hold as far as the
  reviewer could check (the five token-bearing lines byte-identical across a 3-hour gap; 325,267 →
  640,244 → 811,865 bytes) — but that is the reviewer's evidence, not the document's.

**2. An emission method lands and is greppable while open — OK.** Reproduced byte-identically 3 hours
later: same five token-bearing lines at the same JSON paths. "Arbitrary" is not established (only
16-char lowercase hex) and the document says so at `:813-814`.

**3. Hits attributable to the emission — OK conclusion, one decorative guard.** `:113-114` counts the
work order for token values, but that work order is conversation line 149 at 05:06:30Z — *after* every
hit (05:05:18–27Z). It could not have produced them whatever it contained. The confounder that could
have mattered — what instructed the coordinator to emit — is unchecked; the reviewer checked it: the
human prompt at line 122 is three characters, and the tokens are generated in-conversation at line 127.
Attribution is sound, on a fact the document does not record.

**4. Landed and not-landed separately recorded — NG.** The document had a measured negative in hand
and filed it as a naming fact: **a subagent's own turns do not reach the conversation file** (4
token-bearing lines in the subagent file, 0 of its intermediate assistant text blocks present in the
conversation file, while its final report is). "Emit the marker from inside a subagent turn" is a
candidate method, it demonstrably does not land, and it is the method an `rn` implementation is most
likely to reach for. It belongs in the table as a NO.

## Findings outside the criteria

- **F1 — a tighter latency bound sits inside the document's own quoted output.** `:230-233` says no
  tighter bound is recorded without fresh probes. But `:221` quotes `lines: 160`, and conversation line
  159 is an `assistant` text entry (an emission point) at 05:06:35.762Z — the same arithmetic gives
  **11.1 s**, and 16.0 s for the `Agent` tool_use at line 149. This matters: 79.7 s is what `:900-903`
  carries forward as the reason same-turn read-back is doubtful.
- **F2 — the compaction duplication is measured in the wrong direction.** `:726-728` needs
  P(reproduced in summary | appeared earlier); the document measured P(appeared earlier | in summary) =
  27/39. The reverse direction is **22/70 = 31.4%**, not 69%. Real hazard, stated ~3× too strong.
- **F3 — compaction is n=1** (1 of 62 files carries a compact summary), yet `:664` generalises.
- **F4 — "no file on this machine spans two versions" is false, and the counterexample answers a
  question the document hands forward as unanswerable.** The scan covered 62 ccpm files; machine-wide
  there are 94, and `…dotfiles--claude-worktrees-herdr4mac/1b4dd5b8…` spans `2.1.239` → `2.1.240`, one
  `sessionId`, no compact summary, version change after an 840 s gap. A running binary cannot change
  its own version, so a restart appends into the same file. `:912-913`'s second half is wrong.
- **F5 — a fourth conversation file appeared in the session's directory during the review, carrying
  zero timestamps.** `555280be-…jsonl`, 10 entries, no top-level `timestamp` at all; its
  `file-history-snapshot` entries replay `ef482a21`'s messageIds. Two consequences the document does
  not reach: a timestamp sort can drop an entire file (so `:875`'s "76 of 268" understates it), and the
  session's file set changes while the session is open — exactly the condition the goal works under.
- **F6 — relocation happens mid-file.** In `5466c142` the `relocated` entry is line 7 of 13, with
  entries before and after. A path resolved earlier in a session stops being the file. Not listed in
  "What this still cannot answer".
- **F7 — the 3-second boundary rule generalises from one observation of an entry type that cannot carry
  a marker.** The only 3.094 s backstep is a `pr-link` entry; every inversion involving a `user` or
  `assistant` entry is 1–25 ms. And it is a running maximum, not a bound (`ef482a21`: 2 inversions /
  0.001 s when measured, 3 / 0.060 s now). "Observed worst case" is honest; a threshold is not.
- **F8 — `:523` "All three stubs share the same three features"** — `10dcd188` and `5466c142` carry two
  `cost-state` entries each, `04319f87` none.

## What held up

The probe walk reproduces byte-identically 3 hours later. `isSidechain` all-False in the conversation
file now holds across 357 entries and eleven more subagents — stronger than when measured. The
375-second idle explanation at `:292-293` is correct. The `tr` mapping, the `/a/b.c` vs `/a/b-c`
collision, and "all 24 project directories match `^[A-Za-z0-9-]*$`" all reproduce. The token elision
worked: the document has been read back into the conversation and the file still carries exactly five
token-bearing lines.
