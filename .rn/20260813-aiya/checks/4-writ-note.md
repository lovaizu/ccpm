# What changed — writ rebuild of aiya/docs/design.md

The document was rebuilt fresh from the previous draft's content and intent (writ procedure, not
in-place editing). 10,612 → 7,269 words (`wc -w`, markup included); 3 → 5 mermaid diagrams.

## Writ step emissions

**Step 1 — Subject / Must convey.**
Subject: aiya's foundational design — one Conductor, ephemeral Turns, a human at six gates.
Must convey: delegation's two failure modes (context bloat, drift) are answered by a few
load-bearing principles — the bet on model progress, two walls instead of a controller,
one bounded state per wave, a two-layer traceability chain — from which the concrete behavior
reads off simply.

**Step 2 — Reader** (ratified by the owner; not inferred, so no `Assumed reader:` line in the
document). WHO: a first-time reader of aiya — the person deciding whether the design is sound,
and the person who will build on or maintain it. WHAT afterward: understand why aiya exists and
how its few principles produce its behavior, well enough to approve the design or challenge a
specific choice. HOW: straight through for chapters 1–4; chapters 5–7 consulted when a question
arises.

**Step 3 — Outline.** The axis is aiya's own shipped Design format
(`aiya/references/design.md`) — seven fixed chapters, overriding the writ's five generic axes:

1. Problem — Big work turns into babysitting
2. Core — Two roles, two walls, one bet
3. Structure — One chain of yardsticks, and who owns what (chain / ledger / on-disk / what ships)
4. Behavior — One loop, from a Step to the whole run (Step / wave / steering / gates / suspend-resume / discharge)
5. Rules — What each part promises (Turn contract, generate, verify, brief, record, Plan, Conductor)
6. Observability — Is the loop earning its keep?
7. Trade-offs — Shapes discarded, costs paid

The old draft's extra chapter (§6, discharging the two properties) diverged from the
seven-chapter shape. **Call recorded here**: its substance is folded into §4.6 as the close of
Behavior — the properties are defined in Problem, and the story of chapters 1–4 lands by
discharging them where the behavior that discharges them has just been shown. Observability
keeps only the cost question, which was already its job. Off-axis material moved out per the
owner's diagnosis: contract-level lookup detail (schemas, vocabularies, worked examples,
adapter procedure) now lives only in the shipped artifacts it always shipped in — see the
disposition list.

**Step 6 — Voice / Closing / per-section form.**
Voice: declarative decision-language throughout — decisions stated as choices with intent,
facts with sources, heuristics marked as heuristics. Chapters 1–4 read-through (motive before
mechanism); chapters 5–7 reference-terse. Closing: per the format, the document ends on costs
stated so they read as accepted — no summary chapter.
Forms: §1 prose + two parallel pairs (failure modes / properties). §2 prose + the whole-system
diagram. §3 chain diagram, ownership table, layout tree, run.yaml block (kept verbatim as the
pending proposal). §4 step-pipeline diagram, **new** wave-pipeline diagram, phases table,
**new** gates diagram, prose. §5 numbered contract list, Verdict YAML example, prose per part.
§6 ratio table + prose. §7 two parallel lists.

## Substance changes, tied to reader and purpose

- **Principles stated once, decisions read from them.** The enforcement rule ("no controller
  program → every rule is structural, or default and observable") is now stated once in §2;
  the old draft restated it per part. §5 states only each part's promise and breach trace.
- **Vocabulary moved to Core** (Phase/Plan/Step/Turn, role families, gates, elicit items,
  verify-vs-review), per the shipped format ("vocabulary is fixed here too"); the old draft
  fixed it in §3.1, forcing the Core argument to run on undefined terms.
- **Two new diagrams where flow genuinely lives**: the wave pipeline (generate×N → verify →
  one brief → one record → steer), which the old draft carried as a bolded prose sentence,
  and the six-gate sequence, which the old draft carried as a table the chapter then re-explained.
- **The discharge (§4.6) compressed ~400 → ~190 words**: with the principles stated once in
  §2–§4, the discharge now cites rather than re-argues.
- **The rebuild makes `references/design.md:34` true**: seven chapters titled
  "Chapter — gist", headings alone telling the story, physical layout exactly once (§3.3),
  chapters 1–4 story / 5–7 reference.
- **The run-state proposal kept recognizable as pending**: `run.yaml` marked "(proposed)" in
  §3.3, with fields `backend`/`branch`/`gates`/`status`, the Planning-Gate identifier
  (`purpose-planning`), and the example branch `aiya/csv-export` all verbatim.

## Disposition list — every contract-bearing clause that did not survive verbatim

Categories: **carried** (lives in a shipped artifact; file named, per the Design Contract Trace
in `checks/4.md`) / **derivable** (reads off a principle the rebuilt document states) /
**dropped** (with reason). Everything not listed here survives in the rebuilt document,
compressed but intact.

### Old §2 (Core)

- "The agent platform permits nesting by default" — **dropped**: platform background; the
  operative contract (spawn tool omitted from every Turn definition) survives in §2 and §5.1.
- Wall 1 aside "half the answer to bounded context" — **dropped**: restatement; the full
  discharge is §4.6.

### Old §3.1 (Parts and vocabulary)

- The four-skills enumeration ("do a unit of domain work and report on it; judge with no prior
  context; consolidate several accounts into one fixed-shape state; operate a platform without
  touching content — every Turn exercises exactly one") — **derivable** from one-role-one-skill
  (rebuilt §3.2) plus each role's §5.2–§5.5 definition; the per-role phrasings are also
  **carried** by the shipped agent preambles (`aiya/agents/turn-*.md`).
- "G is short for Gate" — **dropped**: glossary trivia; G1–G3 usage carries it.
- "The Turn(verify)s around it, and the wave's Turn(brief) and Turn(record), are ephemeral
  measurement and run-keeping" (opened old §4.1) — **derivable**: restates §2's role families.

### Old §3.3 (ownership)

- The reverse-side table (six rows of role × not-responsible-for) — **carried**:
  `aiya/skills/conductor/SKILL.md` §1 (do/never) and the three `aiya/agents/turn-*.md`
  preambles (trace row "§3.4 reverse side"); also **derivable** from one-role-one-skill.
  The Conductor's row survives as §5.7; the Human's row is derivable from
  machines-verify/humans-review plus the two-roles definition.

### Old §3.4 (where things live)

- "writing run files is not new to it: it already writes elicit answers under `research/`" —
  **dropped**: supporting argument for the writer choice; the choice and its load-bearing
  reason (only party present at every boundary event) survive in §3.3.

### Old §4.2 (waves)

- "The full pipeline of one wave is therefore fixed: generate ×N → verify → one brief →
  one record → the Conductor steers" — **not dropped, form-changed**: now carried by the §4.2
  wave diagram instead of prose (writ form rule: prose must not repeat the diagram).

### Old §4.3 (steering)

- "For the same reason the CCS is replaced rather than appended, the Plan is steered by
  re-planning" — the analogy **dropped**: both underlying rules survive independently
  (§5.4 replacement semantics; §4.3 re-planning-not-diffs).

### Old §4.4 (phases and gates)

- "a Delivery product's viewpoints are drawn from both documents, so its Verdicts cite
  `purpose@G1-vN` or `approach@G2-vN` individually" — **derivable** from Delivery's dual
  yardstick (§4.4) plus per-Verdict edition pinning (§5.3); the consequence (the invalidation
  grep finds exactly the Verdicts pinned to a revised document) survives in §4.4.
- Progress-board contents ("waves, running items, attempts") — **carried**: conductor SKILL §8
  (trace row "§4.4 progress board"); "a progress board kept current on the console" survives.

### Old §5.2 (Turn(generate))

- The fenced Report format block — **carried**: `aiya/references/report.md` (still linked) and
  `aiya/agents/turn-generate.md`; the three headings and their CCS-source mapping survive in
  §5.2 prose.
- "It is never machine-processed … so it is not YAML" — **dropped**: format-choice rationale;
  the facts it argued from (only brief reads it; it is Markdown) survive.

### Old §5.4 (Turn(brief) / CCS)

- The nine-component role/sourced-from table — **carried**: `aiya/agents/turn-brief.md`
  (ships the table inline; trace row "§5.4 nine components"). The component names and the
  sourcing rule (product wins; Report only for tried/unsure) survive in §5.4.
- The `type` vocabulary table (9 rows) — **carried**: `aiya/agents/turn-brief.md`.
- The worked CCS YAML example — **carried**: `aiya/agents/turn-brief.md`.
- "quote any value containing a `:`" — **carried**: `aiya/agents/turn-brief.md`.
- "YAML's native shape … no notation is invented … greps, and being real YAML parses with
  standard tools" — **dropped**: format-choice rationale; the choice (YAML, nine fixed
  components) survives.
- The symptom→remedy table (focal_entities / relational_map / uncertainty_signal) —
  **carried**: conductor SKILL §6 (trace row "§5.4 breach symptoms", commit 2ee0d49); the
  gist survives in §5.4 ("which component bloats diagnoses the Step's scope: split it, narrow
  it, or add a Step that resolves the pile-up").

### Old §5.5 (Turn(record))

- Per-adapter local behavior at `on`, pre-Planning-Gate, and G3 ("the local adapter confirms
  and reports them", "no CCS yet to name", "no `history/` edition at G3; confirms and reports
  the run directory's final state") — **carried**: `aiya/agents/turn-record-local.md` and
  conductor SKILL §2/§3/§8 (trace rows "§5.5 …", "Gate-stop ruling"). The local adapter's
  defining rules (no git operations; same dispatch points and return; the `history/` archive)
  survive in §5.5.

### Old §7 (observability)

- Commit-provenance breakdown ("one per wave, plus the `on` / gate / `dn` events and one per
  Plan draft or Planning-Gate rework") — **derivable** from §5.5's five dispatch points; the
  headline ("Turn(record) dispatches are the commit history itself") survives in §6.

### Old §6 (Closing) and §8 (Trade-offs)

- Old §6 folded into §4.6 (see step-3 call above); every bullet's substance survives.
- Old §8 survives complete: all seven discarded shapes and all eight costs, each compressed,
  none dropped.

## AI tells caught (step 9)

Built fresh, the draft needed one net catch:

- **Tell 3 (vague claim where a referent belongs)** — "Investigation Steps exist in every
  phase, and pay most there" left "pay" without a subject. Fixed to the source's claim:
  "it is on them that compression and independent checking pay most, not least".

Sweep of the other six tells: no padding openers, no restatement (§4.6 cites rather than
re-argues), no flavorless connectives, lists checked for parallelism, one voice held, no
hedges — heuristics are explicitly statused instead ("starting heuristic, to be refined in
use").

## Step-10 self-check

- [x] Single axis — the shipped seven-chapter Design format, no mixing. **PASS**
- [x] Reader reaches the purpose top to bottom — problem → principles → statics → dynamics →
  discharge; §5–§7 consulted, not required for the argument. **PASS**
- [x] Form fits content — mermaid where structure/flow lives (5 diagrams), lists only for
  parallel items, tables for same-field comparisons. **PASS**
- [x] No prose repeats what a diagram carries — the wave pipeline order and the gate sequence
  live only in their diagrams; surrounding prose adds semantics the diagrams cannot. **PASS**
- [x] Voice and closing fit the step-2 reader — decision-language held throughout; closes on
  accepted costs per the format. **PASS**
- [x] None of the seven tells remain — post-fix sweep clean. **PASS**
- [x] Headings alone carry the argument — chapter and section headings read as the story
  (verified by reading them in sequence). **PASS**
- [x] `Assumed reader:` line present iff inferred — reader was ratified, line absent. **PASS**
- [x] Every claim carries its status — the bet marked as a bet, borrowed skeleton and CCS
  schema sourced (industry standard; Bousetouane arXiv:2601.11653), size cap and keep-rate
  threshold marked as starting heuristics, `run.yaml` marked proposed, decisions written with
  intent. **PASS**

Verification scope: every sentence of the rebuilt document was written against the previous
draft (each claim traced before writing); the two carried relative links
(`../references/report.md`, `../references/plan.md`, plus the `../references/` directory
citations) confirmed to resolve from `docs/`; the run.yaml proposal fields confirmed present
verbatim. Not re-verified here: the shipped artifacts named in the disposition list were
trusted per `checks/4.md`'s Design Contract Trace, not re-read end to end.
