# Goal

Make a document read as if a person wrote it — not an AI — so the reader takes it in with the least
effort. Package this as a Claude Code plugin `techting` (skill `up`, invoked `/techting:up`) so the
procedure can be applied on demand to any draft, by a human or by Claude itself. Primary mode is
brushing up an existing draft; authoring from scratch runs through the same procedure but is
secondary. The verbatim instruction is preserved at `.rn/techting/instruction.md` as the source of
record, and the skill body is derived from it.

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

- **Level A — the `SKILL.md` artifact (the prompt itself):** `techting/skills/up/SKILL.md` exists
  and carries all source intent — reader definition (who / what they must decide-or-do / how they
  read), the five outline axes (article, guide, reference, record-ADR, evaluation), and a pre-output
  self-check. The body separates two layers: **process** (instructions to the model running the
  skill) from **output rules** (constraints on the produced document), with the §output-rules layer
  carrying an explicit addressee sentence stating its rules target the produced document, not this
  prompt. The body is imperative and lean (<2,000 words). **No mermaid diagram is embedded in the
  prompt body** (and none is required by these criteria) — the mermaid rule lives only in
  §output-rules as a directive to the produced document.
- **Level A — the two-tier quality is encoded:** the process is an **ordered writing procedure that
  builds the document fresh from the input's intent** (rather than editing the draft in place), so
  the AI tells do not take hold; the floor scrub is the **final net** (name / quote / fix the seven
  tells) after the writing, not a pre-edit of the draft. The process names the floor checklist
  (padding / throat-clearing, restatement, retreat into generalities, flavorless connectives,
  reflexive bulleting, a wavering voice, hedging). The §output-rules layer states **both tiers**:
  floor (b) = none of those AI tells present; ceiling (a) = density, concreteness (names / numbers /
  examples), a single load-bearing thread (conclusion first), diagrams and lists that earn their
  place, a consistent voice.
- **Level B — the document the skill produces (dogfood-verified):** running `up` on a draft yields
  output whose structure/flow is shown as mermaid wherever there is order or branching, with no
  diagram/prose duplication; feeding two different reader definitions changes the output's voice and
  axis (proving the procedure derives, not memorizes); each produced document holds a single axis,
  not mixed.
- **Level B — the floor is clear in the rebuilt document:** the produced document carries none of
  the named AI tells, and the "what was changed and why" report leads with the **substance** (the
  structure, story, and voice built, each tied to the reader or purpose) and closes with a short line
  on any **AI tells the final-net step caught**.
- The skill states the brush-up use case explicitly: input = an existing draft (read for intent, not
  reused verbatim), output = the rebuilt document plus "what was changed and why" (substance first,
  then the tells the net caught).
- The SKILL.md frontmatter is model-invocable (no `disable-model-invocation`) and its description is
  written so it can fire for a human or for Claude itself.
- `techting/.claude-plugin/plugin.json` has name, description, version (semver), and author, and the
  version lives only in plugin.json (no version field in marketplace.json).
- `techting/README.md` exists and shows how to use `/techting:up` in a scenario + real-console style.
- `.claude-plugin/marketplace.json` has a techting entry (name / description / source `./techting` /
  category) and the root `README.md` Plugins list also links to techting (the two stay in sync).
- `claude plugin validate ./techting --strict` and `claude plugin validate . --strict` both pass.
- `claude -p "/techting:up …" --plugin-dir ./techting` loads the skill and starts the brush-up
  procedure, confirmed headlessly.
- All shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English.

# Assumptions

- Fact (verified on disk): official skills are model-invocable by default. `rn`'s skills set
  `disable-model-invocation: true` because they are meant for a human to drive; this skill is meant
  for a human or AI.
- Fact (verified): skills are invoked as `/{plugin}:{skill}`. Plugin name and skill name are
  independent slots — they need not relate or match (`rn:gm` is the precedent). So plugin `techting`
  + skill `up` is valid.
- Fact (ccpm rules): version lives only in plugin.json; marketplace.json and root README stay in
  sync; shipped artifacts are English; README is scenario-style.
- Assumption (unverified): the marketplace entry `category` is a free string. Use `"writing"` (the
  existing entry uses `"development"`).
- Assumption (unverified): `claude plugin validate` and `claude -p … --plugin-dir` are available in
  this environment. If not, #3 falls back to manual verification.
- Scope: exactly one plugin `techting` and one skill `up`. The procedure lives inline in SKILL.md;
  it is not split into separate reference files (rn uses references, but this skill is self-contained
  in one file).
- Source-of-record exception: `.rn/techting/instruction.md` stays in its original Japanese — it is
  the user's verbatim instruction, so translating it would corrupt the source. This is the one
  artifact exempt from the English rule.

# Rules

- 1 task = 1 commit
- Shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English,
  including this steering.md
- The version lives only in `techting/.claude-plugin/plugin.json` (no version in marketplace.json)
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
- [x] self-check (record OK/NG per criterion in `.rn/techting/checks/1.md`)
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
- [x] self-check (record OK/NG per criterion in `.rn/techting/checks/2.md`)
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
- [x] self-check (record OK/NG per criterion in `.rn/techting/checks/3.md`)
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

- [x] Rewrite `techting/skills/up/SKILL.md` from `.rn/techting/instruction.md`, fresh — do not patch
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
- [x] self-check (record OK/NG per criterion in `.rn/techting/checks/4.md`)
- [x] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**:

- `SKILL.md` body separates process from output rules, contains no embedded mermaid diagram, and
  carries an addressee sentence on the diagram rule.
- All source pillars present; the self-check includes the single-axis (no-mixing) item.
- The steering acceptance criteria use the Level A / Level B split from D-3.
- `CHANGELOG.md` exists; both strict validations pass; the two-reader dogfood shows voice/axis change.

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
- [ ] Re-validate: `claude plugin validate ./techting --strict` and `. --strict` — **done, both
      pass** (Level A). **Level B dogfood (run the skill on a real draft) NOT yet done** — deferred
      to the Acceptance-criteria run, since Level B is a goal-level gate, not a step #5 can finish in
      isolation. This box stays open until that dogfood runs.
- [x] self-check (record OK/NG per criterion in `.rn/techting/checks/5.md`)
- [x] QA engineer review (subagent) — re-review PASS after one fix round (6-vs-7 floor mismatch fixed)
- [ ] user review (on the PR)

**Completion criteria**:

- `SKILL.md` process instructs the floor-scrub **before** any derivation and names the AI-tell
  checklist; the floor→ceiling order is explicit.
- §output-rules states both tiers and keeps the addressee sentence; the body stays <2,000 words.
- The acceptance-criteria floor items (Level A and Level B) are all satisfied; both strict
  validations pass; the dogfood shows the AI tells removed and the report split into floor then
  ceiling.


## D-1: Plugin `techting` / skill `up` (not the same name)
- **Issue**: For a single-skill plugin, how to name the plugin vs the skill. The official convention
  is to use the same name for both.
- **Conclusion**: Plugin `techting` (technical writing), skill `up`. Invoked `/techting:up`.
- **Rationale**: The skill name is typed often, so keep it short. Plugin name and skill name are
  independent slots and need not match (`rn:gm` is the precedent). Brushing an existing draft up a
  level is the primary mode, so the verb `up` fits the content.
- **Evidence**: Official single-skill plugins mostly use the same name (`frontend-design` etc.), but
  `rn` works fine with unrelated short names (`gm/bb/hi`). Skill invocation form is `/{plugin}:{skill}`.
- **Sources**: `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/*`, this repo's
  `rn/skills/*`, the Skill tool spec.

## D-2: Make it model-invocable (the opposite of rn)
- **Issue**: Whether to set `disable-model-invocation: true` on the skill.
- **Conclusion**: Do not set it (let it fire for a human or for Claude itself).
- **Rationale**: The distinguishing axis is not side effects but who the skill is meant for. This
  skill is meant for a human or an AI.
- **Evidence**: `rn`'s skills are meant for a human and set `disable-model-invocation: true`.
  Official skills are model-invocable by default.
- **Sources**: this repo's `rn/skills/*/SKILL.md`, the official plugins.

## D-3: The category error — output-document rules vs the prompt's own format (overturns the old SKILL.md)
- **Issue**: The acceptance criterion read "its body covers ... structure-and-flow shown as mermaid
  diagrams", which made *the SKILL.md prompt itself* required to contain a mermaid diagram. The old
  SKILL.md duly embedded a procedure flowchart. The user flagged this as a category error.
- **Conclusion**: The instruction's "render structure/flow as mermaid" is a rule for the **document
  the writer produces**, not a property of the SKILL.md prompt. The skill body must NOT embed a
  diagram. Two layers must be physically separated in the body: (a) **process** = instructions to
  the model running the skill (define reader, ask-or-infer, self-check); (b) **output rules** =
  constraints on the produced document (md, dry, mermaid-for-structure, voice-by-reader, the five
  axes). The mermaid rule belongs only to layer (b).
- **Decision on scope**: Do NOT delete the whole plugin. The packaging (plugin.json, marketplace
  entry, root README) is sound and validated (Expert B). The intent mapping was audited faithful
  (Expert C: 0 drops). Only the one file that embodies the misunderstanding — `SKILL.md` — is
  rebuilt from source. Rebuilding the 82-line source is cheaper than patching a base we didn't fully
  understand, and yields a base we can stand behind line by line.
- **Best-practice basis (grounded, not asserted)**: official `skill-development` guide at
  `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/skill-development/SKILL.md`.
  Binding rules for techting: third-person `description` with concrete trigger phrases; body in
  imperative form (no second person); lean 1,500–2,000 words; progressive disclosure with NO
  duplication across files. skill-creator notes writing/subjective skills don't need evals.
- **Structure decision**: single `SKILL.md`, no `references/`. The source is ~650 chars; the body
  stays under 2,000 words, and "define reader → pick axis → derive → self-check" is one continuous
  procedure — splitting the five axes into references would force cross-file reads mid-procedure.
  Split later only if an axis grows heavy.
- **Corrected acceptance criteria (replace the old mermaid criterion during #4)**: split into two
  levels. **Level A — the SKILL.md artifact**: frontmatter name/description(third-person triggers,
  brush-up first)/version; model-invocable; imperative & lean; all source intent present; **no
  mermaid diagram embedded in the prompt body or in the criteria**; §output-rules carries an
  explicit addressee sentence ("this is an instruction to the produced document, not to this
  prompt"). **Level B — the document the skill produces (dogfood-verified)**: structure/flow shown
  as mermaid where there is order/branching with no diagram/prose duplication; feeding two different
  reader definitions changes the output's voice and axis (proves derivation, not memorization);
  single axis, no mixing. Every diagram criterion's subject is "the produced document".
- **Sources**: official skill-development guide (path above); `.rn/techting/instruction.md` (source
  of record); three expert subagent reports captured in this session.

## D-4: Purpose reframed — human-readable end, two-tier quality (floor / ceiling)
- **Issue**: The old Goal framed techting as "a reader-first procedure." The user reframed the
  **purpose**: the end is a document that reads as if a person wrote it (not an AI), taken in with
  the least reader effort. The reader-first procedure is the *means*, not the end.
- **Conclusion**: Purpose = a human-readable document. Quality is **two tiers**: **floor (b) =
  table-stakes** — clearing it earns no praise, but failing it instantly reads as AI-written, so the
  skill must scrub the AI tells (padding / throat-clearing, restatement, retreat into generalities,
  flavorless connectives, reflexive bulleting, a wavering voice); **ceiling (a) = attractive** —
  density, concreteness, a single load-bearing thread, earned figures, a consistent voice. The skill
  works **floor-then-ceiling**: adding ceiling onto an uncleared floor is wasted.
- **Why two tiers, in the user's words**: (a) is 魅力 (the charm that earns praise), (b) is 当たり前
  (table-stakes whose absence reads as AI). A human document needs both, in order.
- **Scope note (important)**: the floor (b) **extends beyond `instruction.md`**. The verbatim source
  covers reader-first + tone / diagrams / closing / outline, not an AI-tell scrub. Floor (b) is a
  deliberate session-level expansion of the goal, recorded here; `instruction.md` stays verbatim and
  is no longer the *sole* source — this Decision and the revised Goal are the source for the floor.
- **Consequence**: task #4 (the process / output-rules split, no embedded mermaid) still stands; it
  is necessary but no longer sufficient. Task **#5** adds the floor layer and the floor→ceiling order
  on top of it. Both are reviewed together on PR #5.
- **Sources**: this session's exchange (2026-06-26); the revised Goal and acceptance criteria above.

## D-5: SKILL.md reshaped — build fresh from intent, floor as a net (supersedes the edit-the-draft runbook)
- **Issue**: The runbook form of `SKILL.md` (#5, `reader → floor → axis → voice → restructure →
  deliver`) was structured to **edit the input draft in place** — step 2 scrubbed the draft, step 5
  reordered it. The user flagged two faults: (a) editing in place drags the old wording along and
  reads as patched (継ぎ足し); (b) it is a checklist, not a **writing procedure** — following it does
  not itself produce the document.
- **Conclusion**: Rebuild the document **fresh from the input's intent**, through an ordered writing
  procedure, so the AI tells never take hold. The floor scrub moves from a pre-edit to a **final net**
  for stragglers. The procedure is: understand the input → define reader & purpose → outline from the
  purpose → fill the outline with the message as bullets → read as the reader and check the story →
  decide voice & form from purpose+story → write it out → brush up to the ceiling → clear the floor
  (net) → self-check & deliver.
- **Key reorders from the runbook**: floor goes last (was 2nd); voice & **form** (prose / list /
  table / diagram / graph) is decided **after** the story stands (was an early step), derived from
  purpose+story — this dissolves reflexive bulleting (form is chosen deliberately) and folds in the
  mermaid rule as "diagram where structure/branching lives". Quality is **built in during writing**,
  not scrubbed on after ([[build-quality-in]]).
- **What stays**: the two-layer split (process vs §Reference/output-rules) and the addressee sentence
  (D-3); no embedded mermaid; the five axes, voice table, and seven tells (reused as reference the
  steps point to, reordered into work-order, not deleted); lean (<2,000 words; the rebuilt file is
  ~1,631).
- **Consequence**: the Goal's "first clear the floor, then reach for the ceiling" wording and the
  acceptance criteria that mandated a floor pre-scrub and a "floor-fixes-then-ceiling-lifts" note are
  revised above to "build in, then net" and "substance first, then the tells the net caught".
- **Sources**: this session's exchange (2026-06-27); the rebuilt `techting/skills/up/SKILL.md`.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
