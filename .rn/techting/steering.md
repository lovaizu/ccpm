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

# State

- **Status**: paused
- **Date**: 2026-06-15
- **Last completed**: Dogfooded `/techting:up` end-to-end on a deliberately flawed draft, found and
  fixed a real design gap in the skill, then rebased the branch onto origin/main and force-pushed.
- **Next**: Wait for the user's own PR review of #5. No code work remains unless their review
  surfaces a gap. When they say go, `gh pr ready 5` then merge to main.
- **Notes**: Branch `worktree-techting`, PR https://github.com/lovaizu/ccpm/pull/5 (still **draft**,
  by the user's choice — they review it themselves before ready/merge). Tip `0c8034b`.
  - Tasks #1–#3 all complete and reconciled; all 9 Acceptance criteria previously verified by
    measurement (PASS). The plugin is shipped on the branch: `techting/skills/up/SKILL.md` (four
    pillars), `plugin.json` (version 0.1.0, only place with a version), `techting/README.md`
    (scenario style), registered in `.claude-plugin/marketplace.json` (category `writing`, no
    version) and linked from root README.
  - **This session's change** (`0c8034b`): a dogfood simulation of `/techting:up` surfaced that
    step 1's safety valve ("can't pin the reader → ask the user") assumed a human in the loop,
    contradicting the skill's model-invocable design. Fixed to **ask-else-infer** across the three
    places that must agree — step-1 prose, the procedure mermaid ASK node, and the pre-output
    self-check (new item: declare an inferred reader). Also clarified step-2 axis purity for small
    documents (keep a minimal inline version + link the exhaustive one out, instead of spawning a
    file for a few entries). `claude plugin validate ./techting --strict` and `validate . --strict`
    both still pass clean.
  - Branch was rebased onto origin/main (10 commits replayed, no conflicts) and force-pushed with
    `--force-with-lease`.
  - When resuming: nothing to build. Either (a) the user approves → `gh pr ready 5` then merge, or
    (b) the user reports review feedback → fix, re-run the relevant Acceptance checks, re-commit.
