Rn version: 0.8.0
Design: writ/docs/design.md

# Goal

Make a document read as if a person wrote it — not an AI — so the reader takes it in with the least
effort. Package this as a Claude Code plugin `writ` (skill `up`, invoked `/writ:up`) so the
procedure can be applied on demand to any draft, by a human or by Claude itself. Primary mode is
brushing up an existing draft; authoring from scratch runs through the same procedure but is
secondary. The verbatim instruction is preserved at `.rn/20260614-writ/instruction.md` as the
source of record, and the skill body is derived from it.

**Purpose (the end):** a human-readable document. Concretely — the reader's cognitive load is low,
it goes in when read top to bottom, and its structure is graspable at a glance through diagrams and
lists.

**Quality, in two tiers:**

- **Floor — table-stakes quality (b):** clearing it earns no praise, but failing it instantly reads
  as "an AI wrote this." Scrub the fingerprints: padding and throat-clearing, restatement, retreat
  into generalities, flavorless connectives, reflexive bulleting, a wavering voice.
- **Ceiling — attractive quality (a):** on a cleared floor, what makes it worth reading — density,
  concreteness (names, numbers, examples), a single load-bearing thread (conclusion first), diagrams
  and lists that earn their place, a consistent voice. Adding ceiling onto an uncleared floor is
  wasted.

The skill **builds both tiers in by construction, then verifies**: it does not edit the input draft
in place (that drags the old wording along and reads as patched) but rebuilds the document fresh
through an ordered writing procedure, so the AI tells never take hold. The floor is a **final net**
for stragglers, not a pre-scrub; the ceiling is what the writing actively builds.

**Means (not the end):** rebuild from intent — take from the input only its content and what it must
convey, define the reader (who they are / what they must decide or do / how they read), then build
the document through ordered writing steps (outline from purpose → fill with the message → check the
story as the reader → decide voice and form → write → brush up → clear the floor), deriving the axis,
voice, and form from the reader and purpose rather than from memory or the old draft.

# Acceptance criteria

Stated as ends — what is true once writ works. The mechanisms that reach them (the ordered steps, the
two layers, the axis skeletons, the length bound) are decisions, and they live in `writ/docs/design.md`:
§4 for what each guarantees and how a breach is caught, §5 for why it was chosen over the
alternatives. A criterion here never names a step number or a section of `SKILL.md` — one that does
has become a means, and belongs in the design notes.

**How these are judged.** Criteria 1–8 are read off a real run's output and its what-changed note, and
the experiential ones (1 and 2) are judged by a fresh-context reader given only the document and the
reader definition, never by the author's own reading. Criterion 9 is judged by installing and
invoking the plugin.

## What a run produces

1. **The reader reaches the purpose.** Given a draft (or a topic) and a reader, the delivered document
   carries that reader to what they must decide or do, read top to bottom.
2. **It reads as a person wrote it, at the least cost to that reader.** No AI tell survives — padding,
   restatement, retreat into generalities, flavorless connectives, reflexive bulleting, a wavering
   voice, hedging. The answer comes first, the headings alone carry the argument, the load-bearing
   claims stand out at a glance, and figures and lists appear only where each beats prose.
3. **One document, one shape.** The output holds a single axis for a single reader. Where the content
   genuinely serves two readers, the run says so and offers the split; if the owner keeps one file,
   each part stands alone — its reader reaches its purpose without crossing into the other.
4. **Voice and shape are derived, not remembered.** The same content under two different reader
   definitions comes back with a different voice and a different axis.
5. **The input's claims survive with their status.** What was proposed stays proposed, a hypothesis
   stays marked, a decision keeps its intent — and nothing is dropped for not being true yet.
6. **Only what the reader needs gets in, and everything they need has somewhere to go.** Content
   serving someone else stays out and is named in the note: whose it is, where it belongs. A need the
   supplied format has no slot for is surfaced with its reader evidence and the place it belongs,
   never buried under the nearest heading.
7. **A defect in the subject is handed back, not smoothed over.** Where the reader trips on the thing
   itself rather than on the writing, the document gains no reconciling clause; the defect ships named
   for whoever owns it.
8. **Nothing ships unread or unexplained.** Delivery ends on a reading, not on an edit, and whatever
   is left unverified or unresolved is named as such. What ships is the rebuilt document plus a
   what-changed note that leads with the substance — structure, story and voice, each tied to the
   reader or the purpose — and closes with the tells the final net caught.

## Reach

9. **It can be applied on demand, by a human or by Claude itself.** `/writ:up` installs from the ccpm
   marketplace, loads and starts the procedure when invoked, and fires unprompted while Claude is
   drafting or revising a document. Evidence: both strict validations pass and a headless invocation
   starts the procedure. The repo rules that keep this true — version in `plugin.json` only,
   marketplace and root README in sync, English artifacts, scenario-style README — are in `# Rules`,
   where compliance is checked as a rule rather than as a criterion.

## Traceability

The three field-feedback rounds are folded into the criteria above instead of standing as their own
mechanism checklists. What each round changed and why is in `design.md` — round 1 in 4.5–4.6 and D-8,
round 2 in 4.7–4.11 and D-10, round 3 in 4.3, 4.5–4.7 and 4.9–4.11 and D-11 — and what was verified at
the time is in `checks/7.md`, `checks/9.md` and `checks/10.md`. The clause-by-clause mapping from the
previous means-based criteria to these ends is in `checks/11.md`.

# Assumptions

- Fact (verified on disk): official skills are model-invocable by default. `rn`'s skills set
  `disable-model-invocation: true` because they are meant for a human to drive; this skill is meant
  for a human or AI.
- Fact (verified): skills are invoked as `/{plugin}:{skill}`. Plugin name and skill name are
  independent slots — they need not relate or match (`rn:gm` is the precedent). So plugin `writ`
  + skill `up` is valid.
- Fact (ccpm rules): version lives only in plugin.json; marketplace.json and root README stay in
  sync; shipped artifacts are English; README is scenario-style.
- Assumption (unverified): the marketplace entry `category` is a free string. Use `"writing"` (the
  existing entry uses `"development"`).
- Assumption (unverified): `claude plugin validate` and `claude -p … --plugin-dir` are available in
  this environment. If not, #3 falls back to manual verification.
- Scope: exactly one plugin `writ` and one skill `up`. How the skill body is laid out — one file, or
  a body plus `references/` — is a design decision, not a scope constraint: `design.md` §5.2 owns it
  and it is free to change without touching this steering.
- Source-of-record exception: `.rn/20260614-writ/instruction.md` stays in its original Japanese —
  it is the user's verbatim instruction, so translating it would corrupt the source. This is the one
  artifact exempt from the English rule.
- Historical-record exception: Tasks #1–#5 below narrate work done under the plugin's original name
  `techting` (renamed to `writ` in task #6) — their Steps/Completion-criteria text keeps the
  `techting` paths as an accurate record of what was done at the time; only forward-looking sections
  (Goal, Acceptance criteria, Assumptions, Rules, task #6 onward) use the current name `writ`.

# Rules

- 1 task = 1 commit
- Shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English,
  including this steering.md
- The version lives only in `writ/.claude-plugin/plugin.json` (no version in marketplace.json)
- On any add / rename / remove, update `.claude-plugin/marketplace.json` and root `README.md` in the
  same commit
- README is scenario + real-console style, not a mechanical list
- The SKILL.md description is written to be model-invocable (no `disable-model-invocation`)
- The skill body is derived from `instruction.md` and must not drop any of the four pillars

# Tasks

### #1: Author the `up` skill (techting/skills/up/SKILL.md)

**Purpose**: Turn the instruction into a single-file "brush up an existing document" skill. This is
the heart of the plugin.

**Prerequisites**: none (instruction.md was saved in the session-start commit)

**Steps**:

- [x] Write the frontmatter: `name: up`, a model-invocable description (fires for a human or Claude
      itself when a document is being written or revised), and no `disable-model-invocation`
- [x] Write the body procedure: reader definition (who / what to decide-or-do / how they read) →
      pick axis and outline (the five axes) → show structure and flow as mermaid → pre-output
      self-check
- [x] State the brush-up frame: input = an existing draft, output = the revised document plus "what
      was changed and why"
- [x] Cross-check against instruction.md item by item so no pillar or point is dropped (do not sample)
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/1.md`)
- [x] QA engineer review (subagent)
- [x] user review

**Completion criteria**:

- `techting/skills/up/SKILL.md` frontmatter has `name: up` and a description, and no
  `disable-model-invocation`
- The body contains all four pillars (reader definition / five-axis outline / mermaid diagrams /
  pre-output self-check)
- The input = existing draft, output = revision + reasons frame is stated in the body

### #2: Package the plugin and register it in the marketplace

**Purpose**: Make techting a standalone plugin and make it reachable from both the ccpm marketplace
and the root README.

**Prerequisites**: #1

**Steps**:

- [x] Create `techting/.claude-plugin/plugin.json` (name `techting`, description, version `0.1.0`,
      author lovaizu)
- [x] Create `techting/README.md` (scenario + real-console style showing `/techting:up`)
- [x] Add a techting entry to `.claude-plugin/marketplace.json` (name / description / source
      `./techting` / category `"writing"`, no version field)
- [x] Add techting to the root `README.md` Plugins list (link to `./techting/README.md` + one-line
      description)
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/2.md`)
- [x] QA engineer review (subagent)
- [x] user review

**Completion criteria**:

- `techting/.claude-plugin/plugin.json` has a version and `marketplace.json` has no version field
- Both `marketplace.json` and root `README.md` contain techting
- The root `README.md` techting entry links to `./techting/README.md`

### #3: Validate strict and verify headless invocation

**Purpose**: Confirm structural validity and real invocation by measurement, and fix whatever fails.

**Prerequisites**: #2

**Steps**:

- [x] Run `claude plugin validate ./techting --strict` and clear every warning/error
- [x] Run `claude plugin validate . --strict` (marketplace root) and clear every warning/error
- [x] Run `claude -p "/techting:up …" --plugin-dir ./techting` and confirm the skill loads and starts
- [x] If the CLI is unavailable, switch to manual verification and record that fact and the result
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/3.md`)
- [x] QA engineer review (subagent)
- [x] user review

**Completion criteria**:

- `claude plugin validate ./techting --strict` and `claude plugin validate . --strict` both pass
- `claude -p … --plugin-dir ./techting` loads and starts the `up` skill (or, if the CLI is absent,
  there is a record of manual verification confirming the equivalent)

### #4: Rebuild SKILL.md from source and correct the acceptance criteria (D-3)

**Purpose**: The shipped `SKILL.md` embodies the category error in D-3 (a mermaid diagram embedded
in the prompt body). Rebuild it from source with the two layers separated, and fix the criteria so
the diagram requirement targets the produced document, not the prompt. Keep the validated packaging.

**Prerequisites**: #1–#3 (packaging stays; only SKILL.md + criteria change). User's go to rebuild.

**Steps**:

- [x] Rewrite `techting/skills/up/SKILL.md` from `.rn/20260614-writ/instruction.md`, fresh — do not patch
      the old file. Frontmatter: third-person description with brush-up-first trigger phrases,
      model-invocable, version. Body in imperative form, lean (<2,000 words), single file.
- [x] Separate the two layers in the body: process (model instructions) vs output rules (constraints
      on the produced document). Put the mermaid rule only in output rules, with an explicit
      addressee sentence. No mermaid diagram embedded in the prompt body.
- [x] Carry every source pillar (reader definition + ask-or-infer gate, base/house-style, the five
      axes with no-mixing, voice-by-reader, pre-output self-check) — cross-check item by item.
- [x] Add the missing self-check item "each document is a single axis (not mixed)" (Expert C's one
      fidelity gap). Optionally wire derivation: "how-they-read → axis", "table is an example, §1 is
      the source of truth".
- [x] Replace the old mermaid acceptance criterion with the corrected Level A / Level B criteria
      from D-3.
- [x] Add `techting/CHANGELOG.md` (Keep a Changelog; `## [Unreleased]` Added line — not a dated
      `## [0.1.0]`, since no release instruction has been given; promotes on release).
- [x] Re-validate: `claude plugin validate ./techting --strict` and `. --strict`; dogfood with two
      different reader definitions to confirm Level B (voice/axis change).
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/4.md`)
- [x] QA expert review (subagent)
- [x] Craft expert review (subagent, writing)
- [x] Verification expert review (subagent, fact-check)
- [x] Design expert review (subagent)

**Completion criteria**:

- `SKILL.md` body separates process from output rules, contains no embedded mermaid diagram, and
  carries an addressee sentence on the diagram rule.
- All source pillars present; the self-check includes the single-axis (no-mixing) item.
- The steering acceptance criteria use the Level A / Level B split from D-3.
- `CHANGELOG.md` exists; both strict validations pass; the two-reader dogfood shows voice/axis change.
  (dogfood deferred to the session's Level B acceptance run, per `checks/4.md`)

### #5: Add the floor (table-stakes) layer and the floor→ceiling order to SKILL.md

**Purpose**: The rebuilt `SKILL.md` (#4) carries reader-first derivation but not the **floor** — the
pass that removes AI tells — nor the **floor-then-ceiling order** the revised Goal now requires. Add
both so the skill clears the floor before it reaches for the ceiling. Without this, the skill can add
polish onto text that still reads as AI-written, which the Goal forbids.

**Prerequisites**: #4 (the process / output-rules split stands; this extends it, it does not rebuild
it). The Goal reframing (two-tier quality) and the revised acceptance criteria are the source.

**Steps**:

- [x] Add a **floor pass** to the process: first inspect the draft for AI tells and remove them,
      before any derivation. Name the floor checklist (padding / throat-clearing, restatement,
      retreat into generalities, flavorless connectives, reflexive bulleting, a wavering voice).
      Done: new step 2 "Clear the floor"; checklist runs to **seven** (hedging added in the fix round).
- [x] Make the procedure order **explicit**: floor (remove AI tells) → ceiling (derive and add the
      attractive qualities). State that adding ceiling onto an uncleared floor is wasted.
- [x] In §output-rules, state **both tiers**: floor (b) = none of the named AI tells; ceiling (a) =
      density, concreteness, single load-bearing thread, earned diagrams/lists, consistent voice.
- [x] Make the "what was changed and why" report **separate floor fixes from ceiling lifts**, in
      that order.
- [x] Cross-check the result against the revised Goal and acceptance criteria item by item (do not
      sample); keep the body lean (<2,000 words) and the addressee sentence intact. Done: 1,900 words.
- [x] Re-validate: `claude plugin validate ./techting --strict` and `. --strict` — both pass (Level A).
      **Level B dogfood — done 2026-07-07**: ran `up` on a throwaway draft through two contrasting
      reader definitions (see `checks/5.md`) — different axis and voice each time, mermaid rendered
      when branching genuinely warranted it and skipped when a sentence carried the structure just as
      fast, single axis held, floor clean in both runs.
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/5.md`)
- [x] QA expert review (subagent) — re-review PASS after one fix round (6-vs-7 floor mismatch fixed)
- [x] Craft expert review (subagent, writing)
- [x] Verification expert review (subagent, fact-check)
- [x] Design expert review (subagent)

**Completion criteria**:

- `SKILL.md` process instructs the floor-scrub **before** any derivation and names the AI-tell
  checklist; the floor→ceiling order is explicit.
- §output-rules states both tiers and keeps the addressee sentence; the body stays <2,000 words.
- The acceptance-criteria floor items (Level A and Level B) are all satisfied; both strict
  validations pass; the dogfood shows the AI tells removed and the report split into floor then
  ceiling.

### #6: Rename the plugin `techting` → `writ` (skill stays `up`) and drop the "technical document" framing

**Purpose**: The design content was never actually technical-writing-specific — the reader definition,
five axes (sourced from Diátaxis/MADR/ADR guidance, D-6), and floor/ceiling AI-tell scrub apply to any
document a person writes. Only the naming and framing narrowed it: plugin name `techting`, the title
"technical writing, up a level", and "brush a **technical** document up" wording in `SKILL.md`,
`plugin.json`, `CHANGELOG.md`, root `README.md`, and the marketplace entry. Rename the plugin to `writ`
so `/writ:up` reads as "write it up" with no redundant "up up", and reword every "technical
document"/"technical writing" occurrence to plain "document"/"writing" so the shipped artifacts match
what the skill actually does.

**Prerequisites**: #1–#5 (the packaging and SKILL.md content stand; this is a rename + rewording pass,
not a rebuild).

**Steps**:

- [x] `git mv techting writ` (directory rename, preserves history)
- [x] `writ/.claude-plugin/plugin.json`: `name` → `writ`; description drops "technical-writing" →
      "reader-first document brush-up"
- [x] `writ/skills/up/SKILL.md`: frontmatter description and H1 drop "technical document" → "document";
      confirm no other "technical" wording remains in the body (Reference section already generic)
- [x] `writ/README.md`: title, intro, install command (`writ@ccpm`), and invocation examples
      (`/writ:up`) updated; drop "technical" from the title/intro line
- [x] `writ/CHANGELOG.md`: reword the `[Unreleased]` entries' "technical document" → "document"
      (still unreleased, no need to preserve old wording as history)
- [x] `writ/docs/design.md`: rename references to `writ`/`/writ:up` throughout; add **(D-7) Renamed
      `techting` → `writ`, skill stays `up`** documenting that the content was general-purpose from
      the start (D-6's sourcing already proves this) and only the name/framing lagged
- [x] `.claude-plugin/marketplace.json`: `name` → `writ`, `source` → `./writ`, description reworded
      (drop "technical-writing")
- [x] Root `README.md` Plugins list: link → `./writ/README.md`, entry text drops "Technical writing, up
      a level" → a general document-brush-up description
- [x] Re-validate: `claude plugin validate ./writ --strict` and `claude plugin validate . --strict`
- [x] Update PR #5's title and description to drop "technical-writing" framing and reflect the new
      plugin name (QA also caught stale session-dir links in the body — `.rn/techting/...` → 404 —
      fixed to `.rn/20260614-writ/...`)
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/6.md`)
- [x] QA expert review (subagent)
- [x] Craft expert review (subagent, writing)
- [x] Verification expert review (subagent, fact-check)

**Completion criteria**:

- No file under `writ/`, `.claude-plugin/marketplace.json`, or root `README.md` contains "techting" or
  "technical document"/"technical writing" in a scope-narrowing sense
- `/writ:up` is the invocation shown everywhere (README, root README, plugin descriptions)
- `claude plugin validate ./writ --strict` and `claude plugin validate . --strict` both pass
- `design.md` records the rename decision (D-7) and its rationale
- PR #5 title/description reflect the new name and general-document framing

### #7: Encode the PR #15 field feedback — reader as content gate, verification independence

**Purpose**: A real run (PR #15 comment 5353396410) produced a document its owner judged
noise-ridden while every writ check passed. Root cause: the step-2 reader governs only form (axis,
voice), not **content admission** — sentences and slots serving other readers (re-reader, past
reviewer, approver) pass through — and the experiential checks are run by the author, whom the
curse of knowledge blinds. Build both properties into the construction instead of adding nets:
the reader becomes the admission filter for content (dissolves Findings 1 and 3), and experiential
verification moves to a fresh-context subagent (dissolves Finding 2). Finding 4 resolves as a
consequence: the ceiling's target is minimal reader effort; density is a means.

**Prerequisites**: #6. The user approved the two-structural-change proposal (2026-08-20).

**Steps**:

- [x] Steps 3–4 of `SKILL.md`: make the step-2 reader the **admission criterion for content** — a
      heading or point enters only if that reader needs it to reach the purpose; content serving
      another reader stays out and is reported in the what-changed note (whose it is, where it
      belongs). External-template slots pass the same test; an unjustifiable slot is reported to
      the user as an axis-side conflict (headless: recorded in the what-changed note), never
      silently filled.
- [x] Split step 10: mechanical checks (single axis, `Assumed reader:` line, claim statuses) stay
      with the author; **experiential checks** (reaches the purpose top to bottom, headings carry
      the argument) move to a fresh-context subagent given **only** the document and the step-2
      reader definition, reporting where it stumbled; its pass gates delivery, and stumbles come
      back as fixes.
- [x] Reference: restate the ceiling around **minimal reader effort to the purpose** — density
      becomes a means; add "the few load-bearing claims are distinguishable at a glance"; leave
      the one-voice rule and the seven-tell floor table unchanged.
- [x] Keep the body <2,000 words by trimming existing text (no relaxing the budget); keep the
      addressee sentence; update `writ/CHANGELOG.md` `[Unreleased]`.
- [x] Dogfood against the field evidence: run the new fresh-reader check on the aiya document
      (`486a1af:aiya/docs/design.md`, reader definition from
      `486a1af:.rn/20260813-aiya/checks/4-writ-note.md`) — it must flag the three noise spots the
      FB named (opening abstract, §1 "Out of scope" — a paragraph, so caught at point level via
      the trial's content-not-needed report — and the §2 provenance opener); run the
      slot-justification test over the heading structure for the heading-level admission.
- [x] Re-validate: `claude plugin validate ./writ --strict` and `claude plugin validate . --strict`.
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/7.md`)
- [x] QA expert review (subagent)
- [x] Craft expert review (subagent, writing)
- [x] Verification expert review (subagent, fact-check)
- [x] Design expert review (subagent)

**Completion criteria**:

- `SKILL.md` admits content solely through the step-2 reader's path to the purpose, at both heading
  and point level, with routed-out content reported in the what-changed note and unjustifiable
  external slots escalated, not filled.
- Experiential self-check items run in a fresh-context subagent (document + reader definition only)
  whose pass gates delivery; mechanical items remain self-checked.
- The ceiling names minimal reader effort as the target, density as a means, and load-bearing
  claims distinguishable at a glance; one voice and the seven-tell floor stand unchanged.
- Body <2,000 words; addressee sentence intact; both strict validations pass; CHANGELOG updated.
- The dogfood flags the FB's three named noise spots ("Out of scope" at point level — it is a
  paragraph, not a heading).

### #8: Evaluation sign-off

**Purpose**: Close the session through the Evaluation gate — run the steering Acceptance criteria
end to end and take the user's verdict. Fills the planning gap noted at suspend ("Evaluation
sign-off gap open"): the original plan had no Evaluation sign-off task, which the rn workflow
requires for a session to close.

**Prerequisites**: #7, then #9, #10 and #11 — the FB round-2 and round-3 work, and the rewrite of the
criteria into ends, all landed after the first criteria run, so the run is re-done against the current
criteria before the verdict is taken.

**Steps**:

- [x] Run every Acceptance criteria item against the shipped artifacts and record the result per
      item
- [ ] Present the run result to the user (on PR #15, per push-and-review) and take the verdict via
      `/rn:ty` or `/rn:gm`

**Completion criteria**:

- Every acceptance criterion has a recorded pass, or the user has explicitly accepted the exception
- The user's `/rn:ty` verdict is recorded

### #9: Encode the PR #15 round-2 field feedback — mechanisms for the standing instructions, and a legal composite

**Purpose**: A controlled experiment (PR #15 comment 5469096123) rebuilt a real design document from
a blank page with `/writ:up` and judged it against the hand-patched original with two fresh readers
under an identical prompt. The rebuild won — both QUALIFIED, effort 3 vs 4, better headings-only pass
— so the procedure works; the six findings are about where it got there *despite* writ. Five are
taken. Three of them share one shape: an instruction standing where a mechanism belongs ("build
fresh", "fix every stumble", "a clean pass gates delivery"), each measurably unenforced — 127 shared
8-token spans with the source, a reconciling clause that became the next reader's own stumble, a gate
that has never once opened. The other two are about reading the input honestly: its claims have
statuses writ never asked for (a pending proposal was deleted for not being built yet), and its shape
may legitimately serve two readers, which step 3 forbade while offering no alternative.

**Prerequisites**: #7 (the reader-as-content-gate and the fresh-reader trial stand; this backs them
with mechanisms rather than replacing them).

**Steps**:

- [x] Step 1 of `SKILL.md`: sort the input's assertions by status (in force / proposed / hypothesis),
      emit the proposed ones, and bar dropping a point because reality has not caught up — content
      leaves only through the step-3 admission. §Reference: a decision not yet in force says so.
- [x] Make "build fresh" a mechanism: step 4 bullets in the writer's own words, step 7 closes the
      input (outline is the only source from rendering on), step 10 gains a side-by-side carryover
      check.
- [x] Step 11: sort each stumble into prose defect (fix) and subject defect (named for the subject's
      owner, left standing or struck, never patched).
- [x] Give the gate a termination: delivery gated on no prose defect remaining, subject defects ship
      named, loop stops after three trial rounds with any survivor named.
- [x] Step 3: a two-axis document is two documents — offer the split first; where the owner keeps one
      file, declare the parts (own reader line and axis each, admissions and the step-11 trial per
      part, no blending inside a part). Step 10's axis item accepts exactly that shape.
- [x] Decline the length measure and record why (D-10): the document that grew 27% is the one that
      read easier, the reader trial already discriminates, and a ratio with no bar competes with the
      real target.
- [x] Realign `writ/README.md` and `writ/docs/design.md` (4.7–4.11, D-10, §3.2 table, §3.3 diagram,
      4.3 and 4.6 cross-references) with the shipped skill.
- [x] Re-validate: `claude plugin validate ./writ --strict` and `claude plugin validate . --strict`.
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/9.md`)
- [ ] user review (on PR #15, per push-and-review)

**Completion criteria**:

- Every clause of the FB-round-2 acceptance criterion above is present in `SKILL.md`.
- `README.md` and `design.md` describe the shipped behavior — no "waits until that reader gets
  through clean", no unqualified "won't mix roles".
- Both strict validations pass; the body stays under the official 500-line bound and inside
  1,000–3,000 words.
- The declined finding is recorded with its reasoning in `design.md` (D-10).

### #10: Encode the round-3 field feedback — an admission test that can add, and checks moved to where failure is cheap

**Purpose**: The round-2 re-run (`worktree-aiya:.rn/20260813-aiya/writ-feedback-3.md`) is the first
honest head-to-head writ has had — task #9's carryover mechanism failed the rebuild's first render at
70.87% shared text and forced a rebuild from meaning, which also retired round 1's effort-3 "win" as
a measurement of the source rather than of the procedure. Honest, the comparison is a **tie**: both
documents QUALIFIED, both effort 4, the rebuild 43% longer. The finding the tie is about: four fresh
readers, two rounds, two independently written documents prescribed the same change in near-identical
words — put the answer at the front — and writ detected it every time without being able to act,
because step 3's slot-by-slot test can only return removal. Five smaller findings put existing checks
one step away from where their failure is cheap or visible.

**Prerequisites**: #9 (this extends the admission gate, the carryover mechanism, the stumble triage,
the trial loop, and the declared composite that #7 and #9 built).

**Steps**:

- [x] Step 3: run the admission test both ways — reader → slot alongside slot → reader; an unslotted
      need becomes a proposed slot with its position and reader evidence; a slot that defers the thing
      elsewhere does not carry it. Step 10's admission item restated in both directions.
- [x] Step 11: add **format defect** as a third stumble class, routed to step 3's proposed slot; an
      unruled proposed slot ships named rather than blocking delivery.
- [x] Five axes: the article skeleton leads with the answer, its closing is not a recap; the other
      four re-checked against the ceiling.
- [x] Step 5: read the filled outline against the input, where a carryover failure costs one re-fill;
      step 10's side-by-side stays as the backstop.
- [x] Step 11: the reader's stumble question asks what read as machine-written (a sentence already
      read, a figure that disagrees with the prose).
- [x] Step 11: end on a trial, never on an edit — a post-cap fix gets a changed-passages-only read,
      and whatever is unconfirmed ships named as unverified.
- [x] Step 10: record produced-vs-input size and argue the growth (no bar). D-10 reopened as
      record-and-argue with the round-2 evidence (+43% for no gain).
- [x] Step 3: a declared composite is walked part by part at step 5; a part that cannot reach its
      purpose without the other is the split answer.
- [x] Realign `writ/docs/design.md` (4.3, 4.5, 4.6, 4.7, 4.9, 4.10, 4.11, D-10, D-11, §5.2) and
      `writ/README.md` with the shipped skill.
- [x] Re-validate: `claude plugin validate ./writ --strict` and `claude plugin validate . --strict`.
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/10.md`)
- [ ] user review (on PR #15, per push-and-review)

**Completion criteria**:

- Every clause of the FB-round-3 acceptance criterion above is present in `SKILL.md`.
- `README.md` and `design.md` describe the shipped behavior, including the additive direction of the
  admission test and the reopened length measure.
- Both strict validations pass; the body stays under 500 lines and inside 1,000–3,000 words.

### #11: Restate the acceptance criteria as ends, and move the means to the design notes

**Purpose**: The criteria had accreted implementation. Of sixteen items, ten described how `SKILL.md`
is built — a physically separated `## Reference` section, a 1,000–3,000 word body, no mermaid in the
prompt, and three field-feedback rounds written as step-numbered mechanism checklists — rather than
what writ achieves. Means in the criteria have a cost: any change to the skill's construction fails
the criteria and forces them to be rewritten, so the shape of the prompt is frozen by the document
that was supposed to judge its results. Criteria state the end; `design.md` holds the intent and the
decisions; the implementation follows the decisions.

**Prerequisites**: #10 (round 3 is the last content folded in).

**Steps**:

- [x] Rewrite `# Acceptance criteria` as nine ends — eight on what a run produces, one on reach —
      naming no step number and no section of `SKILL.md`, with the judging method stated up front.
- [x] Fold the three FB rounds into those ends and point traceability at `design.md` and the
      `checks/` files instead of restating their mechanisms.
- [x] Drop the repo-rule items (version placement, marketplace/README sync, English artifacts,
      README style) from the criteria — `# Rules` already governs them.
- [x] Realign `design.md`: 4.1's breach-catch no longer cites a criterion that no longer exists, and
      D-12 records this decision and its cost.
- [x] Map every clause of the previous sixteen criteria to its new home, so nothing is lost
      (`checks/11.md`).
- [ ] user review (on PR #15, per push-and-review)

**Completion criteria**:

- No criterion names a step number, a `SKILL.md` section, or a length bound.
- Every clause of the previous criteria is either restated as an end or located in `design.md` /
  `# Rules`, with the mapping recorded.
- `design.md` carries the decision (D-12) and no longer points at a deleted criterion.

# State

- **Status**: in progress
- **Date**: 2026-09-01
- **Last completed**: #11 restate the acceptance criteria as ends (PR review outstanding)
- **Next**: #8 evaluation sign-off — run the nine end-based criteria against a real run, then take
  the verdict. This needs a live `/writ:up` run to judge criteria 1–8; the earlier runs were
  inspections of the prompt.
- **Notes**: Branch `worktree-writ`, PR #15 open; #9's review is also outstanding. The earlier
  criteria run (`checks/8.md`, 13/13) predates the three sign-off fixes, task #9 and task #10, so it
  is re-run before the verdict. Two questions for the sign-off: (a) acceptance criterion 9 tests only
  marketplace/README sync, not README-vs-implementation agreement — add that criterion or accept the
  gap — note that #11 removed the length and structure criteria, so (a) is now about whether README
  agreement is an end worth stating at all; (b) the body is at 2,994 words against the official 1,000–3,000 band, so the next addition has
  to be paid for by a trim or by splitting §Reference into `references/` (§5.2 records this; the
  split reverses the single-file scope assumption). The aiya side rebuilds against this version and
  judges the result on its own merits.
