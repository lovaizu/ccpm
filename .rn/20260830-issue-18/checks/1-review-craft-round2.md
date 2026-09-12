# Task #1 — Craft (writing) expert review, round 2

Against `evidence/1-jsonl-behaviour.md` at `9f5f413`. **Verdict: Fail** — on craft, not on evidence.
The reviewer reconciled every count it checked (268 = 168 + 100, 268 = 192 + 76, 62 = 58 + 4,
62 = 16 + 46; the 79.7 s / 88.2 s / 6.6 s / 99 ms intervals all recompute from the printed timestamps).

## Completion criteria

All four OK. Three supporting claims inside the location/liveness sections carry no command, against
the document's own promise at `:11`: `:440` (all 24 project directories match `^[A-Za-z0-9-]*$`),
`:517-519` (the stub inventory naming entries the block at `:474-490` never prints), `:265-266` (the
entry's first content block is `thinking`).

Criterion 3 is OK but weakened: the zero-count guard at `:118-136` counted the work order passed to
the *subagent*, while the four hits are `isSidechain: false` — coordinator emissions, whose own
instruction was never searched.

## Findings, most to least serious

1. **No conclusion.** Opens on a version stamp and a naming section; first substantive claim at `:48`;
   closes on open questions. Insert a ~10-line "What this establishes" block after `:8`, one line per
   finding with a section link.
2. **~250 of 913 lines are cuttable.** 56% of the file is inside fences. Named: `:731-794` (the whole
   multi-day-gap section → 5 lines), `:329-368` (40-line pretty-printed entry → 6 lines; its payload is
   already at `:374-377`), `:471-515` (45 lines → the `assistant entries` and `relocated` columns),
   `:429-441` (the `/a/b.c` collision demo — measures nothing about Claude Code), `:418-427` (the `tr`
   reproduction — repeats `:405`), `:800-809` (9 lines to say four tokens are 16 hex chars),
   `:543-551` (superseded by `:563-571`), `:227` (a looser bound beside the tight one), `:685` (17-key
   dump; only `isCompactSummary` is used).
3. **Which agent emitted the probes is never stated**, and "probing subagent" (`:114`) vs "probing
   turn" (`:97`) name different actors with the same adjective. Load-bearing: `:233` argues a
   subagent's probes land in a subagent file, which makes the probes coordinator-emitted — so `:114`'s
   label is wrong and the guard at `:118-136` checked the wrong instruction.
4. **The naming section defines the terms that hold and omits the ones that drift.** `:24` defines
   probe/token, then `:50`, `:198`, `:811` "emit a probe" (an act cannot be emitted). `marker`,
   `entry`, `emission point`, `emission channel` are undefined; point vs channel is never reconciled
   (`:48` says four points, `:296` a fifth channel).
5. **Three sections open by litigating an earlier draft** (`:237`, `:665`, `:733`). `output.md:33`
   forbids it. Lead each with the measured fact instead.
6. **The h2 at `:195` states a latency the section spends four lines retracting.** Rewrite as
   "greppable 80 s later; the true delay is unmeasured". Also spells "eighty" where the document uses
   numerals throughout.
7. **The self-reference hazard is made three times** (`:39-41`, `:635-661`, `:890-897`). Keep the
   open-question bullet as its single home.
8. **`:243-260` is a reconstruction presented as a transcript** — no `$` line, hand-added ` 1| `
   gutters, a prose annotation inside the fence. Show the extractor command; move the note above the
   fence.
9. **Ten inline heredocs of 14–21 lines, three of them duplicates** (`walk` at `:65-72` and `:310-317`;
   the `toks`/`mask` preamble at `:56-60`, `:119-120`, `:204-208`, `:383-385`). `output.md:51` caps a
   code example at 10 lines. Move to `evidence/tools/walk.py` and `masktok.py`; ~90 lines go.
10. **Six sentences force a re-read** — `:110` (ungrammatical subjunctive), `:101` ("negative column"
    the table does not have), `:274` (unresolvable "the criterion"), `:613-614` (`entry` used for the
    act of entering a worktree), `:399-400` (bold falls on the empty half of the opposition), `:863`
    ("larger" ranks two different kinds of problem).
11. **`:379-380` contradicts `:811`** — calls the report's not quoting a token "an accident of wording"
    when `:37-39` establishes the elision was a deliberate rule.
12. **`:576` asserts a join the block never shows** — `cwd` 128 and `gitBranch {main: 94, wt: 34}` are
    independent tallies; 94 + 34 = 128 makes the identification plausible, not measured.
13. **`:632` says seven `leafUuid` values where `:876` tallies fourteen `last-prompt` entries.** Growth
    between 05:07Z and 05:30Z probably explains it, but no command lets the reader check.
14. **The primary attribution evidence is not reproducible and the document does not say so.** Every
    probe block depends on `$PROBE`, a per-conversation scratchpad directory that will not outlive the
    conversation. `:274` advertises re-runnability for a different block, which makes the silence read
    as coverage.
15. **The order splits the reader's two questions.** "What to emit" is answered at `:48` and again 750
    lines later at `:796`; "how to find it" at `:403`, `:537`, `:663`, `:824`, interleaved. Reorganise
    into *What lands* then *What a later reader can rely on*. The liveness fact — one of the two the
    criteria name — sits at h3 (`:272`) behind a retraction; it belongs at h2.
16. **Voice breaks into clipped fragments `design.md` never uses** — "That is not tidiness." (`:39`),
    "The log refutes it." (`:238`), "They are stubs." (`:520`).

Minor: the shorthand block at `:29-35` reads as output rather than assignments to paste; the walk at
`:68` truncates strings to 110 chars without declaring it, against the promise at `:12`.
