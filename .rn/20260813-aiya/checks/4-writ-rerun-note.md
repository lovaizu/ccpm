# What changed — writ re-run of aiya/docs/design.md (updated procedure)

Re-run of the build-fresh procedure at `origin/worktree-writ` HEAD (153fb88) over the document
already rebuilt under the old writ (486a1af, note `4-writ-note.md`) and refined once (edcf1b4,
note `4-refine-note.md`). **Outcome: the document did not change** — 6,239 words before and
after (`wc -w`). This is a fixed point, not a skipped run: the upstream writ commits
(8b2e42e…153fb88) codify the same PR #15 feedback (2026-08-20) the refine pass already applied
to this document by hand. Every step below was executed; what the updated procedure newly
demands turned out to be note-level obligations — per-slot justification of the supplied
outline and the naming of excluded content — discharged here.

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
