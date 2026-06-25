# Goal

Apply two improvements to the `rn` plugin that surfaced from real usage:

1. **`/rn:dn` must end with a genuinely clean worktree.** Today `dn` commits only tracked changes
   and then asserts `git status` is clean (Step 5), but test runs during a session leave untracked
   residue (caches, coverage output, compiled/temp files). That residue keeps the tree from ever
   being clean, so the "Verify clean" step is unsatisfiable in practice. `dn` should resolve the
   residue — never just assert — while never silently deleting anything the user authored.
2. **Completion criteria must express the work's *objective*, not its *result*.** The current
   guidance ("outcomes / end-state only") still gets read as "the output was produced," so criteria
   describe work done rather than goal met. Reframe the guidance so criteria verify three things:
   the objective is achieved, the intended behavior actually occurs, and representative failure
   modes are absent.

The change set is documentation/prompt edits to the `rn` plugin's skill and reference files. No
runtime code is involved.

# Acceptance criteria

- Running `/rn:dn` from a worktree that contains test-run residue ends with `git status --porcelain`
  empty — the tree is genuinely clean, not merely asserted clean.
- After `/rn:dn`, recurring test/build artifacts are excluded by a committed `.gitignore` rule, so a
  later test run does not re-dirty the tree (the residue problem does not recur).
- The `dn` instructions never direct removing an untracked path that is not clearly test/build
  residue without first surfacing it to the user — user-authored content is never silently deleted.
- `/rn:dn` always completes the handoff — it never loops/wedges; an untracked path the user leaves
  unresolved is recorded in `State → Notes` and the suspend proceeds (see D-1).
- The completion-criteria guidance in `steering-template.md` directs writing criteria along three
  verification lenses — objective achieved, intended behavior observed, representative failure modes
  absent — and explicitly contrasts an objective-style criterion against a result-style ("the output
  exists") one.
- The guidance retains every existing valid constraint (third-party verifiable, no vague terms,
  outcomes-not-actions); none is dropped or contradicted.
- `task-workflow.md`'s use of completion criteria as the review bar stays consistent with the new
  guidance — no rn doc contradicts another after the change (grep-verified).
- `rn/CHANGELOG.md` records both changes under `## [Unreleased]`, one user-facing line each, in user
  terms; `version` in `plugin.json` is unchanged (no release is being cut).

# Assumptions

- The dn residue problem is caused by untracked test/build artifacts that are not gitignored: `dn`
  Step 2 commits only tracked changes and Step 5 requires a clean tree, so untracked residue blocks
  cleanliness. (Fact, read from `rn/skills/dn/SKILL.md`.)
- No new `rn` version is cut in this session — there is no release instruction — so changes wait
  under CHANGELOG `## [Unreleased]` and `plugin.json` stays at `0.6.0`. (Assumption; corrected if the
  user asks for a release.)
- The edits are prose/prompt only (no executable code), so each task uses the non-code verification
  chain (self-check → QA expert → user review). (Assumption based on the files in scope.)
- The plugin set is unchanged (no plugin added/renamed/removed), so `marketplace.json` and the root
  `README.md` need no update. (Fact: only `rn/` internals change.)

# Rules

- commit and push every change; one completion marker per task
- edits stay within the `rn/` plugin (skills, references, CHANGELOG); do not touch other plugins
- do not bump `version` in `plugin.json` — no release instruction is in scope
- the steering's own completion criteria must themselves follow the objective-based form this session
  introduces (dogfood task #2)

# Tasks

### #1: `/rn:dn` ends with a genuinely clean worktree

**Purpose**: Rewrite the `dn` skill so a suspend resolves test-run residue and finishes with a truly
clean tree, without ever silently deleting user-authored files.

**Prerequisites**: none

**Steps**:

- [ ] In `rn/skills/dn/SKILL.md`, revise the residue handling: before declaring clean, inspect
      `git status --porcelain`; for untracked residue, add a committed `.gitignore` rule for
      recurring test/build artifacts, and only remove clearly-transient residue
- [ ] Add the guard that any untracked path not clearly test/build residue is surfaced to the user,
      never auto-deleted
- [ ] Make Step 5 ("Verify clean") assert `git status --porcelain` is empty as the end-state, after
      the residue is resolved (not before)
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- Given a worktree whose only residue is recurring test/build artifacts, the revised `dn` flow ends
  with `git status --porcelain` empty — the residue is gitignored away (objective: the residue the
  feedback is about no longer keeps the tree dirty; verifiable by reading the flow).
- The instructions direct adding a committed repo-root `.gitignore` rule for recurring test/build
  artifacts, so the same residue does not re-dirty the tree on a later run (representative failure
  mode: recurrence).
- The agent never deletes any untracked path on its own; an untracked path that is not clearly a
  regenerable artifact is surfaced to the user, never auto-deleted or auto-gitignored (representative
  failure mode: destroying or silencing user work). See D-1.
- The suspend always completes — it never loops/wedges. An untracked path the user leaves unresolved
  is recorded in `State → Notes` and the session suspends anyway (representative failure mode:
  `/rn:dn` hanging when the user is trying to leave). See D-1.

### #2: Reframe completion-criteria guidance to be objective-based

**Purpose**: Rewrite the completion-criteria guidance so it directs criteria that verify the
objective is met, intended behavior occurs, and representative failure modes are absent — not that an
output was produced.

**Prerequisites**: none

**Steps**:

- [ ] In `rn/references/steering-template.md`, rewrite the `Completion criteria` guidance block to
      state the three lenses (objective achieved / intended behavior observed / representative failure
      modes absent), keeping the existing valid constraints
- [ ] Add a short contrast example distinguishing a result-style criterion from an objective-style one
- [ ] Update the `Task definition requirements` table rows (Objectivity / Criteria vs steps) to match
- [ ] In `rn/references/task-workflow.md`, align any description of completion criteria as the review
      bar with the new framing (no contradiction)
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- `steering-template.md`'s completion-criteria guidance states all three verification lenses and
  contrasts an objective-style criterion against a result-style one (objective: a reader can tell the
  two apart from the guidance alone).
- Every existing valid constraint (third-party verifiable, no vague terms, outcomes-not-actions)
  remains present (representative failure mode: silently dropping a still-valid rule).
- No statement in `task-workflow.md` or `steering-template.md` contradicts the new framing
  (representative failure mode: two rn docs disagreeing on what a completion criterion is).

### #3: Record the changes and verify cross-doc consistency

**Purpose**: Record both changes in the CHANGELOG and confirm the rn docs are internally consistent
after the edits.

**Prerequisites**: #1, #2

**Steps**:

- [ ] Create `## [Unreleased]` at the top of `rn/CHANGELOG.md` with one user-facing `Changed` line per
      change (dn cleanliness; objective-based criteria)
- [ ] Grep the rn docs for stale references to the old completion-criteria framing and the old
      dn-cleanliness wording; confirm none now contradicts the new guidance
- [ ] Confirm `version` in `plugin.json` is still `0.6.0`
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- `rn/CHANGELOG.md` has an `## [Unreleased]` section carrying one user-facing line per change, written
  in user terms (objective: a user reading the changelog learns what changed and why it helps).
- A grep over the rn docs finds no surviving statement that contradicts the new completion-criteria or
  dn-cleanliness guidance (representative failure mode: leftover stale instruction).
- `version` in `rn/.claude-plugin/plugin.json` is `0.6.0` — unchanged (representative failure mode:
  accidentally cutting a release).

# Decisions

## D-1: Reconcile "tree ends clean" with "suspend never wedges"
- **Issue**: The first review of task #1 required a terminal escape so `/rn:dn` never loops forever
  (the user runs `dn` precisely to leave). But task #1's original criterion 1 demanded the tree end
  with `git status --porcelain` *empty* unconditionally. For an untracked path that is genuinely
  ambiguous (not clearly regenerable residue) and that the user defers on, those two goals conflict —
  ending empty would force an autonomous delete/gitignore, which the never-silently-destroy rule
  forbids.
- **Conclusion**: Split the bar. (a) For *recurring test/build residue* — the case the feedback is
  about — the tree ends genuinely empty, because such residue is gitignored away. (b) For an
  *ambiguous untracked path*, the agent never acts autonomously; it surfaces the path to the user, and
  any path the user defers is recorded in `State → Notes` and the suspend completes anyway. The tree
  may then end non-empty by the user's own choice, which is correct, not a failure.
- **Rationale**: The feedback's intent is "test residue should stop keeping the worktree dirty," which
  (a) satisfies fully. Forcing (b) to also end empty would require the agent to delete or hide files it
  cannot safely classify — trading a clean tree for the worse failure of destroying user work or
  wedging the handoff. Honesty (record + warn) beats a false guarantee.
- **Evidence**: `/rn:dn` is invoked to stop and hand off (skill purpose, `dn/SKILL.md` Phase 1);
  recurring artifacts are silenced by a gitignore rule, removing them from `git status` output without
  deletion.
- **Sources**: `rn/skills/dn/SKILL.md`; the task #1 QA reviews in this session.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up.)

- **Status**: not suspended
- **Date**: 2026-06-25
- **Last completed**: none
- **Next**: #1 dn ends with a genuinely clean worktree
- **Notes**: context needed for resume
