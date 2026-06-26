# Goal

Apply three improvements to the `rn` plugin that surfaced from real usage:

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
3. **`steering.md` must not accumulate across repeated `/rn:up`/`/rn:dn` cycles** (surfaced
   2026-06-26, see D-5). Redefine steering's purpose as the *forward contract for the remaining work*
   — the minimum a resuming agent needs to finish the goal correctly — not the session's archive.
   The durable record of what was decided and why already lives in git commits and the PR, so three
   accumulation vectors are cut: (a) `Decisions` becomes a live working set — `/rn:up` retires a
   decision once the tasks it governs are shipped; (b) `/rn:dn` caps `State → Notes` to a forward
   pointer (branch/PR, next action, open blockers/deferred paths), not a session re-narration;
   (c) `/rn:up` collapses a shipped task to a one-line `SHIPPED` pointer, so the `Tasks` section — the
   largest — stops carrying finished tasks' full Steps and Completion criteria across cycles.
4. **Review gates must sit where human judgment is irreplaceable, not on every task** (surfaced
   2026-06-26, see D-6). Today every task ends with a user-review gate (`task-workflow.md` Phase:
   Complete) — N tasks, N gates — while design has no dedicated gate and evaluation is only a weak
   "propose running Acceptance criteria." Rebalance to exactly three scheduled gates — **plan,
   design, evaluation** — and remove the per-task user gate; per-task quality stays covered by the
   self-check + QA/expert + coordinator chain. Separately, as a **different category (not a gate, not
   a gate's exception)**, specify **escalation**: an always-open channel where any execution discovery
   that would change the agreed plan or design is raised to the user immediately, wherever it occurs.

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
- `/rn:up`'s reconcile retires a decision from `Decisions` once every task it governs is checked off
  and shipped (its `complete task #` marker is in git), and keeps a decision that still governs an
  unchecked task — so the `Decisions` section does not accumulate shipped-work decisions across
  cycles (representative failure mode: a stale shipped decision lingers; or a still-governing decision
  is wrongly dropped). The retired decision's rationale remains recoverable from the commit that
  recorded it and from the PR.
- A `Governs: #N` field on each decision makes retirement determinable without re-reading the
  decision's prose; a cross-cutting decision with no single task uses `Governs: —` and is kept for the
  session's life.
- `/rn:up`'s reconcile collapses a shipped task (its box is checked and its `complete task #` marker
  is in git) to a one-line `SHIPPED` pointer carrying the task number, name, and marker SHA, dropping
  its Steps and Completion criteria — so the `Tasks` section, the largest, does not carry finished
  tasks' full bodies across cycles (representative failure mode: a shipped task keeps its full
  Steps/criteria and `Tasks` grows unbounded; or an unshipped/in-progress task is wrongly collapsed).
  The collapsed task's detail remains recoverable from its `complete task #` commit, its
  `checks/{id}.md`, and the PR; the next-task scan still treats a `SHIPPED` task as done.
- `/rn:dn` writes `State → Notes` as a bounded forward pointer — branch/PR, next concrete action,
  open blockers, user-deferred paths — not a multi-paragraph re-narration of the session
  (representative failure mode: the per-resume narrative bloat returns).
- `steering-template.md` encodes both as structure: the `Decisions` template carries the `Governs`
  field and states the live-working-set retirement rule; the `State` template directs `Notes` to the
  forward-pointer form. The redefinition rationale lives in `rn/DESIGN.md`, not in the runtime
  prompt files (representative failure mode: rationale prose re-enters a runtime file).
- `rn/CHANGELOG.md` records all three changes under `## [Unreleased]`, one user-facing line each, in
  user terms; `version` in `plugin.json` is unchanged (no release is being cut).
- `task-workflow.md` no longer carries a per-task user-review gate; a task completes via the
  self-check + QA/expert + coordinator chain and the check-off, with no per-task user sign-off
  (objective: the per-task gate is gone; representative failure mode: a per-task user gate survives
  anywhere in `task-workflow`/`on`/`up`).
- The workflow defines exactly three scheduled user gates — plan (`/rn:on`), design, and evaluation —
  and no others (objective: the three gates are the complete set; representative failure mode: a
  fourth scheduled gate, or one of the three missing).
- The design gate gives the user a sign-off on the approach/key decisions before they are built on,
  distinct from reviewing a task's deliverable; the evaluation gate makes the end-of-session
  Acceptance-criteria run a user sign-off, not a bare proposal (objective: design and evaluation are
  gated; representative failure mode: either remains ungated).
- Escalation is specified as a separate always-open channel, not a gate's exception: any execution
  discovery/blocker/call that would change the agreed plan or design is surfaced to the user
  immediately (objective: the loop stays honest between gates; representative failure mode: escalation
  is written as a special case of a gate, collapsing the two categories).
- `rn/DESIGN.md` records the gate-vs-escalation model and the rebalance rationale; the runtime files
  stay pure procedure; `rn/CHANGELOG.md` gains one user-facing line under `## [Unreleased]`; no rn
  doc contradicts another after the change (grep-verified).

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
      → D-3a/D-3b in `7233d51`; criteria refined to two-questions+grounds final form (D-4) in `eab36f3`
- [x] self-check (checks/3.md) + [x] QA expert review (PASS; dn trim empirically validated by sandbox
      execution — residue tree ends `git status --porcelain` empty, no loop, no deletion) + [ ] user review

**Completion criteria**:

- A recorded decision (in Decisions) for each feedback item — keep / trim / change — with rationale
  judged on the clean base.
- Any applied change preserves the pure-procedure form and is reflected in `rn/DESIGN.md`
  (representative failure mode: re-introducing rationale prose into a runtime file).

### #4: Redefine steering's purpose so it does not accumulate across cycles — IN PROGRESS (Lever C)

**Purpose**: Make `steering.md` the forward contract for the *remaining* work, not the session's
archive, so repeated `/rn:up`/`/rn:dn` cycles do not pile up content. Three structural changes:
`Decisions` becomes a live working set retired on ship (Lever A), `/rn:dn` caps `State → Notes`
to a forward pointer (Lever B), and `/rn:up` collapses a shipped task to a one-line `SHIPPED` pointer
(Lever C). See D-5.

**Status**: Levers A+B implemented and QA-PASS (round-2; `87f63cf`), user review pending on PR #14.
Lever C added 2026-06-26 after `/rn:up` measured this steering at 412 lines and found `Tasks` (the
largest section) untouched by A/B — impl + QA for Lever C pending.

**Prerequisites**: none

**Steps**:

- [x] In `rn/skills/up/SKILL.md` Step 6, add decision retirement to the reconcile: drop any decision
      whose every `Governs` task is checked off and shipped (its `complete task #` marker is in
      git); keep decisions that still govern an unchecked task or use `Governs: —`
- [x] In `rn/references/steering-template.md`, add the `Governs: #N / —` field to the `Decisions`
      template and state the live-working-set retirement rule; direct `State → Notes` to the
      bounded forward-pointer form (branch/PR, next action, open blockers, user-deferred paths)
- [x] In `rn/skills/dn/SKILL.md` Step 3, cap what is written to `Notes` to the forward pointer — not
      a multi-paragraph session re-narration
- [x] Record the redefinition rationale in `rn/DESIGN.md` (up Step 6 retirement; dn Step 3 cap;
      template Decisions live-working-set + Governs; State Notes forward pointer) — runtime files
      stay pure procedure
- [x] self-check + QA expert review of Levers A+B (checks/4.md) — round-2 PASS (round-1 found D1/D2,
      fixed `87f63cf`)
- [x] Lever C: in `rn/skills/up/SKILL.md` Step 6, add task collapse — collapse any shipped task (box
      checked + `complete task #` marker in git) to a one-line `### #N: <name> — SHIPPED (#N in
      <sha>)` heading, dropping its body; in-progress/unshipped tasks untouched (`f72018a`; boundary
      made structural in `a1fb624`)
- [x] Lever C: in `rn/references/steering-template.md`, note the shipped-task collapse on the `Tasks`
      section (parallel to the `Decisions` live-working-set note) so the structure encodes it
- [x] Lever C: in `rn/skills/up/SKILL.md` Step 7, make the next-task scan treat a `SHIPPED` task as done
- [x] Lever C: record the collapse rationale and the collapse-vs-delete distinction in `rn/DESIGN.md`
      (up Step 6; steering-template) — runtime files stay pure procedure
- [x] self-check of Lever C (checks/4.md)
- [x] QA expert review of Lever C (subagent) — round-1 found the phantom-`Status` defect, fixed
      `a1fb624`; re-check PASS
- [ ] user review (whole of #4: Levers A+B+C)

**Completion criteria**:

- `/rn:up`'s reconcile retires a decision once every task it `Governs` is checked off and shipped,
  and keeps one that still governs an unchecked task (objective: the `Decisions` section stops
  accumulating shipped-work decisions across cycles; representative failure mode: a stale shipped
  decision lingers, or a still-governing decision is wrongly dropped). The retired decision's
  rationale remains recoverable from its recording commit and the PR.
- `steering-template.md`'s `Decisions` template carries the `Governs` field and states the
  retirement rule; its `State` template directs `Notes` to the forward-pointer form (objective:
  the structure itself encodes both levers; representative failure mode: the rule is documented
  nowhere a writer reads).
- `/rn:dn` Step 3 writes `Notes` as a bounded forward pointer, not a session re-narration
  (representative failure mode: per-resume narrative bloat returns).
- `/rn:up`'s reconcile collapses a shipped task to a one-line `SHIPPED` pointer and leaves an
  in-progress/unshipped task fully intact, and `steering-template.md` records the collapse on the
  `Tasks` section (objective: the `Tasks` section stops carrying shipped tasks' full Steps/criteria
  across cycles, and the structure encodes the rule; representative failure modes: a shipped task is
  not collapsed and `Tasks` grows unbounded; an unshipped task is wrongly collapsed and its remaining
  Steps are lost; the next-task scan skips a not-yet-done task or re-runs a collapsed one). The
  collapsed task's detail stays recoverable from its `complete task #` commit, `checks/{id}.md`, and
  the PR.
- The redefinition rationale lives in `rn/DESIGN.md`; no rationale prose enters the runtime files,
  which stay pure numbered procedure (representative failure mode: "why" leaks back into a runtime
  file). No rn doc contradicts another after the change (grep-verified).

### #5: Record the changes and verify cross-doc consistency — DONE (user review pending)

**Purpose**: Record the shipped changes in the CHANGELOG and confirm the rn docs are internally
consistent after all edits.

**Status**: CHANGELOG `## [Unreleased]` written (`10a3bc4`), grep + version verified; self-check +
QA round-1 PASS (no defects, `checks/5.md`). User review pending on PR #14. Prerequisites #1–#4 are
done-through-QA but not yet checked off (their user review is also pending) — #5 was done ahead on
the user's instruction; if PR review changes #1–#4, the CHANGELOG lines get reconciled.

**Prerequisites**: #1, #2, #3, #4

**Steps**:

- [x] Create `## [Unreleased]` at the top of `rn/CHANGELOG.md`, one user-facing line per user-impacting
      change: dn residue/clean-tree (#1, `Fixed`); completion criteria as two questions + grounds (#3,
      `Changed`); steering non-accumulation (#4 — retire shipped decisions, collapse shipped tasks, cap
      Notes; `Changed`). The #2 pure-procedure rewrite gets NO entry — it is behavior-preserving and
      invisible to a user (plugin.md: refactors are not changelog-worthy)
- [x] Grep the rn docs for stale/contradictory wording; confirm none contradicts the current docs
- [x] Confirm `version` in `plugin.json` is still `0.6.0`
- [x] self-check + QA expert review (round-1 PASS, no defects) — [ ] user review

**Completion criteria**:

- `rn/CHANGELOG.md` has an `## [Unreleased]` section carrying one user-facing line per user-impacting
  change, in user terms (objective: a user reading the changelog learns what changed and why it helps;
  representative failure mode: a behavior-preserving refactor like the #2 proceduralization is listed,
  or a user-visible change is missing). A behavior-preserving refactor is excluded per plugin.md.
- A grep over the rn docs finds no surviving statement that contradicts the current docs
  (representative failure mode: leftover stale instruction).
- `version` in `rn/.claude-plugin/plugin.json` is `0.6.0` — unchanged (representative failure mode:
  accidentally cutting a release).

### #6: Rebalance review gates to plan/design/evaluation; escalation as a separate channel — NOT STARTED

**Purpose**: Move the workflow's user-review gates to the three points where human judgment is
irreplaceable (plan, design, evaluation), remove the per-task user gate, and specify escalation as a
distinct always-open channel. See D-6.

**Prerequisites**: #2 (edits land on the pure-procedure base)

**Steps**:

- [ ] In `rn/references/task-workflow.md`, remove the per-task user-review gate from Phase: Complete;
      a task completes via self-check + QA/expert + coordinator review + check-off, no per-task user
      sign-off. The coordinator's independent diff review and the expert reviews stay intact.
- [ ] Generalize the existing "User's call" triage (`task-workflow.md` Triage step) into an explicit
      **escalation** channel: any execution discovery/blocker/call that would change the agreed plan
      or design is surfaced to the user immediately, wherever in the flow it occurs — stated as a
      channel distinct from the gates, not an exception to one.
- [ ] Add the **design gate**: a scheduled user sign-off on the approach/key decisions before they
      are built on, distinct from reviewing a task's deliverable (folds into the plan gate when design
      is settled at plan time; a separate stop before heavy build when it is not).
- [ ] Strengthen the **evaluation gate**: make the end-of-session Acceptance-criteria run a user
      sign-off in `on`/`up`/`task-workflow` advance, not a bare proposal.
- [ ] Confirm the **plan gate** in `rn/skills/on/SKILL.md` stays and is named as one of the three.
- [ ] Record the gate-vs-escalation model and rebalance rationale in `rn/DESIGN.md`; runtime files
      stay pure procedure.
- [ ] Add one user-facing line to `rn/CHANGELOG.md` under `## [Unreleased]`.
- [ ] self-check (checks/6.md) + QA expert review (subagent) + grep cross-doc consistency

**Completion criteria**:

- `task-workflow.md` has no per-task user-review gate; a task completes via the self-check + QA/expert
  + coordinator chain and the check-off (objective: the per-task gate is gone; representative failure
  mode: a per-task user gate survives in `task-workflow`/`on`/`up`).
- Exactly three scheduled user gates exist — plan, design, evaluation — and escalation is specified as
  a separate always-open channel, not an exception to a gate (objective: the model is encoded as the
  user defined it; representative failure modes: a fourth scheduled gate; a missing gate; escalation
  written as a gate's special case).
- The design gate signs off the approach before it is built on, and the evaluation gate makes the
  Acceptance-criteria run a user sign-off (objective: design and evaluation are gated; representative
  failure mode: either remains ungated).
- `rn/DESIGN.md` carries the model + rationale; the runtime files stay pure numbered procedure;
  `rn/CHANGELOG.md` has one user-facing line; no rn doc contradicts another (grep-verified).

# Decisions

## D-1: Reconcile "tree ends clean" with "suspend never wedges"
- **Governs**: #1
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
- **Governs**: #2
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
- **Governs**: #3
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
- **Governs**: #3
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

## D-5: steering.md is a forward contract, not an archive — retire decisions on ship, cap State Notes
- **Governs**: #4
- **Issue**: The user asked whether repeating `/rn:up`/`/rn:dn` makes `steering.md` grow without
  bound, and to redefine its purpose so it does not. Measuring all six on-disk steering files settled
  what actually accumulates: `Decisions` is append-only (`dn` adds, nothing removes) but stays small
  in practice (1–4 per session, max 4); `State` is overwritten each cycle so it does **not** pile up
  across cycles, yet `dn` writes a multi-paragraph `Notes` (29–39 lines when paused) that every
  resume re-reads. So there are two distinct vectors: a slow cross-cycle one (`Decisions`) and a
  per-resume one (verbose `Notes`). A later `/rn:up` (2026-06-26) measured this session's own steering
  at 412 lines and found a **third** vector that Levers A+B leave untouched: `Tasks` (168 lines, the
  largest section) keeps every shipped task's full Purpose/Steps/Completion criteria, so finished work
  accumulates in the file's biggest section.
- **Conclusion**: Redefine `steering.md` as the **forward contract for the remaining work** — the
  minimum a resuming agent needs to finish the goal correctly — not the session's archive. Cut all
  three vectors structurally: **(A)** `Decisions` becomes a live working set; each decision carries a
  `Governs: #N` (or `—`) field, and `/rn:up`'s reconcile (Step 6) drops any decision whose every
  `Governs` task is checked off and shipped. **(B)** `/rn:dn` Step 3 caps `State → Notes` to a bounded
  forward pointer (branch/PR, next concrete action, open blockers, user-deferred paths), not a session
  re-narration. **(C)** `/rn:up`'s reconcile collapses a shipped task (box checked + `complete task #`
  marker in git) to a one-line `### #N: <name> — SHIPPED (#N in <sha>)` heading, dropping its Steps
  and Completion criteria; the next-task scan treats a `SHIPPED` task as done. The redefinition
  rationale goes to `rn/DESIGN.md`; the runtime files stay pure procedure.
  - **Delete-on-ship** was chosen for decisions (A) over archiving to a side file or
    keeping-but-skipping, because each decision is already committed when recorded (`record D-N …`),
    so git history + the PR are the durable system of record — an in-file archive would duplicate them.
  - **Collapse, not delete, for tasks (C).** A shipped *decision* is pure rationale with zero forward
    value once its work lands, so it is removed entirely. A shipped *task* is part of the goal's map:
    other tasks reference it (`Prerequisites: #N`), the numbering must stay stable, and a resuming
    agent needs the at-a-glance sense of what is already done. So a task is collapsed to a one-line
    `SHIPPED` pointer — kept as a map entry, its full body recoverable from the `complete task #`
    commit, `checks/{id}.md`, and the PR — rather than deleted.
- **Rationale**: A resuming agent needs only what is required to finish correctly; a decision whose
  work has shipped is no longer required for that, and its "why" is preserved in the commit that
  recorded it. The `Governs` field makes retirement a mechanical check (no prose re-reading) — the
  property is enforced by structure, not by a rule the agent must remember. Capping `Notes` removes
  the larger per-resume cost the data exposed: the narrative `dn` re-writes each cycle, which `git
  log` already holds. Collapsing shipped tasks (C) closes the same loophole on the largest section by
  the same logic — a finished task's Steps and criteria are not needed to finish the *remaining* work,
  and the same trigger Lever A uses (box checked + marker in git) drives it, so one reconcile pass
  prunes both. Keeping the rationale in `DESIGN.md` preserves D-2's pure-procedure runtime form.
- **Evidence**: Six on-disk steering files measured — `Decisions` count 1/1/2/3/3/4; completed
  sessions (`rn-rename2`, `experts-do-the-work`) show `State` reset to the 9–11-line placeholder
  (self-cleaning confirmed), while paused sessions show `State` at 29 (`subagent-execution`) and 39
  (`rn-update`) lines of narrative `Notes`. Each decision in this session was committed when recorded
  (`git log`: `record D-3`, `record D-4`), so deletion stays recoverable from history. The third
  vector (C) was measured 2026-06-26 on this steering at 412 lines: `Tasks` 168 lines (largest),
  `Decisions` 132, with #1–#4 all shipped-but-uncollapsed — Levers A+B leave the largest section
  untouched, and no `complete task #` marker is in git yet (nothing retired/collapsed), so 412 is the
  expected pre-ship peak, not unbounded growth.
- **Sources**: user feedback this session (2026-06-26); measurement of `.rn/*/steering.md` on
  `rn-update`; `dn/SKILL.md` Step 3, `up/SKILL.md` Step 6, `steering-template.md` (branch).

## D-6: Review gates sit at plan/design/evaluation; escalation is a separate always-open channel
- **Governs**: #6
- **Issue**: The user observed that user-review gates appear at every task (`task-workflow.md` Phase:
  Complete — N tasks, N gates) and judged this too many. Reading the actual gates confirmed a deeper
  imbalance: the plan has a strong gate (`on/SKILL.md` Step 5), but design has no dedicated gate and
  evaluation is only a weak "propose running Acceptance criteria" (`task-workflow.md` advance step).
  The workflow over-reviews execution increments and under-reviews the two judgments where human input
  is irreplaceable.
- **Conclusion**: Gate the points where human judgment is irreplaceable and a late error is expensive
  — **plan** (right problem/scope/breakdown), **design** (right approach/key decisions), **evaluation**
  (goal actually achieved). Exactly three scheduled gates; the per-task user gate is removed, because
  per-task quality is already covered independently by self-check + QA expert (+ language/SWE for code)
  + the coordinator's own diff review — the per-task user gate was redundant with that chain.
  **Gate and escalation are different categories, not rule-and-exception.** A *gate* is a scheduled
  stop-and-sign-off built into the flow. *Escalation* is an always-open, event-driven channel: whenever
  execution surfaces something that would change the agreed plan or design — a discovery, blocker, or
  scope/direction/taste call — the coordinator raises it to the user immediately, wherever it occurs.
  The two coexist; escalation is not a special case of a gate.
- **Rationale**: The per-task gate spent the user's attention on "is it done right" (which the expert
  chain answers) instead of "are we doing the right thing" (which only the user answers) — and the
  latter is exactly plan/design/evaluation. Removing it cuts the N-gate tax without losing oversight:
  the three gates cover direction and acceptance, and escalation — as its own channel — catches any
  mid-flight change to the agreed plan/design, so nothing important waits silently until evaluation.
  Keeping escalation distinct from gates (the user's correction) prevents re-smuggling a per-task gate
  back in as "the exception."
- **Evidence**: `task-workflow.md` Phase: Complete (per-task user gate); `on/SKILL.md` Step 5 (plan
  gate exists); `task-workflow.md` advance step (evaluation is a bare proposal); `task-workflow.md`
  Triage step's "User's call" branch (the seed of the escalation channel, today scoped only to review
  findings).
- **Sources**: user feedback this session (2026-06-26); the gate read above on `rn-update`.

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: —
- **Last completed**: —
- **Next**: —
- **Notes**: —
