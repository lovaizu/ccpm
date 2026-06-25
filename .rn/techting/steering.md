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

So the skill works in that order: **first clear the floor** (inspect and remove the AI tells), **then
reach for the ceiling** (derive and add the attractive qualities).

**Means (not the end):** reader-first derivation — define the reader (who they are / what they must
decide or do / how they read), then derive the axis, voice, and structure from that definition
rather than from memory.

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
- **Level B — the document the skill produces (dogfood-verified):** running `up` on a draft yields
  output whose structure/flow is shown as mermaid wherever there is order or branching, with no
  diagram/prose duplication; feeding two different reader definitions changes the output's voice and
  axis (proving the procedure derives, not memorizes); each produced document holds a single axis,
  not mixed.
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

- **Status**: paused
- **Date**: 2026-06-25
- **Last completed**: Task **#4** deliverable — rebuilt `techting/skills/up/SKILL.md` from source
  (commit `9188602`), added `techting/CHANGELOG.md`, updated the steering acceptance criteria to the
  D-3 Level A / Level B split. Self-check + QA expert review both PASS (recorded in
  `.rn/techting/checks/4.md`). All #4 steps checked **except** the final user-review gate.
- **Next**: Get the user's approval of **task #4 on PR #5**, then check it off with the completion
  marker commit (`{type}: complete task #4 — …`) and push. After that, all four tasks are done —
  propose running the steering **Acceptance criteria** as the final gate (the only remaining items
  are the goal-level criteria, not a new task).
- **Notes**: Branch `worktree-techting`, PR https://github.com/lovaizu/ccpm/pull/5 (still **draft**).
  - **The #4 marker is NOT yet written** — user review is pending. Do not commit `complete task #4`
    until the user approves on the PR. `.rn/techting/checks/4.md` is committed (coordinator ledger)
    via this suspend's `wip:` commit, with the QA verdicts already filled in.
  - **The category-error defect is fixed**: SKILL.md no longer embeds a mermaid diagram in the
    prompt body; the body is split into `## The procedure` (process / model instructions) and
    `## Rules for the produced document` (output rules), the latter opening with the explicit
    addressee sentence "These rules govern the document this skill produces — not this SKILL.md
    prompt." Verified: `grep -c '```mermaid'` on SKILL.md = 0; both `claude plugin validate
    ./techting --strict` and `. --strict` pass.
  - **CHANGELOG decision**: entry sits under `## [Unreleased]`, not a dated `## [0.1.0]`, because no
    release instruction has been given (ccpm rule: bump only on explicit release). It promotes to a
    dated section when the user cuts the release — at which point also tag `techting-v0.1.0` and mark
    PR #5 ready.
  - **When the PR is approved**: this is the last task, so after the #4 check-off, the natural close
    is to run the Acceptance criteria, then (on a release instruction) cut 0.1.0 — bump plugin.json
    stays 0.1.0 already, promote CHANGELOG, tag, publish Release, mark PR ready/merge.
