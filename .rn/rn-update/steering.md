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

**Mid-session pivot (2026-06-25, see D-2).** While reviewing the dn change, the user judged the rn
prompts too noisy to assess the two requirements against. New direction: first rewrite every rn
skill/reference as **pure procedural work-instructions** (no rationale/rules-as-prose; intent moved
to a non-runtime `rn/DESIGN.md`), then re-judge the two feedback items on that clean base. The two
items above stay the goal; the proceduralization is the precondition for judging them.

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

### #1: `/rn:dn` ends with a genuinely clean worktree — DONE (user review pending)

**Purpose**: Rewrite the `dn` skill so a suspend resolves test-run residue and finishes with a truly
clean tree, without ever silently deleting user-authored files.

**Status**: implementation + QA done — `checks/1.md`, QA round-4 PASS after 3 fix iterations. User
review still pending on PR #14 (the user pivoted to #2 before approving).

**Prerequisites**: none

**Steps**:

- [x] In `rn/skills/dn/SKILL.md`, resolve untracked residue: gitignore recurring test/build artifacts
      (repo-root `.gitignore`, committed); ambiguous paths surfaced to the user
- [x] Guard: any untracked path not clearly residue is surfaced to the user, never auto-deleted
- [x] Verify step asserts `git status --porcelain` empty as the end-state, after residue is resolved;
      bounded per-path retry (persisted marker) so the suspend never wedges
- [x] self-check (checks/1.md)
- [x] QA expert review (subagent) — round-4 PASS
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

### #2: Proceduralize all rn prompts; move intent to DESIGN.md — DONE (QA + user review pending)

**Purpose**: Rewrite every rn skill/reference as pure procedural work-instructions — no rationale or
rules-as-prose — preserving all behavior, and relocate the "why" to a non-runtime `rn/DESIGN.md`.

**Status**: all five files converted and the design notes assembled; coordinator-reviewed. A QA pass
over the conversion set and user review are still pending.

**Prerequisites**: none

**Steps**:

- [x] Convert `dn`, `on`, `up`, `task-workflow`, `steering-template` to pure numbered procedure
- [x] Assemble `rn/DESIGN.md` (one intent note per step/decision; not read at runtime)
- [x] Remove duplication (dropped the `steering-template` `Fill rules` section; template block kept
      byte-for-byte)
- [x] Coordinator review of each converted file — behavior preserved (read all five)
- [ ] QA expert review of the conversion set (subagent) — not yet run
- [ ] user review

**Completion criteria**:

- Each rn skill/reference is pure numbered procedure: no rationale, "Why", or rule-justification
  prose; every prior behavior, branch, and fallback survives as a step (representative failure mode: a
  dropped rule).
- `rn/DESIGN.md` carries the removed intent, one note per step/decision, and is not read at runtime.
- The runtime prompt surface drops materially with no behavior change (measured: 616 → 393 lines).
- The fenced `steering.md` template block is byte-for-byte unchanged and completion-criteria semantics
  are unchanged (so #3 can judge them on a faithful base).

### #3: Re-judge the two feedback requirements on the clean base — NOT STARTED

**Purpose**: With the noise removed, decide whether each original feedback change is warranted and
correctly shaped: (a) the dn residue/clean-tree behavior (#1); (b) the completion-criteria reframe —
expressing the work's *objective* (objective achieved / intended behavior observed / representative
failure modes absent) rather than its *result*.

**Prerequisites**: #2

**Steps**:

- [x] Re-read the now-procedural `dn` and decide: is the residue behavior right, over-built, or in
      need of trimming? Record the decision. → **TRIM** (D-3a)
- [x] Re-read `steering-template`'s completion-criteria guidance on the clean base; decide whether the
      objective-vs-result reframe is still needed and, if so, its minimal form (the original #2 plan:
      three lenses + a contrast example, keeping existing constraints, aligning `task-workflow`)
      → **CHANGE, minimal form** (D-3b)
- [x] Apply any decided change via the implementation expert, or record a decision to leave as-is
      → both applied in commit `7233d51`
- [x] self-check (checks/3.md) + [x] QA expert review (PASS) + [ ] user review

**Completion criteria**:

- A recorded decision (in Decisions) for each feedback item — keep / trim / change — with rationale
  judged on the clean base.
- Any applied change preserves the pure-procedure form and is reflected in `rn/DESIGN.md`
  (representative failure mode: re-introducing rationale prose into a runtime file).

### #4: Record the changes and verify cross-doc consistency — NOT STARTED

**Purpose**: Record the shipped changes in the CHANGELOG and confirm the rn docs are internally
consistent after all edits.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] Create `## [Unreleased]` at the top of `rn/CHANGELOG.md` with one user-facing `Changed` line per
      shipped change (dn residue handling; pure-procedure rewrite; any #3 change)
- [ ] Grep the rn docs for stale/contradictory wording; confirm none contradicts the current docs
- [ ] Confirm `version` in `plugin.json` is still `0.6.0`
- [ ] self-check + QA expert review + user review

**Completion criteria**:

- `rn/CHANGELOG.md` has an `## [Unreleased]` section carrying one user-facing line per shipped change,
  in user terms (objective: a user reading the changelog learns what changed and why it helps).
- A grep over the rn docs finds no surviving statement that contradicts the current docs
  (representative failure mode: leftover stale instruction).
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

## D-2: Proceduralize the rn prompts before re-judging the requirements
- **Issue**: The rn prompts had grown heavy with rationale and repeated rules (task-workflow alone was
  279 lines / ~2,700 words). The user found them too noisy to assess whether the two feedback changes
  (dn residue, completion criteria) were warranted, and asked to make them pure work-instructions
  first.
- **Conclusion**: Rewrite every rn skill/reference as pure numbered procedure an LLM follows without
  needing any "why"; move the intent to a separate `rn/DESIGN.md` that is **not read at runtime**,
  with one note per step/decision. Then re-judge the two requirements on the clean base.
- **Rationale**: Two readers with different needs were conflated in one file — the executing LLM needs
  only steps (rationale is noise that blocks judgment), while the maintainer needs the intent (means
  alone can't be judged). Separating by reader removes the noise without losing the "why". Dropping
  the intent entirely was rejected — the user explicitly needs it to judge requirements.
- **Evidence**: Runtime prompt surface dropped 616 → 393 lines (−36%) with behavior preserved; intent
  preserved in `rn/DESIGN.md` (139 lines).
- **Sources**: this session's conversation; the conversion commits `3f0e435`..`e8ebcf7` on `rn-update`.

## D-3: Re-judge the two feedback requirements on the clean base (task #3)
- **Issue**: With the rn prompts now pure procedure, decide for each original feedback item whether the
  change is warranted and correctly shaped: (a) the `dn` residue / clean-tree behavior; (b) the
  completion-criteria objective-vs-result reframe.
- **Conclusion**:
  - **(a) TRIM.** Keep the core — gitignore recurring test/build residue (`dn` step 5), ask-never-delete
    on ambiguous untracked paths, record user-deferred paths, always complete. **Remove** step 7's
    retry-once-per-path correction-marker loop and the step-5 "corrective re-entry" bullet that only
    serves it. Step 7 becomes a single forward pass: verify `git status --porcelain`; record any
    still-present non-gitignored path as user-deferred in `State → Notes`; proceed.
  - **(b) CHANGE — apply, minimal form.** Reframe the `steering-template.md` completion-criteria
    guidance to three lenses (objective achieved / intended behavior observed / representative failure
    modes absent) plus one objective-vs-result ("the output exists") contrast example; keep all three
    existing constraints (third-party verifiable, no vague terms, outcomes-not-actions); clarify the
    `Criteria vs steps` table row (line 90) so "outcomes/end-state only" is not read as "the artifact
    was produced," keeping it consistent with `task-workflow`'s use of criteria as the review bar.
- **Rationale**:
  - (a) D-1's "never wedge" guarantee does not require a retry loop — a single forward pass never loops
    at all. The retry guards only the case of a gitignore rule the agent itself just wrote failing to
    match, and in that case step 5 has no guidance to write a *better* rule the second time, so it falls
    through to "record as deferred" — identical to dropping the loop, minus the correction-marker
    bookkeeping. The mechanism does not earn its runtime complexity.
  - (b) The "read as 'the output exists'" gap survives the proceduralization: the template still says
    only "outcomes / end-state only," the exact wording the feedback flagged. This session's own task
    criteria already use the better form (`representative failure mode:` annotations) but the template
    never directs a writer to. The three-lens + contrast form is the minimal change that closes the gap
    without dropping any existing constraint.
- **Evidence**: `dn/SKILL.md` steps 5–7 (branch); `steering-template.md` lines 52–56 and line 90
  (branch); D-1 (this file); task #2's own criteria use the target objective form.
- **Sources**: this session's re-judgment of `rn/skills/dn/SKILL.md` and `rn/references/steering-template.md` on `rn-update`.

## D-4: Completion-criteria final form — two questions, each with grounds (refines D-3b)
- **Issue**: Reviewing D-3b's applied three-lens form, the user observed it reduces to two questions —
  "is the objective achieved?" and "are new problems absent?" — and that each must be answerable **with
  grounds (根拠)**. D-3b's bullets required third-party *verifiability* but never required the writer/
  verifier to *state the grounds*, so a criterion could still stand as a bare assertion. Applied
  reflexively to this session's own task #3, the QA "PASS" was trace-based, not execution-based — the
  grounds were weak — which is exactly what this gap lets slip through.
- **Conclusion**: Reframe the `steering-template.md` completion-criteria guidance as **two questions a
  third party answers with grounds**: ① is the objective achieved (the objective met, not that an
  output was produced — includes the intended behavior observably present), ② are new problems absent
  (name the representative failure modes, require their absence). Keep the objective-vs-result contrast
  example and all three prior constraints. **Grounds live in the verification, not in the criterion
  text** — the criterion states the end-state (means-vs-end), and the `checks/{id}.md` Self-check
  Evidence / QA Evidence columns are where the grounds are recorded; the guidance just requires the
  criterion be *phrased so the two questions are answerable with grounds*. This supersedes D-3b's
  three-lens wording.
- **Rationale**: Two questions — confirmation (does it achieve the aim?) and falsification (does it
  break anything?) — are a tighter, harder-to-game form than three lenses, and "objective achieved" vs
  "behavior observed" were really one positive axis. Making grounds mandatory turns criteria from
  assertions into checkable claims. Keeping grounds in the verification (not the criterion text) avoids
  re-introducing means into the criterion (the means-vs-end anti-pattern).
- **Evidence**: D-3b applied form (`steering-template.md` lines 54-59, branch); this session's task #3
  QA verdict was trace-based (no execution of the new `dn`), exposing the missing-grounds gap.
- **Sources**: user feedback this session; D-3b (above).

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up.)

- **Status**:
- **Date**:
- **Last completed**:
- **Next**:
- **Notes**:
