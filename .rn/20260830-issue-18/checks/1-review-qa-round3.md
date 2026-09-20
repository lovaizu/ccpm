# Task #1 — QA expert review, round 3

Against `evidence/1-jsonl-behaviour.md` at `d77f9de`. **Verdict: Fail** — criteria 1, 3 and 4 NG.
Most of the document survives adversarial re-execution; it fails on the axis the objective cares about.

## Per criterion

- **1. Location and liveness recorded with command + output — NG.** A machine-wide negative rests on a
  ccpm-only command: `:462` / `:851-852` "no file on this machine carries real work *and* a `relocated`
  entry" is false — three dotfiles conversations do (`d9219a4d` 510 entries / 116 assistant,
  `4b34b25b` 135 / 33, `ee51f10a` 29 / 3). Also `:302-303` shows a `walk.py` invocation producing a
  line shape `walk.py:25` never prints; `:284` and `:531` are likewise paraphrases of the real command.
- **2. An emission method lands, greppable while open — OK.** Independently replicated with a fresh
  token: emitted 11:33:07Z, grepped back 11:33:10Z. Flush 0.102 s replicates; append-only replicates
  (prefix hash constant across 380,349 B → 707,534 B).
- **3. Hits attributable to the emission — NG.** The guard as presented could not fail: the tokens are
  `openssl rand -hex 8` generated in-conversation, so no prior text can contain them by construction.
  The confounder that actually materialised — `p1`/`p2` already present at line 134 from the
  coordinator's own `cat` — is named "incidental" (`:186`) rather than as the thing the guard defeats.
  Channel 5's attribution rests on a scan that silently dropped 8 of 10 handoffs (`scan.py:90` skips a
  handoff whose subagent file is missing).
- **4. Landed and not-landed separately recorded — NG.** Channel 5 is reported as landing a
  verbatim-modulo-entities payload; the document's own scan run against `ef482a21` falsifies that on
  4 of 8 handoffs.

## Findings

- **F1 — Channel 5 mutates a payload containing `<`, beyond anything `html.unescape` undoes.** When a
  subagent report matches an instruction-shaped pattern the harness prepends a ~244-char banner **and
  rewrites `<` to `<\`**. A task-boundary marker is by construction a control-token-shaped string, so a
  marker of the form `<rn:task-1-start>` lands mutated and a literal grep misses it. `:231`'s advice
  ("unescape before grepping") does not recover it.
- **F2 — Channel 5 delivers something other than the report when the subagent fails.** At lines
  305/311/317 the agent ended on a session limit and the `<result>` body carried an unrelated earlier
  fragment. A marker routed through channel 5 is silently absent on subagent failure — unrecorded in
  the channel table and in the open questions.
- **F3 — An answerable question is filed as unanswerable.** `d9219a4d` (510 entries, `cwd` =
  `…/worktrees/issue-9` throughout, 3.5 h) carries `relocated` at line 504 and **zero `/clear`**, which
  refutes `/clear` as a necessary trigger — the separation `:459-462` says the material cannot make.
- **F4 — A whole class of emission methods is unaddressed, including the only one a plugin controls
  deterministically.** All five measured channels are "the agent chooses to say or do something". The
  corpus holds three unexamined alternatives: **hook output** (`attachment` entries with
  `"type":"hook_system_message"`, `hookName`, `hookEvent`, `isSidechain:false`, timestamped, in the
  conversation file); **slash-command output** (`system`/`local_command` entries carrying
  `<local-command-stdout>` — 206 on this machine); and **Write/Edit tool calls** (the document's own
  self-reference section reproduces `.message.content[0].input.content` and
  `.toolUseResult.structuredPatch[N].lines[M]` without enumerating it as a channel).
- **F5 — The declared "sharpest open constraint" is called unsolvable without testing the channel that
  would solve it.** `:834-836` reports no discriminator between an emission and the text describing it.
  That negative is scoped to channels 1-4. A hook-emitted marker sits at `.attachment.content` in a
  `hook_system_message` entry carrying a `hookName` — a field path no document-quoting, work order or
  `git log` can reach.
- **F6 — The compaction figure answers an easier question than the marker's.** `:674` reports 35 of 194,
  but the population is frequency-confounded. Conditioned on prior occurrences: strings appearing
  exactly once before the summary reproduce at **2 of 46 (4%)**; those appearing 5+ times at 20 of 34
  (59%). A boundary marker is the once-per-boundary cohort — 4%, not 18%.
- **F7 — The version stated for the 2026-09-10 round is wrong.** `:8-13` claims `2.1.267`; the
  conversation that produced the measurements stamps `2.1.265` on all 152 version-bearing entries, and
  no ccpm file carries `2.1.267`. The document explains why at `:598` ("a running process cannot change
  the version string it stamps") and then contradicts it.
- **F8 — The >30 KB negative is a head-truncation, not a total loss.** `:382` says the channel "stops
  writing into the JSONL"; the retained `stdout` is the **head** in all three cases checked
  (15,250 / 20,346 / 15,401 chars; `head_match=True`, `tail_match=False`). The operative rule is "a
  marker in the first ~15-20 KB still lands". Also `corpus.py:58` filters on `stdout`, so the scan sees
  only Bash results — nothing is known about a large `Read` result.
- **F9 — "Replays every earlier entry verbatim" is false on both words.** Predecessor 370 entries,
  successor 296; bookkeeping types are dropped rather than replayed, and all 229 shared entries have
  `sessionKind` and `promptId` restamped. The `uuid`-dedup conclusion survives; a reader planning a pass
  keyed on bookkeeping entries is misled.
- **F10 — Summary-table rows overstate their sections.** `:22` attributes the 0.1 s flush to the
  conversation file (measured on a subagent file; the conversation-file figure is 11.1 s); `:23` calls
  the string "arbitrary" though only four hex tokens were emitted and channel 5 was never probed; `:25`
  claims same-turn read-back where the probe was a subagent reading its own file; `:32` quotes the
  superseded 76-of-268 beside current figures.
- **F11 — Internal contradictions.** `:56-57` ("never by a subagent") vs the same-turn probe at `:284`,
  whose emitting entry is `isSidechain=True`. `:231` ("no other channel was shown to transform its
  payload") vs `:194`, which records channel 4 injecting a `1\t` line-number prefix.
- **F12 — Unit mixing.** `:379` reports the threshold "between 29,067 and 30,044 characters"; the lower
  figure is characters, the upper is bytes.

## What held up

`walk.py` on `$CONV` reproduces lines 134/138/139/142/144 byte-for-byte with identical field paths.
Flush delay independently replicated at 0.103 s. Append-only replicated on the reviewer's own file.
Every `scan.py` and `corpus.py` row reproduced, including the 13,429.9 s backstep, the three divergent
stubs, 2/137 multi-version files, the continuation's 229 shared uuids with byte-identical `.message`,
both seams with unbroken `parentUuid`, and the nine self-reference field paths. The attribution facts as
facts: the Agent work order at line 149 contains zero token occurrences, and the four preceding human
prompts are 76/12/1/3 characters.
