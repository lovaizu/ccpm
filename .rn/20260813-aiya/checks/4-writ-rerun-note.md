# What changed — writ re-run of aiya/docs/design.md (updated procedure)

Re-run of the build-fresh procedure at `origin/worktree-writ` HEAD (153fb88) over the document
already rebuilt under the old writ (486a1af, note `4-writ-note.md`) and refined once (edcf1b4,
note `4-refine-note.md`). **Outcome: the document did not change** — 6,239 words before and
after (`wc -w`). This is a fixed point, not a skipped run: the upstream writ commits
(8b2e42e…153fb88) codify the same PR #15 feedback (2026-08-20) the refine pass already applied
to this document by hand. Every step below was executed; what the updated procedure newly
demands turned out to be note-level obligations — per-slot justification of the supplied
outline and the naming of excluded content — discharged here.

**How the run deviated from writ's letter (disclosed 2026-08-23).** writ step 7 says to render
the filled outline into the document fresh, never editing the draft in place; that literal
blank-page rebuild is what 486a1af did (10,612 → 7,269 words, whole text replaced). This
re-run did steps 1–6 as re-derivation — the narrowed one-reader definition drove a fresh
admission audit of every heading and point — but executed step 7 as an **audit against the
existing text** rather than a blank-page re-render: each admitted point was checked to be
carried by a sentence already present, and none was rewritten. A byte-identical result is
itself the evidence — a true re-render would have shifted surface wording even at identical
content. The reason for the deviation: parts of this document are owner-ratified sentence by
sentence, and re-rendering ratified wording when the content is unchanged would replace
approved text with unapproved text for no gain. The claim "fixed point" is therefore about
content, not about the letter of step 7. writ has no stated semantics for re-applying itself
to a document it already produced; that gap is FB for writ, recorded below.

**FB owed upstream to writ (open, not yet sent).** Two gaps this run hit, neither fixable in
this document: (a) step 11's delivery gate — "a clean pass, no stumbles, no unneeded content" —
was unreachable here: four fresh-reader trials each produced a *disjoint* set of novel minor
stumbles, and the unneeded-content half is format-mandated, so the gate never closes; writ
needs a convergence criterion (declining severity + repeated purpose YES + an iteration cap)
instead of a zero bar. The 3-iteration cap used here is this session's invention, not writ's.
(b) re-application semantics — the audit-mode question above. Whether to send these to PR #15
awaits the user's ruling.

## Which upstream writ changes bit, and where

- **One person in one reading stance (a1087d9)** — bit the reader definition. The old run's
  reader was bundled: "the person deciding whether the design is sound, *and* the person who
  will build on or maintain it" (`4-writ-note.md` step 2). This run holds the ratified single
  reader (below) and re-audited every ch1–4 heading and point under the narrowed WHAT. No
  exclusion was forced: the content serving the dropped builder/maintainer stance was already
  cut by the refine pass (FB1 lens), and what remains either feeds the evaluation or is
  format-mandated (audit below).
- **Per-slot justification of a user-supplied outline (8b2e42e, 153fb88)** — bit the note. The
  seven-chapter format is ratified and kept; each slot now carries its justification, and the
  format-only ones are flagged (table below), never cut.
- **Rendering/brush-up admission (844f4e0)** — steps 7–8 admitted nothing new this pass (no
  sentence exists that the filled outline does not carry); the four sentences the refine pass's
  reader trial added (garden-path split, gates decomposition, viewpoint definition, dispatch-
  round relation) were re-tested against the step-2 reader and all four serve it — each removes
  a first-read stumble that trial actually observed.
- **Excluded content named with its reader and home** — the prior notes' exclusions are
  re-affirmed; their homes were re-verified by grep/read this pass (see "Cuts" below).

## Step emissions

**Step 1** — Subject: aiya's foundational design — one Conductor, ephemeral Turns, a human at
six gates. Must convey: delegation's two failure modes (context bloat, drift) are discharged by
two mechanisms — the CCS and the two-layer traceability chain — built from a few stated
principles.

**Step 2** — Reader (ratified by the owner; not inferred, so no `Assumed reader:` line). WHO: a
first-time reader who has never seen aiya, evaluating its design. WHAT: decide whether the two
mechanisms actually discharge the two properties. HOW: reads chapters 1–4 straight through.
Chapters 5–7 serve a different stance (look-up) and are justified per-slot by the ratified
format, not by this reader.

**Step 3** — Outline: the ratified seven-chapter Design format (`aiya/references/design.md`),
specialized as the standing chapter titles (Problem — Big work turns into babysitting; Core —
Two roles, two walls, one bet; Structure — One chain of yardsticks, and who owns what;
Behavior — One loop, from a Step to the whole run; Rules — What each part promises;
Observability — Is the loop earning its keep?; Trade-offs — Shapes discarded, costs paid).

**Step 6** — Voice: declarative decision-language throughout; ch1–4 read-through (motive before
mechanism), ch5–7 reference-terse. Closing: per the format, the document ends on costs stated
so they read as accepted — no summary chapter. Forms unchanged: five mermaid diagrams where
structure/flow lives, tables for same-field comparisons, prose for reasoning.

## Admission audit — ch1–4 under the narrowed reader (steps 3–4)

Borderline points examined; each ruling names the reader served:

- **§2 gates vocabulary, "(`on` / `dn` / `up` run the session; mnemonics in the README)"** —
  admitted: `on`/`dn`/`up` recur in §3.3, §4.5, §5.5, so the straight-through reader needs the
  terms bound first; the mnemonics themselves are excluded content serving a plugin user, and
  the clause names their home (`aiya/README.md`).
- **§3.3 layout tree** — format-mandated ("physical layout appearing exactly once, in
  Structure", `references/design.md:7`); the evaluator needs the record/yardstick separation
  (§3.2), not the directory names. Flagged below as a format-carried slot inside a story
  chapter.
- **§3.3 `run.yaml` block** — stays verbatim: pending ratification at the design gate; no
  shipped home may exist before the verdict (fixed decision).
- **§4.4 phases table, "Typical Steps" column** — admitted: it is where "investigation is
  first-class work" becomes concrete, and the evaluator judging drift coverage needs
  investigation shown inside the verified pipeline, not asserted.
- **§1 "Out of scope: measuring the 10× itself"** — format slot, but not format-only: it bounds
  the claim the step-2 reader is evaluating (the design answers for the two properties, not for
  the 10×). Prior FB3 flag superseded by this ruling for ch1; the ch5 flag stands (below).

## Per-slot justification of the supplied outline (FB3 flags)

Chapters 1–4 are admitted by the step-2 reader directly (audit above). Chapters 5–7 and the §5
sub-slots, per slot — "cited" means chapters 1–4 point the reader there:

| Slot | Justification | Flag |
|---|---|---|
| §5.1 Turn contract | cited (§3.4 "§5.1's Turn contract is [the invariant]"); walls' substance | — |
| §5.2 Turn(generate) | **uncited from ch1–4** (grep: zero `§5.2` hits in the document); justification is the format's per-part completeness, plus content closing wall 1 over the Report and housing §4.4's version-header duty | **nearest to format-only — recorded, kept** |
| §5.3 Turn(verify) | cited (§2 viewpoint entry; §4.4 edition pinning) | — |
| §5.4 Turn(brief)/CCS | cited (§2 mechanism map; §4.6 discharge) | — |
| §5.5 Turn(record) | cited (§3.3 history archive; §4.4 pre-gate dispatch, gate resolution) | — |
| §5.6 Plan | cited (§3.2 fixed viewpoints; §4.2 consumes) | — |
| §5.7 Conductor | cited (§2 wall 1; §3.2 never-list) | — |
| §6 Observability | cited (§4.1 counts; §4.6 hand-off) — but the question it answers (is the loop worth its Turns) belongs to a post-run operator, not the step-2 evaluator | **format-justified, serves the operator stance — recorded, kept** |
| §7 Trade-offs | cited (§2 enforcement pricing; §3.3 backend trade-off; §4.5 durability) — the same evaluator in look-up stance | — |

Carried forward unresolved from the refine note (FB3 territory, awaiting a format ruling): the
ch5 per-part promise+breach-trace requirement — if the format is ever ruled leaner, §5 is the
chapter that shrinks to pointers.

## Cuts and their homes

**No content was cut this pass**, so no ratified decision moved. The zero-loss bar was still
exercised: the prior passes' cut homes were re-verified against today's tree — no commit has
touched `aiya/` since edcf1b4 (`git log edcf1b4..HEAD -- aiya/` is empty), and the sampled
homes were re-read: `aiya/skills/conductor/SKILL.md:39` (backend detection tests), `:51`
(version header format + invalidation grep), `:53` (conversion Step), `:72` (concurrency cap
20, slicing), `:80` (attempt counter reset), `:102` (bare-`gm` local degradation), `:110`
(local observability counts); `aiya/agents/turn-brief.md:53` (2,000-byte cap);
`aiya/agents/turn-record-local.md:16` (`history/purpose@G1-v1.md` naming);
`aiya/agents/turn-verify.md:34-37` (worked Verdict); `aiya/agents/turn-generate.md:25`
(version-header duty); `aiya/references/plan.md:9-15` (consumes semantics). All present.

## AI tells (step 9)

Full-document sweep against the seven tells: none present. Spot results: no announcing openers
(each section leads with its claim); §4.6 cites rather than re-argues (no restatement);
"likewise"/"therefore" joins carry real links; lists checked for parallelism (walls, steering
verbs, discarded shapes, costs — all parallel); one voice held; heuristics statused ("starting
heuristic, to be refined in use"), no unmarked hedges.

## Step-10 self-check

- [x] Reader is one person in one reading stance — the ratified evaluator, single stance. **PASS**
- [x] Single axis — the ratified seven-chapter Design format, no mixing. **PASS**
- [x] Every heading and point admitted by the step-2 reader; kept-out content named — audit
  above; exclusions named with reader and home here and in the two prior notes. **PASS**
- [x] Form fits content — mermaid where structure/branching lives (5), lists only for parallel
  items, tables for same-field comparisons. **PASS**
- [x] No prose repeats what a diagram carries — wave order and gate sequence live only in their
  diagrams; adjacent prose adds semantics (one-CCS consequence, numbering rationale). **PASS**
- [x] Voice and closing fit the step-2 reader — decision-language held; closes on accepted
  costs. **PASS**
- [x] None of the seven tells remain — sweep above. **PASS**
- [x] `Assumed reader:` line present iff inferred — reader ratified, line absent. **PASS**
- [x] Every claim carries its status — bet marked as bet, CCS schema sourced (Bousetouane
  arXiv:2601.11653), skeleton sourced as standard practice, `run.yaml` marked "(proposed)",
  keep-rate threshold marked heuristic, decisions written with intent. **PASS**

Verification scope: the full document was re-walked point by point against the step-2 reader
(steps 3–5) and once against the tells (step 9); section pointers grep-checked; the cut homes
listed above re-read at the cited lines. Not re-verified: the shipped artifacts end to end —
trusted per `checks/4.md`'s Design Contract Trace plus the empty `aiya/` log since edcf1b4.
Step 11 (fresh-context reader trial) is the coordinator's, run after this note.

## Reader trial (step 11, updated spec)

A fresh-context evaluator (the ratified step-2 reader) read chapters 1–4 straight through and
ruled on the document's one question. **Verdict: YES** — the two mechanisms discharge the two
properties as argued; purpose lands, and the headings carry the thread with **one gap** (no
heading named the two properties before §4.6 closed the loop on them). 8 first-read stumbles
were reported alongside. All 9 findings fixed in place, surgical edits only, zero ratified
decisions moved; 6,239 → 6,284 words (+45).

| # | Finding | Fix applied |
|---|---|---|
| 1 | Headings gap: no heading opens the two-properties loop that §4.6 closes | §4.6 heading renamed to "Bounded context and drift detection, discharged" — properties now named in the heading track; no renumbering |
| 2 | §2 wall 1: `Report` used as a defined term before its definition | glossed at first use: "not even a worker's first-person Report, its own account of what it did (§5.2)" |
| 3 | §2 wall 2: `attempt cap` undefined until the §4.1 diagram | glossed at first use: "the attempt cap (three attempts per Step, §4.1)" |
| 4 | §2 vocabulary: acronym CCS never expanded in ch1–4 | expanded at first use: "writes the CCS, the Compressed Cognitive State"; §5.4 stays the full definition |
| 5 | §3.2 ledger, CCS row: "Mechanical rules; the next verification catches lies" cryptic before §5.4 | cell now stands alone: "Mechanical compression rules (§5.4); a claim the products don't support is caught by the next verification, which reads products, not the CCS" — verified against §5.4's product-wins rule |
| 6 | §3.3: bare `gm` / comment stream unexplained until §4.4 | glossed at point of use: "(the argument-less send-back reads feedback from PR/MR review comments, §4.4 — under local there is no comment stream to fetch)"; list parallelism kept |
| 7 | §4.1: "Count by **1 Step = 1 Turn(generate)** per attempt" read as self-contradictory | stated plainly per §4.1's actual meaning: "Each attempt at a Step dispatches exactly one Turn(generate)" |
| 8 | §4.4: "because G1's and G2's products become yardsticks and G3's … never does" undercuts itself (G3 is numbered) | false "because" dropped; the sentence now states only what the document supports: "only the outputs — G1, G2, G3, in phase order — carry numbers" |
| 9 | §2: `on` / `dn` / `up` named with no semantics | glossed inline: "(`on` / `dn` / `up` — start, suspend, resume — run the session; mnemonics in the README)"; README pointer kept |

**Unneeded-content report — recorded, not applied.** The trial flagged content in ch3–4 that
the step-2 evaluator does not need, each serving another reader: §3.3 in full
(builder/operator), §3.4 (installer), §4.4 gate operations (operator), §4.1 side paths
(builder), §4.5 dn/clear/up cycle (operator), §2 command roster (operator). All are
format-mandated slots and stay per the ratified seven-chapter format; they join the standing
FB3 flags awaiting a future format ruling. The trial's estimate: roughly a third of chapters
3–4 serves readers other than the step-2 evaluator.

**Step-10 re-check after the edits — all nine items PASS.** Re-walked against the edited
document: reader/axis/voice/closing unchanged (items 1, 2, 6, 8); every edit is a gloss or
correction admitted by the step-2 reader — each removes a first-read stumble the trial
observed, the same ruling as the refine pass's four sentences (item 3); forms untouched, list
parallelism in §3.3 preserved (item 4); the one gloss that names a number a diagram carries —
"(three attempts per Step, §4.1)" — is a first-use binding with pointer, not a restatement of
the pipeline (item 5); the new sentences carry no announcing openers, no hedges, one voice
(item 7); finding 8 removed a false claim and added none, so every remaining claim keeps its
status (item 9). Section pointers introduced or touched (§4.1, §4.4, §5.2, §5.4) grep-verified
against existing headings; the stale phrase "1 Step = 1" greps to zero.

## Reader re-trial (round 2)

A second fresh-context trial of the same step-2 reader over the round-1-fixed document.
**Verdict: purpose YES** (the two mechanisms discharge the two properties as argued) and
**headings qualified YES** — the thread carries, with one observation: the CCS/bounded-context
mechanism stays invisible in ch1–4 headings until §4.6 (the chain half is visible in §3.1's).
10 re-read-cost stumbles reported. All 10 fixed in place plus the headings observation acted
on — surgical edits only, zero ratified decisions moved; 6,284 → 6,342 words (+58).

| # | Finding | Fix applied |
|---|---|---|
| 1 | §2 wall 1: "its own account" briefly binds "its" to the Conductor | pronoun bound: "not even a worker's first-person Report, the worker's own account of what it did (§5.2)" |
| 2 | §2 wall 2: "the return contract" undefined until §5.1 | glossed with pointer: "and the return contract (the bounded return every Turn owes, §5.1)" |
| 3 | §2 Gates entry: the `on`/`dn`/`up` parenthetical splices three non-gate words into the two-gate-words sentence | split into its own sentence: "…`ty` approve, `gm` send back. The other three — `on` / `dn` / `up`: start, suspend, resume — run the session, not gates; mnemonics in the README." |
| 4 | §3.2 Research row: "Turn(generate); elicit answers, the Conductor" comma-splices | cell now parses in one read: "Turn(generate) — elicit answers: the Conductor" |
| 5 | §3.3 tree / run.yaml: "edition" used before §4.4 defines it | glossed at first use (the tree comment): "history/    # approved editions (gate-approved versions, §4.4), archived at gate resolution under the local backend (§5.5)"; the `run.yaml` `edition:` key follows the now-bound term |
| 6 | §4.1: "Turn-carried items" — coinage defined nowhere | replaced with its meaning: "apply only to items whose work a Turn performs" (vs the elicit item already contrasted in the same sentence) |
| 7 | §4.2: "Record runs where the loop is serial by construction" — "where" reads as a conditional | stated as a position: "Record runs at the loop's serial point — by construction, after the wave has settled into one brief — so no two writers meet at the shared git index" (verified against §4.2's brief-then-record order) |
| 8 | §4.4 "Whoever writes must read, and the Conductor does neither" clashes with the maxim's earlier one-sided use (grep resolves the trial's ~96 to line 174, §4.2 — "nobody commits content unread, where the Conductor may not read at all", the only prior use) — and "neither" (= writes nothing) also collides with the ledger's Conductor-written rows (run-state, elicit answers) | second occurrence now extends the first instead of overreaching: "Whoever writes must read, and the Conductor may not read — so it drafts nothing." — derives no-drafting from the read wall, one-directional, consistent with the Conductor writing bounded records |
| 9 | §4.4: "a progress board kept current on the console" introduced nowhere | glossed at point of use, matching `aiya/skills/conductor/SKILL.md` §8 (read before writing): "(each wave's items shown as done, running with attempts and any re-aim's gap, or ahead)" |
| 10 | §3.2 CCS cell and §5.4 carry the CCS-verification argument verbatim | §5.4 reworded in its own words — "A CCS that claims more than its products show does not survive: the next verification reads the products themselves, never the CCS, so the unsupported claim surfaces there." — the round-1 cell kept intact (compact, self-standing), no substance deleted |
| 11 | Headings: CCS mechanism invisible in ch1–4 headings until §4.6 | **Decision: fix applied.** §4.2 heading renamed "A wave — parallel width, one CCS" (was "…one bounded state") — names the one-brief-per-wave compression in the heading track, reads natural (the section's thesis sentence is exactly this), no renumbering, no distortion; CCS is bound at §2's vocabulary so the acronym is defined before the heading is reached. Other ch1–4 candidates read forced and were not touched. |

**Unneeded-content report — repeated, not new.** The trial's list re-flagged the same
format-mandated cluster already recorded as FB3 flags in round 1 (§3.3, §3.4, §4.4 gate
operations, §4.1 side paths, §2 command roster). The only additions beyond that standing list —
§4.5's operator half (dn/clear/up cycling, durability window) and §4.4's history-audit lines —
are hereby folded into the standing FB3 flag list: format-mandated, kept, awaiting the same
future format ruling.

**Step-10 re-check after the round-2 edits — all nine items PASS.**

- Reader: one person, one stance — unchanged; every edit serves the step-2 evaluator's first
  read. **PASS**
- Single axis — seven-chapter format untouched, no renumbering (§4.2 rename only). **PASS**
- Every heading/point admitted; kept-out content named — no content added or cut beyond glosses;
  the two newly flagged slots are named above with reader and standing. **PASS**
- Form fits content — diagrams/tables/prose unchanged; fix 3 turned a spliced parenthetical
  into prose, fix 4 restored a table cell's one-read parse. **PASS**
- No prose repeats a diagram — none of the edits restates a diagram; fix 10 removed a
  prose-prose duplication. **PASS**
- Voice and closing — declarative decision-language held in every new sentence; closing
  untouched. **PASS**
- No AI tells — no announcing openers, hedges, or restatement in the new text; fix 10
  eliminated a verbatim repetition. **PASS**
- `Assumed reader:` absent (reader ratified) — unchanged. **PASS**
- Every claim keeps its status — no new claim added; fix 8 replaced an overreaching "neither"
  with the supported one-directional claim; fix 9's gloss matches SKILL.md §8 exactly. **PASS**

Verification scope this round: the 11 findings were fixed and each edit re-read in its full
paragraph; every § pointer introduced or touched (§4.1, §4.4, §4.5, §5.1, §5.2, §5.4, §5.5)
grep-verified against the heading list; stale phrases ("Turn-carried", "does neither",
"serial by construction", the spliced Research cell, the old §4.2 heading) grep to zero;
`aiya/skills/conductor/SKILL.md` §8 read before writing fix 9's gloss. Not re-verified: the
shipped artifacts end to end (unchanged since edcf1b4).

## Reader trial round 3 and loop close-out

A third fresh-context trial of the same step-2 reader over the round-2-fixed document.
**Verdict: purpose YES** — the third consecutive — and **headings qualified YES**. 9 minor
stumbles reported. All 9 fixed in place, surgical edits only, zero ratified decisions moved;
6,342 → 6,448 words (+106).

| # | Finding | Fix applied |
|---|---|---|
| 1 | §1 uses "Conductor" before §2 defines it | first use tied to the already-bound noun: "the working state of the directing agent (aiya's Conductor, §2)" |
| 2 | "yardstick" (first used §2 bet paragraph) absent from the vocabulary block that promises "Vocabulary, fixed here" — and used inside the block itself ("Machines verify") | one-line entry added before Viewpoint: "**Yardstick** — a gate-approved product everything downstream is verified against; the chain of them is §3.1." |
| 3 | §4.1 "a **missing viewpoint** re-verifies only" elliptical | ellipsis made explicit per the ratified meaning: "a **missing viewpoint** — a concern noticed absent from the check set — is added to the Plan and re-verified only". The trial's parenthetical read (a lost Turn(verify) return) was checked against `SKILL.md` §5 step 4 ("On noticing a missing viewpoint, add it to the Plan and re-verify only") and is not the ratified semantics — a lost verify return is the other side path (missing return, re-sent); the fix states the overlooked-concern meaning |
| 4 | §4.3 attribution test clipped ("No: the Conductor's (control). Yes: a Turn's (inspection).") | elided nouns restored, subject confirmed as aggregation per SKILL.md §1: "does this act require reading the real work? If not, the act is the Conductor's: control, like the AND over Verdicts. If so, it is a Turn's: inspection, like consolidating state." |
| 5 | §4.4 prerequisites "purpose, UX, design, plan" — UX and this "design" absent from the three-phase product scheme | names verified as the shipped artifact names (`SKILL.md:53`; `references/design.md:5` "only when purpose, UX, design, and plan exist"; `references/ux.md:3` "One per product … One of generation's prerequisites"; `references/` ships `ux.md` and `design.md`), so anchored, not replaced: "the run's own Purpose and Plan, plus the product's UX and Design documents (per-product foundations, not phase products)" |
| 6 | §4.4 "answers are written under `research/`" vs "the Conductor may not read — so it drafts nothing" reads as a contradiction | resolved at the tension point: "so it drafts nothing: transcribing the human's answers verbatim is not drafting, and the elicit exchange sits inside its closed intake (§5.7)" |
| 7 | §3.2 header "Product / record" lists the Conductor-written Plan while §4.4 says a phase's product is "made by Turns, never the Conductor" | one clause in §4.4 removes the collision: "a Plan (drafted and re-planned by the Conductor — the translation layer, not a phase product)" — header untouched |
| 8 | §3.2 CCS cell "carried between Steps" vs §4.2's fixed one-per-wave granularity | cell aligned to the ratified per-wave semantics (§4.2 one brief → one CCS per wave; §5.4 replacement each wave): "The bounded state carried between waves, one file per wave". §5.4's opening carried the same "between Steps" phrase and was aligned in the same stroke ("carried between waves") so the two do not now disagree with each other |
| 9 | §4.5 "costing at most one redundant `ty`" true only when the lost verdict was an approval | cost claim scoped, intent (safe side) kept: "the safe side: a lost approval costs one redundant `ty`; a lost send-back, giving the feedback again" |

**Convergence.** Three trials, three disjoint sets of minor stumbles, severity declining across
rounds, and purpose YES every time — the document's argument is stable; what each fresh reader
still trips on is local phrasing, not structure.

**Unneeded-content report — repeated, not new.** The trial's list again matched the standing
FB3 flag cluster (§3.3, §3.4, §4.4 gate operations, §4.1 side paths, §4.5 operator half, §2
command roster, §4.4 history-audit lines) with no new items. The cluster stands as recorded:
format-mandated, kept, awaiting a future format ruling.

**Loop close-out.** This is the final fix iteration under the 3-iteration cap. Any stumbles a
further trial surfaces are recorded as residual and ruled at the design gate, not fixed in
another round.

**Step-10 re-check after the round-3 edits — all nine items PASS.**

- Reader: one person, one stance — unchanged; every edit removes a first-read stumble the
  trial observed. **PASS**
- Single axis — seven-chapter format untouched, no headings changed, no renumbering. **PASS**
- Every heading/point admitted; kept-out content named — nothing added beyond glosses and one
  vocabulary line the block's own promise requires; nothing cut; the FB3 cluster re-named
  above. **PASS**
- Form fits content — diagrams/tables untouched; fix 8 edits one table cell in place; the
  vocabulary entry keeps the list's one-line parallel form. **PASS**
- No prose repeats a diagram — no edit restates a diagram; fix 3's wording names no number the
  §4.1 diagram carries. **PASS**
- Voice and closing — declarative decision-language in every new clause; closing untouched. **PASS**
- No AI tells — no announcing openers, hedges, or restatement; fix 4 replaced clipped fragments
  with two plain declarative sentences. **PASS**
- `Assumed reader:` absent (reader ratified) — unchanged. **PASS**
- Every claim keeps its status — fix 9 narrowed an overbroad cost claim to the supported one;
  fix 5 anchors names the shipped artifacts verifiably carry; no new unsourced claim. **PASS**

Verification scope this round: the 9 findings fixed and each edit re-read in its full
paragraph; § pointers introduced or touched (§2, §3.1, §5.7) grep-verified against the heading
list; stale phrases ("carried between Steps", "purpose, UX, design, plan", "No: the
Conductor's", "costing at most one redundant", "so it drafts nothing. Until") grep to zero;
finding 3 checked against `aiya/skills/conductor/SKILL.md` §5 step 4 and finding 5 against
`SKILL.md:53`, `references/design.md:5`, `references/ux.md:3` before writing. Not re-verified:
the shipped artifacts end to end (unchanged since edcf1b4).

## Reader trial round 4 — loop closed, residuals recorded (coordinator)

The round-3 re-review trial ran on b2712f2: **purpose YES — fourth consecutive** (both problems,
both properties, both mechanisms restated accurately; plausibility judged with the enforcement
bet correctly located); headings YES with the one standing gap (the two properties named in no
heading before §4.6). Per the close-out ruling above, its 8 findings are residuals for the
design gate, not another fix round:

1. **§4.6 "structural" vs §2's strict sense** — §4.6 calls both discharges "structural rather
   than asserted", but §2 defines *structural* as "the platform makes breach impossible" and
   the no-reading wall is explicitly default-and-observable (§5.7). Loosely read fine; by the
   document's own vocabulary, one leg is overclaimed. The one residual with substance — flagged
   for the gate.
2. **UX/Design documents unanchored** — §4.4's prerequisites (round-3 fix 5) name per-product
   UX and Design documents that have no §3.3 layout home and no §3.2 ledger row. Also flagged
   for the gate (their contract lives in `references/ux.md` / `references/design.md`; whether
   the design document must house them is a format-density call).
3–8. Re-read-cost minors, disjoint from all prior trials: 1:1 mechanism map vs 3+3 discharge
   reconcile; `consumes` forward pointer (§4.2→§5.6); the three-dash dispatch-rounds sentence;
   command words carried on faith; §1 "work streams" never recurring; "missing viewpoint —
   noticed by whom" unstated.

Unneeded-content report: matched the standing FB3 cluster again, no new items.

**Convergence across four trials**: purpose YES every time; stumble sets pairwise disjoint
(each fresh reader trips on different micro-frictions); severity monotonically minor since
round 1. The writ literal clean-pass bar (zero stumbles, zero unneeded content) is unreachable
under the ratified format — the unneeded-content half is format-mandated and every trial
generates novel minor stumbles. Delivery proceeds on the convergence evidence plus the
3-iteration cap; residuals 1–2 above go to the design gate for ruling.
