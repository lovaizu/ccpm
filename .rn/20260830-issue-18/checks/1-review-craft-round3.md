# Task #1 — Craft (writing) expert review, round 3

Against `evidence/1-jsonl-behaviour.md` at `d77f9de`. **Verdict: Fail.** Scope checked: all 871 lines,
all four scripts, `.claude/rules/output.md`, `.claude/rules/language.md`, and `rn/docs/design.md` for
register. All 21 internal anchors resolve; every arithmetic figure re-derives; every quoted `scan.py` /
`corpus.py` output matches its script's format string except one. No measurement was re-run against the
live logs.

## Per criterion

- **1. Location and liveness recorded with command + output — NG (location half).** Liveness is clean.
  Six load-bearing location claims carry no output and three carry no command: `:402-405` (the naming
  rule, `ls -d` named but not shown), `:409-410` (all 32 project directories match a character class),
  `:445-452` (a nine-item entry-type tally plus the `originalCwd`/`relocatedCwd` identity), `:453-456`
  (the `relocated` line positions), `:548` ("1 of the 137 conversation files" above a grep that runs
  over five), `:594-601` (`f96e5843`'s properties, from a `scan.py seam` run only on `1b4dd5b8`). The
  preamble at `:5-6` promises every claim carries its command and that anything unmeasured is labelled
  an inference; none of these is so labelled.
- **2. An emission method lands, greppable while open — NG for the conversation file.** The same-turn
  demonstration greps a subagent file. The only evidence for a *conversation-file* emission is the
  11.1 s figure, whose transcript at `:301-304` is not `walk.py` output: `walk.py:25,47` emit two line
  shapes, and the quoted line matches neither, using double quotes where the script uses `repr()`.
- **3. Hits attributable to the emission — OK, with a live contradiction.** The timing argument at
  `:251-276` carries the criterion. But the first of the "three facts" (`:246-249`) argues from field
  paths — an echo would sit in a prompt field, not at `.input.command` of an `assistant` entry — while
  `:825-831` demonstrates the opposite and concludes "neither a field-path nor an entry-type
  discriminator separates the two". Two passages 580 lines apart that cannot both be true.
- **4. Landed and not-landed separately recorded — NG.** Nothing is over-reported as working, but a
  not-landed method is reported wrongly in the two places a reader reads first: `:340` and summary row 3
  at `:24` say a >30 KB tool result is "not written into the JSONL at all", while `:367` shows
  `stdout kept in the entry 15250 chars` — ~37% stays inline. Only the table row at `:197` is accurate.

## Findings, most serious first

1. **`:340` / `:24` state a falsehood their own evidence refutes.** Rewrite as truncation, not loss, and
   add the missing measurement as an open question: **whether the retained preview is the head or the
   tail decides whether a marker at a boundary survives.**
2. **`:301-304` is not the output of the tool it names.** Re-run `walk.py` and paste what it prints, or
   relabel the block as a quotation of the 2026-09-06 subagent's own tool result with the command that
   produced it. The strongest conversation-file liveness figure currently rests on an unreproducible
   fence.
3. **`:246-249` and `:825-831` contradict each other on field-path attribution.** Drop field paths from
   what *establishes* attribution; say they confirm each hit reached its channel's predicted path, and
   let attribution rest on the two timing facts.
4. **`:98` contradicts `:138-139`** — "complete on disk up to the moment it is read" vs "the entry
   describing an in-flight tool call is not on disk while that call runs". Summary row `:22` needs the
   same repair.
5. **Systemic unbacked assertion in the Placement and Restart sections** (the criterion-1 list above).
   Move the stub tally and `relocated` positions into a `scan.py` subcommand; widen the `continued-in`
   grep at `:544` to the machine so the shown command matches the 137-file claim; run `scan.py seam` on
   `f96e5843` too, or delete the sentence claiming its properties.
6. **`:26` contradicts itself in one sentence** — "nothing is known about `<` and `>`, which one channel
   escapes" — and drops `&`, which `:225-231` and `:838-839` both include.
7. **`:23` calls the string "arbitrary" 200 lines before proving it is not.**
8. **`:32` quotes a superseded figure** (76 of one file's entries) without the label `:15` promises;
   the body's current figure is 100 of 370.
9. **The document declares a single-word discipline and breaks it.** `:51-52` says *channel* is the only
   word used for the concept; "method" is used for it at `:3`, `:24`, `:196-197`, `:200`, `:311`,
   `:313`, `:849`.
10. **`:55` states a definition `:336` corrects without withdrawing** — coordinator entries are
    "`isSidechain: false`", but 48 of 167 carry no such field. Use "never `isSidechain: true`".
11. **"round" is load-bearing, undefined, and inconsistently counted** — two at `:28`, three at `:803`,
    a fourth name at `:509`.
12. **`:8-13` overstates which version produced the figures** — the binary on PATH is not the version
    the writing process stamps, as `:598` itself explains.
13. **`:231` invites a false inference** — with a `[0-9a-f]`-only token no channel *could* have shown a
    transformation, and table row 4 already records channel 4 inserting a `1\t` prefix.
14. **Fence bloat: 335 of 872 lines (38.4%) inside fences; 12 blocks exceed the 10-line cap in
    `output.md`.** `:81` declares the right fix (shared scripts) and then abandons it — **11 blocks
    totalling 139 lines are inline Python that belongs in the existing scripts**. Named: `:639-675`
    (29 lines → `scan.py compaction`), `:354-368` (15 → `corpus.py persist-example`), `:118-132`
    (15 → `scan.py flush`), `:519-532` (14 → `scan.py replay`), `:490-499` (10 → extend `scan.py cwd`),
    `:770-779` (10 → one sentence), `:690-707` (18 → two extremes plus a per-type count), `:789-801`
    (13 → keep the two non-zero rows).
15. **`:150-158` and `:318-321` print the same two measurements for two different claims**, 165 lines
    apart. Cite by `path:line` instead.
16. **"Here is a number; now ignore it" appears three times** — `:291`+`:296-297`, `:308-309`,
    `:677-679`. Delete the second outright; move the bold at `:291` onto the actual finding.
17. **`:144-145` and `:296-297` describe a loose bound as corroboration.** An 11.1 s upper bound is
    compatible with a 0.1 s flush and with a 10 s one; it agrees with nothing.
18. **`:619-622` and `:844-846` argue the same point twice, the second version longer**; same pattern at
    `:604` vs `:840-843`.
19. **Defensive justification / draft archaeology, twice** (`:138-141`, `:275-276`), against
    `output.md`'s ban on litigating a correction. The 05:08:20 reading is real evidence and should stay
    — without the earlier-draft frame. Related editorialising at `:199-202` and `:823`.
20. **Four headings do not carry their fact** — `:311` ("Two candidate methods do not land" — which?),
    `:385` (states the input, not the consequence), `:784` (a methodological boast where the finding
    belongs), and `:398` ("Part 2 — What a later reader can rely on" mislabels a part whose contents are
    largely what a reader specifically *cannot* rely on).
21. **One question split across distant sections** — "which files must I search?" is answered at `:400`,
    `:469`, `:514`, `:570`, `:747`, with `continued-in` introduced at `:543-549` and re-enumerated at
    `:749-750`. Same for "what may my marker contain?" across `:221-231`, `:385-396`, `:624-683`,
    `:836-839`.
22. **Hand-formatted fences presented as raw output** — `:344-348` (`ls` on two directories rendered as
    side-by-side columns; `ls` prints them sequentially), `:236-239` (`ls -la` with no `total` line and
    elided paths), `:614` (an annotation inside a fence of program output), `:736-739` (one joined line
    wrapped across four), `:284` (a `cat` shown with no output where the convention is to mask),
    `:119-121` (the literal was replaced before pasting, explained only afterwards at `:134`).
23. **Sentence-level** — `:805-806` ("those 254" reaches past the preceding sentence to a cell in the
    table above, and the claim is itself unbacked); `:861-864` (a "Frozen records." fragment with no
    predicate); `:865-867` ("every block above" overstates); `:450-452` ("the recorded origin" has no
    antecedent); `:781-782` (a document-wide policy dropped into a paragraph about `leafUuid`);
    `:869-871` (welds two different propositions); `:70` (a comment blurring which agent writes the
    document — the distinction is what makes the `$LIVE` grep return 0); `:858-859` (mis-cased part
    title); `:375-379` (two units merged into one); `:24`/`:197`/`:340` (disagree on tool vs Bash
    scope); `:42` vs `:28`/`:469`/`:484` (*session* defined as the `rn` session, then used for the
    Claude Code one — the exact confusion the Terms section exists to prevent).

## What held up

The evidential spine — the four-token / five-channel table with per-field-path attribution, the timing
argument, the escaping measurement, the append-only test, and the two negatives — is what task #2 needs,
and the negatives are what stop the positive result from being vacuous. Every quoted `scan.py` /
`corpus.py` output matches its script's format string except `:301-304`. Every arithmetic figure
reconciles. All 21 anchors resolve. The masking discipline is rigorous and correctly motivated by the
hazard it later measures. Register matches `design.md`; English throughout. Negative results and open
questions are separated and honest.
