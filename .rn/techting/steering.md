# Goal

Package the "technical-writing instruction" into a Claude Code plugin `techting` (skill `up`,
invoked `/techting:up`) so its reader-first procedure — define the reader, then derive tone,
diagrams, closing, and outline — can be applied on demand without pasting the instruction each
time. It must be invocable by a human or by Claude itself. Primary mode is brushing up an existing
draft (authoring from scratch runs through the same procedure but is secondary). The verbatim
instruction is preserved at `.rn/techting/instruction.md` as the source of record, and the skill
body is derived from it.

# Acceptance criteria

- `techting/skills/up/SKILL.md` exists and its body covers all four pillars of the instruction:
  reader definition (who / what they must decide-or-do / how they read), the five outline axes
  (article, guide, reference, record-ADR, evaluation), structure-and-flow shown as mermaid
  diagrams, and a pre-output self-check.
- The skill states the brush-up use case explicitly: input = an existing draft, output = the
  revised document plus "what was changed and why".
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

- [ ] Rewrite `techting/skills/up/SKILL.md` from `.rn/techting/instruction.md`, fresh — do not patch
      the old file. Frontmatter: third-person description with brush-up-first trigger phrases,
      model-invocable, version. Body in imperative form, lean (<2,000 words), single file.
- [ ] Separate the two layers in the body: process (model instructions) vs output rules (constraints
      on the produced document). Put the mermaid rule only in output rules, with an explicit
      addressee sentence. No mermaid diagram embedded in the prompt body.
- [ ] Carry every source pillar (reader definition + ask-or-infer gate, base/house-style, the five
      axes with no-mixing, voice-by-reader, pre-output self-check) — cross-check item by item.
- [ ] Add the missing self-check item "each document is a single axis (not mixed)" (Expert C's one
      fidelity gap). Optionally wire derivation: "how-they-read → axis", "table is an example, §1 is
      the source of truth".
- [ ] Replace the old mermaid acceptance criterion with the corrected Level A / Level B criteria
      from D-3.
- [ ] Add `techting/CHANGELOG.md` (Keep a Changelog; `## [0.1.0]` Added line; rn is the precedent).
- [ ] Re-validate: `claude plugin validate ./techting --strict` and `. --strict`; dogfood with two
      different reader definitions to confirm Level B (voice/axis change).
- [ ] self-check (record OK/NG per criterion in `.rn/techting/checks/4.md`)
- [ ] QA engineer review (subagent)
- [ ] user review (on the PR)

**Completion criteria**:

- `SKILL.md` body separates process from output rules, contains no embedded mermaid diagram, and
  carries an addressee sentence on the diagram rule.
- All source pillars present; the self-check includes the single-axis (no-mixing) item.
- The steering acceptance criteria use the Level A / Level B split from D-3.
- `CHANGELOG.md` exists; both strict validations pass; the two-reader dogfood shows voice/axis change.


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

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
