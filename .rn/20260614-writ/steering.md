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

- **Level A — the `SKILL.md` artifact (the prompt itself):** `writ/skills/up/SKILL.md` exists
  and carries all source intent — reader definition (who / what they must decide-or-do / how they
  read), the five outline axes (article, guide, reference, record-ADR, evaluation), and a pre-output
  self-check. The body separates two layers: **process** (instructions to the model running the
  skill) from **output rules** (constraints on the produced document; "§output-rules" here names the
  layer realized as the file's `## Reference` section — D-5), with the §output-rules layer
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
- `writ/.claude-plugin/plugin.json` has name, description, version (semver), and author, and the
  version lives only in plugin.json (no version field in marketplace.json).
- `writ/README.md` exists and shows how to use `/writ:up` in a scenario + real-console style.
- `.claude-plugin/marketplace.json` has a writ entry (name / description / source `./writ` /
  category) and the root `README.md` Plugins list also links to writ (the two stay in sync).
- `claude plugin validate ./writ --strict` and `claude plugin validate . --strict` both pass.
- `claude -p "/writ:up …" --plugin-dir ./writ` loads the skill and starts the brush-up
  procedure, confirmed headlessly.
- All shipped artifacts (plugin.json / SKILL.md / README / commit messages / PR) are in English.

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
- Scope: exactly one plugin `writ` and one skill `up`. The procedure lives inline in SKILL.md;
  it is not split into separate reference files (rn uses references, but this skill is self-contained
  in one file).
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
- [x] self-check (record OK/NG per criterion in `.rn/20260614-writ/checks/5.md`)
- [x] QA engineer review (subagent) — re-review PASS after one fix round (6-vs-7 floor mismatch fixed)
- [ ] user review (on the PR)

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
- [x] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**:

- No file under `writ/`, `.claude-plugin/marketplace.json`, or root `README.md` contains "techting" or
  "technical document"/"technical writing" in a scope-narrowing sense
- `/writ:up` is the invocation shown everywhere (README, root README, plugin descriptions)
- `claude plugin validate ./writ --strict` and `claude plugin validate . --strict` both pass
- `design.md` records the rename decision (D-7) and its rationale
- PR #5 title/description reflect the new name and general-document framing

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-07-05
- **Last completed**: Task #6 — renamed the plugin `techting` → `writ` (skill stays `up`, invocation
  `/writ:up`) and reworded every "technical document"/"technical writing" occurrence to plain
  "document"/"writing" across `plugin.json`, `SKILL.md`, `README.md`, `CHANGELOG.md`, `design.md`
  (new D-7), the root marketplace/README, and PR #5's title. Prompted by the user noticing the
  design content (reader definition, five axes sourced from Diátaxis/MADR/ADR guidance) was never
  technical-writing-specific — only the name/framing narrowed it. QA independently confirmed the
  rename preserved git history and left the SKILL.md procedure byte-identical in substance (no scope
  creep), and caught a pre-existing stale-link defect in PR #5's body (`.rn/techting/...` → 404),
  fixed to `.rn/20260614-writ/...`. Both strict validations pass. The branch itself was then renamed
  `worktree-techting` → `worktree-writ` — an earlier attempt via GitHub's branch-rename API
  unexpectedly closed the PR instead of retargeting it, so the fix was to recreate it: PR #15
  supersedes closed PR #5 with identical content. Task-level state: #1–#4 done; #5 and #6 done except
  `[ ] user review (on the PR)`, both awaiting review on PR #15.
- **Next**: User reviews PR #15 (tasks #5 and #6). Once approved, #5's remaining open box — the Level
  B dogfood (run `up` on a real draft with two different reader definitions, confirming voice/axis
  change) — still needs to run before the Acceptance-criteria run can close the session.
- **Notes**: Branch `worktree-writ` (renamed from `worktree-techting`; PR #15 supersedes closed PR
  #5 — same content, recreated after an earlier GitHub branch-rename attempt unexpectedly closed #5).
  PR #15 is open and unreviewed. No blockers beyond the
  pending review and the deferred Level B dogfood.
