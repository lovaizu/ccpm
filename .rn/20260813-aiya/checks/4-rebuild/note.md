# What changed — rebuild of aiya's Design under the `up` writ

The document was built on a blank page from the ratified seven-chapter outline and the shipped plugin files. `aiya/docs/design.md` was read once, in full, for intent; no sentence of it was reused, and it was never opened for editing. Nothing under `aiya/` was modified.

## Step 1 — Understand the input

`Subject:` aiya's foundational design — the plugin's roles, walls, chain of approved yardsticks, execution loop, per-part rules, cost measures, and rejected alternatives.
`Must convey:` that aiya's two mechanisms — the CCS, and the two-layer chain of yardsticks — actually discharge the two properties the problem demands (bounded context, drift detection), with each leg identified as either structurally enforced or default-and-observable with a named trace.

## Step 2 — Reader and purpose (ratified; not inferred)

- **WHO:** a first-time reader who has never seen aiya, evaluating its design.
- **WHAT they decide afterward:** whether aiya's two mechanisms actually discharge the two properties the problem demands.
- **HOW they read:** chapters 1–4 straight through; chapters 5–7 in a look-up stance.

No `Assumed reader:` line appears in the document: the reader was ratified, not inferred.

## Step 3 — The outline, slot by slot

The outline is the owner-ratified seven-chapter Design format (`aiya/references/design.md`). The seven chapters are fixed and none was cut. Each slot's justification against the step-2 reader:

| Slot | Admitted by the step-2 reader? | Justification |
|---|---|---|
| 1. Problem | Yes | States the two properties the reader's decision is *about*. Without it there is no criterion. |
| 2. Core | Yes | Roles, the two walls, the enforcement principle, and the naming of the two mechanisms — the object under evaluation. |
| 3. Structure | Yes | The chain is drift detection's primary mechanism; the ledger and disk layout show it exists as artifacts, not as an assertion. |
| 4. Behavior | Yes | The loop is where both mechanisms operate; §4.6 is the reader's verdict page. |
| 5. Rules | Format-only (flagged) | Serves a look-up reader — an implementer or a reviewer checking one part's promise. The step-2 reader needs §5 only for the traces §4.6 points at. Kept whole, per the ratified format. |
| 6. Observability | Format-only (flagged) | Serves whoever must decide, after a run, whether the loop paid for itself. Not needed to answer "do the mechanisms discharge the properties" — §4.6 explicitly hands that question over. Kept whole, per the ratified format. |
| 7. Trade-offs | Partly | The rejected alternatives and accepted costs bear on the evaluation (an evaluator asks "compared to what, and at what price"), but the register form is a look-up form. Kept whole, per the ratified format. |

**Axis conflict, recorded rather than resolved.** The writ's step 3 admits exactly one axis. The ratified format is two: chapters 1–4 are the article/explanation axis (a story read top to bottom), chapters 5–7 the reference axis (consulted, not read). The format states this split itself, and the owner ratified it, so it was not resolved away — it is recorded here and marked FAIL in the step-10 self-check.

Headings as built (specialised to this content):

1. Problem — Delegation whose cost climbs with the size of the job
2. Core — One director that never reads, workers that never remember
3. Structure — An approved spine, disposable records, and one place each of them lives
   - 3.1 The spine — yardsticks that cannot move, plans that must
   - 3.2 The ledger — who writes each thing, who checks it, who owns it
   - 3.3 On disk — one directory per run, and one backend behind it
   - 3.4 What ships — six skills, six Turn definitions, seven formats
4. Behavior — The same cycle at three sizes: a Step, a wave, a phase
   - 4.1 One Step — make it, judge it, aim again, or hand it up
   - 4.2 One wave — width in parallel, a single state out
   - 4.3 Steering — rebuild the plan from zero, every wave
   - 4.4 Phases and gates — three questions, six stops, versioned approvals
   - 4.5 Suspending and resuming — nothing special is saved, because nothing special is needed
   - 4.6 The discharge — what each property actually rests on
5. Rules — What each part promises, and the mark a breach leaves
   - 5.1 The Conductor — its two lists
   - 5.2 The Turn contract — five rules, and the invariant they add up to
   - 5.3 Turn(generate) — the product, and an honest account of making it
   - 5.4 Turn(verify) — a single concern, judged and written down
   - 5.5 Turn(brief) — the CCS, bounded by how it is built
   - 5.6 Turn(record) — the physical record, one adapter per backend
   - 5.7 The Plan — three lines an item, and revision with a paper trail
6. Observability — What the loop costs, counted from what it already leaves behind
7. Trade-offs — What was rejected, and what this shape costs

## Step 4 — Points dropped at the fill

Content that belonged to someone else's reader, and where it lives instead:

- **The CCS's nine component names, their vocabularies, and the 2,000-byte soft cap** — an implementer's reader; `aiya/agents/turn-brief.md`. §5.5 states the boundedness rules and the cap's *meaning* (a health signal), not the schema.
- **The Verdict YAML schema and its example** — an implementer's reader; `aiya/agents/turn-verify.md`.
- **The progress-board glyphs, the five command mnemonics, the csv-export walkthrough, install instructions, and the aiya-or-rn comparison** — the prospective user's reader; `aiya/README.md`.
- **Run location on resume** (the `.aiya/` directory carrying a `backend` file; most recently modified when several) — an operator's reader; `aiya/skills/conductor/SKILL.md` §9.
- **The chapter structures of the shipped formats** (what a purpose.md's four chapters each hold, and so on) — the reader drafting one of those documents; `aiya/references/*.md`.
- **Wave slicing mechanics beyond the cap number** — an implementer's reader; conductor SKILL §5. Only the one-clause consequence (throughput, not correctness) is stated.

## Step 5 — Story check, in the reader's order

Walked chapters 1–4 as one line of argument: two properties demanded → the roles and walls that make them possible, plus the two named mechanisms → the artifacts the mechanisms are made of → the loop they run in → an explicit discharge of each property against three legs each. One gap was closed at this step: the original ordering left "what ships" (§3.4) before the reader had seen the loop, making the six-skill inventory meaningless; it stays in Structure, per the format, but is written as an inventory of three artifact kinds rather than as behaviour. One detour was cut: the default viewpoints were pulled forward from the rules chapter into §4.1, where the pipeline first needs them.

## Step 6 — Voice and form

`Voice:` plain and declarative, third person throughout, no second person; each design choice written as a choice with its intent, never as a law of nature; a term is glossed in plain words at its first appearance because the reader has never seen aiya.
`Closing:` chapter 7's accepted costs — what this shape gives up, stated so it reads as accepted.

Form per section:

| Section | Form | Why |
|---|---|---|
| 1 | Prose + two short parallel lists | The failure modes and the properties are genuinely parallel pairs; the reasoning between them is prose. |
| 2 | Prose + one mermaid diagram + one definition list | The whole (roles, walls, the human) is a structure — a diagram. Vocabulary is a definition list. Everything else is a line of reasoning. |
| 3.1 | Prose + mermaid | Two layers over three nodes; the layering is what the diagram carries and the prose does not repeat. |
| 3.2 | Table | Nine records compared on the same four fields. |
| 3.3 | Code block + prose | A directory tree is a tree; the backend reasoning is prose. |
| 3.4 | Prose with bolded leads | Three artifact kinds, not parallel enough to bullet. |
| 4.1, 4.2 | Mermaid + prose | Branching (attempt cap, escalation) and convergence (one brief per wave) are flow, which prose renders slowly. |
| 4.3 | Prose | A line of reasoning about discretion; no items to enumerate. |
| 4.4 | Table + mermaid + prose | Three phases compared on the same fields; the gate sequence is a flow; the rest reasoning. |
| 4.5, 4.6 | Prose | Argument, and the reader's verdict page. |
| 5.1–5.7 | Prose, with a numbered list only where the five Turn rules are genuinely parallel | Look-up sections, so each leads with its promise. |
| 6 | Table + prose | Three measures on the same field; the accounting reasoning is prose. |
| 7 | Two lists | Rejected shapes and accepted costs are both genuinely parallel registers. |

## Step 8 — Brush-up additions

Three concrete facts were added at brush-up, each admitted because it bears on the reader's decision and each verified against the shipped files: the platform's default concurrency cap of 20 (§4.2, conductor SKILL §5), the same-file guard on bundling (§4.2, conductor SKILL §5 and `references/plan.md`), and the four record-adapter rules — explicit paths, read-before-commit, idempotence, no force-push (§5.6, the three adapter definitions).

## Step 9 — AI tells caught

| Tell | Line as drafted | Fix |
|---|---|---|
| 3 — retreat into generalities | "The platform caps how many subagents run at once" | Named the number: "20 by default". |
| 2 — restatement | §3.1's "turns drift into an object" reappeared verbatim as §4.6's first drift leg | §4.6 rewritten as "gives drift a physical form — a Step whose justification does not reach the link above it". |
| 1 — padding | "**Drafting the Purpose is split in two, and the split is deliberate.**" | Cut the second clause: "split between the two roles". |
| 6 — wavering voice | "makes drift a thing you can point at" — the only second person in the document | Rewritten in third person. |
| — prose repeating a diagram | "Six stops, then: three phases times a Plan going in and a product coming out." — the gate diagram already shows all six | Cut to the one fact the diagram does not carry: "Only the outputs carry numbers — G1, G2, G3, in phase order." |
| 1 — throat-clearing framing | "The first wall is that… / The second wall is that…" | Both rewritten to lead with the wall itself. |

No instances of tells 4 (flavourless connectives), 5 (reflexive bulleting), or 7 (hedging) survived the draft; a grep for the standard connectives and hedges over the finished document returns nothing.

**One further defect, found by measurement rather than by reading, and disclosed here.** The document was written on a blank page, but it was written directly after reading the existing one in full, and unconscious phrase carryover was the result. An n-gram comparison against `aiya/docs/design.md` (8-token windows, mermaid blocks excluded) found 127 maximal shared spans, several of them 15–24 tokens long — whole clauses reproduced verbatim. Fifty-three passages were rewritten in two passes; the residue is 61 spans covering 7.3% of the document's tokens, and every remaining span of 10 tokens or more is an identifier rather than wording: the Bousetouane citation, the run-directory tree, two table header rows, the three ratio formulas, the phase names, and the fixed vocabulary (`Purpose (why) → Approach (how) → Delivery (execution)`). Exactly one full line is identical between the two documents — the verification-overhead formula. The measurement script is reproducible: normalise both files, drop mermaid blocks, and diff 8-gram sets.

## Step 10 — Self-check

- [x] **PASS** — Reader is one person in one reading stance (ratified, §2 above).
- [ ] **FAIL (disclosed, not fixable at this level)** — Single axis. The ratified format is two axes: article for chapters 1–4, reference for 5–7. The format states the split itself and the owner ratified it, so it is recorded here per step 3's headless rule rather than resolved. Fixing it would mean rejecting the ratified format.
- [x] **PASS** — Every heading and point admitted, with the exception recorded: chapters 5–7 are admitted by format ratification rather than by the step-2 reader, flagged per-slot in the step-3 table; everything kept out is named in step 4 and in "Decisions I did not carry".
- [x] **PASS** — Form fits content: five mermaid diagrams for structure and flow, four tables for same-field comparisons, lists only where items are parallel.
- [x] **PASS** — No prose repeats what a diagram carries (one violation found and cut at step 9).
- [x] **PASS** — One voice held throughout; closing is chapter 7's accepted costs, which fits an evaluating reader.
- [x] **PASS** — None of the seven tells remain.
- [x] **PASS** — No `Assumed reader:` line, correct: the reader was ratified, not inferred.
- [x] **PASS** — Every claim carries its status, with three flags: the Bousetouane citation is carried as the owner's attribution and is *not* corroborated by any shipped file (nor was the arXiv entry checked — no network access was used); the 50% keep-rate figure is stated as a starting heuristic, not a measured rule; the local backend's uncountable dispatch points are stated as a limit of counting rather than estimated.

## Fact-check against the shipped files

Every behavioural claim in the rebuilt document was checked against `aiya/skills/conductor/SKILL.md`, the five entry skills, the six agent definitions, `aiya/references/*.md`, `aiya/README.md`, and `aiya/.claude-plugin/plugin.json`. One material divergence was found in the existing document and is *not* repeated:

**The run-state file `state.yaml` does not exist in the shipped plugin.** `docs/design.md` introduces it once as "(proposed)" and then asserts it as shipped in seven further places (the ledger row, the disk tree, the backend paragraph, gate resolution, the resume point, Turn(record)'s commit contents, and the Conductor's does-list and intake list). The shipped files carry a plain `backend` file instead — one line naming the backend, written at `on` and reread at `up` — and no gate-verdict log, no run branch record, and no `status: open | closed`. The shipped resume point is three items, not four (conductor SKILL §9, `skills/up/SKILL.md`), and where the existing document says resume "reads the gates' standing from disk instead of guessing", the shipped procedure does the opposite: it re-presents a pending gate when disk cannot distinguish the two states, costing at most one redundant `ty`. The rebuilt document states the shipped behaviour.

Two smaller divergences, also not repeated: the existing document's default paths `docs/ux.md` / `docs/design.md` with a Planning-Gate redirect appear in no shipped file (conductor SKILL §3 says only that missing prerequisites become Plan Steps in aiya's formats, with a conversion Step at the end of Delivery where the project demands its own format); and the existing §5.5 rule that "a Planning-Gate approval dispatches no Turn(record) — its run-state entry becomes durable at the next dispatch point" depends on the run-state file and has no shipped counterpart.

## Decisions I did not carry

Walked section by section through `aiya/docs/design.md`. Each item below is something that document fixes and the rebuilt one does not state.

**From §3.2, §3.3, §4.4, §4.5, §5.5, §5.7 — the run-state file, in full.** Dropped because no shipped file carries it (see the fact-check above); a reader finds the shipped substitute in `aiya/skills/conductor/SKILL.md` §2 and §9. Specifically not carried:

- The filename `state.yaml` and its "(proposed)" status.
- Its ledger row: "Run-state — the run's lifecycle facts, written by the Conductor, verified by nothing because every entry mirrors a command or verdict the human typed, owned by no one."
- Its line in the run directory tree.
- The four fields of its YAML example — `backend:`, `branch: aiya/csv-export`, the `gates:` list of `{gate, verdict, edition}` entries, and `status: open | closed` closed at G3 resolution.
- "The Conductor writes it and no one else does — it is the one party present at every boundary event: at `on`, at each gate verdict, at G3 resolution."
- "Turn(record) carries it into the durable record and never writes into it."
- The backend being "recorded in the run-state file" (the rebuilt document says the `backend` file).
- Gate resolution's "two parties write", and the Conductor writing every gate's verdict — approvals and send-backs alike — into that file, which "is a log, not a ledger anything reads a next version from".
- The run-state file as the fourth item of the resume point, and "the run-state file says where the gates stand — read from disk, not guessed".
- The run-state file inside Turn(record)'s wave-settle and gate-verdict commit contents.
- "A Planning-Gate approval dispatches no Turn(record) — its run-state entry becomes durable at the next dispatch point."
- The run-state file as an item of the Conductor's closed intake list, and "Keep the run-state file current at every boundary event" in its does-list.

**From §4.5 — the machine-loss window.** "One window degrades: a boundary event not yet carried into the durable record is lost with the machine, and a resume then re-presents the pending gate — the safe side: a lost approval costs one redundant `ty`; a lost send-back, giving the feedback again." Not carried as written, because the premise is the run-state file. The rebuilt §4.5 states the shipped ambiguity instead (a Planning Gate approval writes nothing new, so the gate is re-presented, costing at most one redundant `ty`); the "lost send-back means giving the feedback again" case is not stated anywhere and has no shipped counterpart.

**From §3.3 — the UX and Design documents' locations.** `docs/ux.md` and `docs/design.md` as defaults, and their redirection "at the Planning Gate where the project's layout differs". Dropped as unsupported by the shipped files; the rebuilt §3.3 says only that both live with the product rather than under `.aiya/`. Where a reader would look instead: conductor SKILL §3 (prerequisites) and `aiya/references/ux.md`.

**From §4.4 — the pointer "The mechanics ship in the conductor skill and the Turn definitions"** (for version invalidation). Dropped as a navigation aid for an implementer, not a design decision; the mechanics themselves are in conductor SKILL §3.

**From §5.2, §5.3, §5.4, §5.6, §3.3 — the per-file reference links.** `[references/report.md]`, `[references/plan.md]`, the two "Schema and worked example: the Turn definition" pointers, and the two links to `[references/]`. Replaced by one statement in §3.4 naming all seven shipped formats, and by §5's opening line saying schemas and worked examples are not restated in this chapter. A reader looking for a format finds it in `aiya/references/`.

**From §2 — "mnemonics in the README"** for the three session command words. Dropped: it serves the end-user reader, and the mnemonics are in `aiya/README.md`.

**From §5.3 — the placement of the default viewpoints.** "The defaults are the Step's done-when and the relevant criteria of the phase yardstick; the Plan item may declare domain viewpoints beyond them" was moved, not dropped: it is now in §4.1, where the pipeline first needs it, and §5.4 does not repeat it.

**From §4.4 — "Six stops: three phases × {Plan on the way in, product on the way out}".** The arithmetic is dropped as a sentence because the gate diagram directly above it shows all six stops; the fact that only the outputs carry numbers is kept, and the six-gate definition is in §2's vocabulary.

**Carried in substance but not in the existing wording** (listed so the comparison does not read them as losses): "one role, one skill" appears as "one role holding one job" (§3.2); "10× is a rising ceiling, not a static target" appears as "a rising ceiling, not a fixed number" (§2); "git history reads as the run's state machine" appears as "the history reads back as the run's state machine" (§4.2).

**Everything else in the existing document is carried**: both failure modes and both properties and the out-of-scope line (§1); the two roles, both walls, all ten vocabulary entries, the enforcement principle, the model-progress bet, and the mechanism mapping (§2); the two-layer chain, all eight remaining ledger rows, the run directory, the three backends and their two named degradations, and the three shipped artifact kinds (§3); the Step pipeline with its attempt cap, escalation and two side paths, the wave with its single brief and single record, steering's three questions and discretion line and finite verb set and attribution test, the three phases and six gates with versioned approvals and both send-back forms and dispatch rounds, suspend/resume, and the full discharge (§4); all seven parts' promises and breach traces (§5); all three ratios with the uninstrumented counting and the 50% heuristic (§6); all seven rejected shapes and all eight accepted costs (§7).
