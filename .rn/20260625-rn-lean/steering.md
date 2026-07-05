Design: rn/docs/design.md

# Goal

Make the `rn` plugin lighter, and fix three issues that surfaced from real usage. Two threads.

**A — Fix three concrete issues:**

1. `/rn:dn` ends with a genuinely clean worktree — resolves test-run residue (gitignores recurring
   artifacts) and never silently deletes user-authored files.
2. Completion criteria express the work's *objective*, not its *result* — phrased as two questions a
   third party answers with grounds: is the objective achieved? are new problems absent?
3. Every rn skill/reference is pure procedural work-instruction; the "why" lives in `design.md`, not in
   the runtime prompts. (Precondition for judging A1/A2 on a clean base.)

**B — Lighten the rn process, which over-produces:**

4. `steering.md` is a lean forward contract — not a design doc, not an archive. It carries only Goal,
   Acceptance criteria, Rules, remaining Tasks, and State (handoff), plus a one-line pointer to the
   session's `design.md`. No Decisions section, no completed-task bodies, no change narration: a
   decision lands in a task / `design.md` / a rule, and deliberation + history live in git and the PR.
5. Review gates sit at the three points where human judgment is irreplaceable — **plan, design,
   evaluation** — not on every task. **Escalation** is a separate always-open channel: any execution
   discovery that would change the agreed plan or design is raised to the user immediately.

**C — Add the verdict commands and the PR-feedback workflow:**

6. Every rn user-confirmation is answered with two console commands: **`ty`** (approve what was asked)
   and **`gm`** ("good, more" — revise). `gm`'s feedback is its argument; with no argument, the feedback
   is the PR's review comments. They are the single accept/revise vocabulary at every gate and
   confirmation point — the verdict is the user's, so it is a command the user runs, never something the
   system infers.
7. PR feedback is processed by a documented light loop (`pr-feedback-workflow.md`): collect the
   unresolved review threads whose last comment is the author's, hand them to an execution subagent one
   at a time — each either addresses the thread, pushes, and replies with the commit link, or replies
   with a question — and the coordinator reviews each result before the next. Verification is
   deliberately light (one coordinator pass, not the QA-expert/multi-round chain). A thread is resolved
   only by its author.

**D — Reduce the user's context load at stops:**

8. Every point rn stops for the user's input opens with a compact session-status block — goal
   one-liner, ✅ completed tasks (grouped), 👉 the current task and what is being asked, ⬜ remaining
   tasks (omitted when none) with a parenthesized outlook — so the user grasps the session's
   before/after without reading `steering.md` or asking.

The change set is documentation/prompt edits to the `rn` plugin only. No runtime code.

# Acceptance criteria

(Each is an objective to confirm — the aim achieved and new problems absent — not a description of the
edit made. The means are in the tasks' Steps; the grounds are recorded in `checks/{id}.md`, per A2.)

- **dn clean tree.** Running `/rn:dn` in a worktree dirtied only by test/build residue leaves the tree
  genuinely clean (`git status --porcelain` empty) and a later test run does not re-dirty it; the
  suspend still completes when an untracked path is left unresolved, and no untracked path the user did
  not approve is deleted. (Failure modes absent: residue keeps the tree dirty; the suspend wedges; user
  work is destroyed.)
- **Criteria verify objectives.** Completion criteria written under the revised guidance read as
  objective-achievement (aim met + new problems absent), not as "the output was produced" —
  demonstrable on this steering's own criteria. The prior constraints still hold (third-party
  verifiable, no vague terms, outcomes-not-actions) and `task-workflow.md` still uses criteria as the
  review bar. (Failure mode absent: a criterion satisfied by the artifact merely existing.)
- **Prompts run without rationale.** An agent can execute any rn skill/reference with no rationale prose
  present, and the workflow behaves exactly as before the rewrite; the intent stays recoverable from
  `design.md`. (Failure mode absent: a rule/branch/fallback lost in the conversion.)
- **steering is a sufficient, minimal forward contract.** A resuming agent can finish the goal correctly
  from `steering.md` plus what it points to (git, PR, `design.md`), with nothing required missing, while
  steering holds no design rationale, no completed-task bodies, and no change narration; the template
  enforces this shape and no accumulation-managing machinery exists, because the content is never stored
  — demonstrable on this steering. (Failure modes absent: a resume blocked by missing context; steering
  re-growing into a design doc/archive.)
- **Design lives where the user chose, in whole-structure form.** For an rn session, the design is found
  at a path the user agreed at start and named in steering, not inside steering, and is a whole-structure
  doc — decisions and how the parts fit, produced from a design template, not per-step rationale. The
  doc-division (requirements/criteria → steering, structure → `design.md`, UX → README) lives in
  `steering-template` and `/rn:on` applies it at planning; a session with no design has none and the
  design gate folds into the plan gate. (Failure modes absent: design content scattered into steering; an
  empty `design.md` forced on a session that has none; per-step memos returning; the doc-division
  contradicting across `on` / `steering-template` / README.)
- **The user is consulted only where judgment is irreplaceable.** The user signs off at plan, design,
  and evaluation only — not per task — and no change to the agreed plan or design proceeds without
  reaching the user mid-flight via escalation; per-task quality is still caught by self-check +
  QA/expert + coordinator review. (Failure modes absent: a surviving per-task user gate; a fourth or
  missing scheduled gate; escalation collapsed into a gate's exception so a mid-flight change ships
  unseen.)
- **The record is honest and consistent.** A user reading `rn/CHANGELOG.md` learns each user-facing
  change and why it helps; no rn doc contradicts another; `version` is `0.7.0` matching the finalized
  `## [0.7.0] - 2026-07-05` CHANGELOG section (release instructed 2026-07-05). (Failure modes absent:
  a behavior-preserving refactor listed or a real change missing; a surviving contradictory
  instruction; a version/CHANGELOG mismatch or an empty `## [Unreleased]` left behind.)
- **Two-command verdict vocabulary.** `ty` and `gm` exist as rn skills: `ty` registers approval of what
  was asked; `gm` registers a revise verdict whose feedback is its argument, or — with no argument — the
  PR's review comments. Every scheduled gate (plan/design/evaluation) and every assistant-asks-to-confirm
  point resolves through these two, and the assistant records no verdict the user did not issue. (Failure
  modes absent: a verdict command that performs nothing; `gm` ignoring its argument or failing to locate
  the PR comments; a confirmation point still using a bespoke yes/no.)
- **PR feedback runs as a light, reviewable loop.** `pr-feedback-workflow.md` drives it: collect the
  unresolved review threads whose last comment is the author's; dispatch one at a time to an execution
  subagent; each thread ends either addressed-pushed-and-replied-with-its-commit-link or answered with a
  question; the coordinator reviews each subagent result before the next is dispatched, and the loop
  re-runs safely to pick up the author's follow-ups. (Failure modes absent: parallel dispatch dropping
  the per-item review gate; a thread changed but left without a reply; the QA-expert/multi-round chain
  creeping back into this loop.)
- **Threads are resolved only by their author.** No assistant or subagent marks a review thread
  resolved; resolution is the reviewer's act, and the loop treats GitHub's unresolved state as its queue.
  (Failure mode absent: the assistant auto-resolving a thread it answered.)
- **Session status arrives at every stop.** Every point rn stops for the user's input while a session
  is active (its `steering.md` exists and is identified) opens with the session-status block
  (✅ completed grouped / 👉 current task + the ask / ⬜ remaining, omitted when empty, with a
  parenthesized outlook), derived from `steering.md` at emit time — demonstrable on this session's own
  #15 re-presentation; stops before a session's steering exists are explicitly scoped out in the spec.
  (Failure modes absent: an in-session stop that asks without the block; a block whose content still
  sends the user to `steering.md`; a block contradicting steering's actual state; docs claiming
  coverage the wiring does not deliver.)

# Rules

- edits stay within the `rn/` plugin (skills, references, `design.md`, CHANGELOG); touch no other plugin
- release instructed by the user on 2026-07-05: `version` bumps `0.6.0` → `0.7.0` and the CHANGELOG's
  `## [Unreleased]` finalizes to `## [0.7.0] - 2026-07-05` per `plugin.md` (supersedes the original
  "no release in scope" rule)
- the plugin set is unchanged, so `marketplace.json` and the root `README.md` need no update
- prose/prompt edits only (no executable code) → non-code verification chain (self-check → QA expert →
  the gates)
- this steering must itself follow the lean form it introduces (dogfood B4)
- `ty`/`gm` are the only verdict vocabulary at every confirmation point; the assistant never infers a verdict the user did not issue
- only a review thread's author resolves it; the assistant/subagent never resolves a thread

# Tasks

(Completed tasks are kept compact — full bodies and QA trails live in their `checks/{id}.md` and git.
#15 is the session's own Evaluation sign-off task, placed last per #14's rule, added by escalation
during `/rn:up`; #16 was added by escalation on user request during the PR-feedback stage and ran
before #15 so the sign-off re-presentation carries the block. Numbering is preserved so
`checks/{id}.md` stay aligned.)

### #1: `/rn:dn` ends with a genuinely clean worktree — DONE through QA

**Purpose**: A suspend resolves test-run residue and finishes with a truly clean tree, never silently
deleting user-authored files. See `checks/1.md`.

**Completion criteria**:

- Given a worktree whose only residue is recurring test/build artifacts, the revised `dn` flow ends
  with `git status --porcelain` empty (residue gitignored away), and a committed repo-root `.gitignore`
  rule stops it recurring.
- No untracked path is auto-deleted; an ambiguous one is surfaced, never silenced; a user-deferred path
  is recorded in State and the suspend completes anyway (it never loops/wedges).

### #2: Proceduralize all rn prompts; move intent to design.md — DONE through QA

**Purpose**: Every rn skill/reference is pure numbered procedure with behavior preserved; the "why" is
relocated to `design.md` (whole-structure form per #4 / `design-template`, not per-step memos), not read
at runtime. See `checks/2.md` (assembled).

**Completion criteria**:

- An agent executes any rn skill/reference with no rationale prose present and the workflow behaves as
  before the rewrite (failure mode absent: a lost rule/branch/fallback); the intent stays recoverable
  from `design.md`, which is not read at runtime.

### #3: Completion criteria as two questions + grounds — DONE through QA

**Purpose**: Reframe `steering-template.md`'s completion-criteria guidance to two questions answered
with grounds (objective achieved? new problems absent?), and trim the `dn` residue flow to a single
forward pass. See `checks/3.md`.

**Completion criteria**:

- Completion criteria written under the revised guidance verify objective-achievement, not result
  (demonstrable on this steering's own criteria), keeping the three prior constraints and staying
  consistent with `task-workflow.md` (failure mode absent: a criterion met by the artifact merely
  existing).
- The trimmed `dn` flow is a single forward pass that still ends clean and never wedges (failure mode
  absent: a residue tree left dirty, or a suspend that loops).

### #4: steering is a lean forward contract; design becomes a whole-structure doc from a template — DONE through QA; awaiting consolidated PR review

**Purpose**: Reduce `steering.md` to the forward contract (Goal, Acceptance criteria, Rules, Tasks,
State + a `Design:` pointer), move design intent to an external whole-structure `design.md` built from
the new `design-template.md`, and place the doc-division rule in `steering-template.md` — replacing the
earlier non-accumulation machinery (heavy content is never stored, not pruned). See `checks/4.md`.

**Completion criteria**:

- A resuming agent finishes the goal from the new `steering.md` plus what it points to, nothing required
  missing, while steering holds no design rationale, no completed-task bodies, and no change narration;
  the template enforces the shape and the earlier `Governs`/collapse/retire machinery no longer exists
  because the content is never stored (failure modes absent: a resume blocked by missing context;
  steering re-growing into a design doc/archive).
- The session's design is found at the path steering names — decided with the user at `/rn:on` — not
  inside steering, and is a whole-structure doc produced from `design-template` (decisions + how the
  parts fit, no per-step rationale); `rn/docs/design.md` is a conforming instance with every reference
  resolving, and the doc-division rule lives in `steering-template` with `/rn:on` applying it (failure
  modes absent: a dangling or empty design reference; per-step memos returning; design content left in
  steering; the doc-division contradicting across `on` / `steering-template` / README).

### #5: Record the changes and verify cross-doc consistency — DONE through QA

**Purpose**: Record the user-facing changes in `rn/CHANGELOG.md` (the `gm`/`ty` commands and the
PR-feedback loop included), record the verdict-command + FB-workflow structure in `rn/docs/design.md`,
and verify cross-doc consistency. See `checks/5.md`.

**Completion criteria**:

- A user reading `rn/CHANGELOG.md` learns each user-facing change and why it helps — the `gm`/`ty`
  commands and the PR-feedback loop included, the behavior-preserving #2 rewrite excluded;
  `rn/docs/design.md` records the verdict-command + FB-workflow structure; no rn doc contradicts another;
  `version` is `0.6.0` (failure modes absent: a refactor listed or a real change missing; a surviving
  contradiction; an accidental release).

### #16: Session-status block at every user stop — DONE through QA

**Purpose**: Open every rn stop for user input with a compact session map (✅ done / 👉 now / ⬜ ahead),
specified in `rn/references/status-display.md` and wired into every stop point. Added by escalation
(user request during the PR-feedback stage). See `checks/16.md`.

**Completion criteria**:

- Every rn stop for user input while a session is active (its `steering.md` exists and is identified)
  opens with the status block per `status-display.md` — no in-session stop asks without it, the block
  alone conveys done / current / remaining plus the ask, and stops outside an active session (before
  steering exists, or none identified) are explicitly scoped out in the spec (failure modes absent: an
  in-session stop missing the block; a block that still requires opening `steering.md`; the ⬜ section
  rendered when nothing remains; a doc claiming coverage the wiring does not deliver).
- The record is consistent: CHANGELOG lists the feature, `design.md` records the structure, README's
  scenario shows it, and no rn doc contradicts another (failure mode absent: a stop-point instruction
  left contradicting `status-display.md`).

### #15: Evaluation sign-off — user approves the Acceptance criteria run

**Purpose**: This session's closing user gate, placed last per its own #14 rule: present the Acceptance
criteria run result and take the verdict via `/rn:ty` (approve) or `/rn:gm` (revise → address the
feedback, re-present).

**Prerequisites**: #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12, #13, #14, #16

**Steps**:

- [x] Run this `steering.md`'s Acceptance criteria section against the current state of the branch/PR
      and record the result per criterion (achieved / not, with grounds — failure modes present or
      absent). — run posted as PR #14 comment (10 OK / 1 NG on criterion 4):
      https://github.com/lovaizu/ccpm/pull/14#issuecomment-4880711175
- [ ] Present the result to the user and take the verdict via `/rn:ty` (approve → session done) or
      `/rn:gm` (revise → address the feedback, re-run the affected criteria, re-present).

**Completion criteria**:

- The user has reviewed the Acceptance-criteria run and approved via `/rn:ty`, or the revise/re-present
  loop ran until approved (failure modes absent: the session closing without this sign-off; a verdict
  recorded that the user did not issue).

### #6: Review gates → plan/design/evaluation; escalation as a separate channel — DONE through QA; awaiting consolidated PR review

**Purpose**: Move the user-review gates to the three points where human judgment is irreplaceable
(plan, design, evaluation), remove the per-task user gate, and specify escalation as a distinct
always-open channel. See `checks/6.md`.

**Completion criteria**:

- The user is consulted only at plan, design, and evaluation — not per task — and no change to the
  agreed plan or design proceeds without reaching the user mid-flight via escalation, a separate
  always-open channel and not a gate's exception; per-task quality is still caught by self-check +
  QA/expert + coordinator review (failure modes absent: a surviving per-task user gate; a fourth or
  missing scheduled gate; escalation collapsed into an exception so a mid-flight change ships unseen).

### #7: `gm` skill — the revise / feedback verdict command — DONE through QA

**Purpose**: Add `rn/skills/gm/SKILL.md`, the "good, more" revise verdict command — its argument is the
feedback to act on; with no argument, the current PR's review comments via `pr-feedback-workflow.md`.
See `checks/7.md`.

**Completion criteria**:

- `/rn:gm <text>` acts on `<text>` as the feedback; `/rn:gm` with no argument processes the current PR's
  review comments through the FB workflow; both register a revise verdict and drop nothing (failure modes
  absent: the argument ignored; no-argument `gm` not locating/processing the PR comments; `gm` a no-op).

### #8: `ty` skill — the approve verdict command — DONE through QA

**Purpose**: Add `rn/skills/ty/SKILL.md`, the approve verdict command — registers approval of whatever
the assistant last asked the user to confirm, and the flow advances. See `checks/8.md`.

**Completion criteria**:

- `/rn:ty` registers approval of the pending confirmation and the flow advances (the gate passes / the
  item is accepted), with no revision performed (failure modes absent: `ty` a no-op; `ty` triggering a
  revise).

### #9: `pr-feedback-workflow.md` — the light PR-feedback loop — DONE through QA

**Purpose**: Add `rn/references/pr-feedback-workflow.md`, the light PR-feedback loop: collect the
unresolved threads whose last comment is the author's, dispatch one at a time to an execution subagent,
coordinator review between each, resolution left to the author. See `checks/9.md`.

**Completion criteria**:

- An agent runs the loop from the reference alone: it collects exactly the unresolved threads whose last
  comment is the author's, processes them one at a time with a coordinator review between each, and each
  thread ends addressed-and-replied-with-its-commit-link or answered with a question; resolution is left
  to the author; verification is the single coordinator pass (failure modes absent: a thread dispatched
  past the review gate in parallel; a thread changed without a reply; the heavy QA chain present; the
  assistant resolving a thread).

### #10: Wire the gates + escalation to `gm`/`ty`; state the resolve-by-author rule — DONE through QA

**Purpose**: Connect the three scheduled gates and the escalation channel to the `gm`/`ty` verdict
vocabulary across `on`/`up`/`task-workflow`, and state the resolve-by-author rule where review threads
are handled. See `checks/10.md`.

**Completion criteria**:

- Every scheduled gate and confirmation point in `on`/`up`/`task-workflow` resolves through `/rn:ty` or
  `/rn:gm`, the assistant records no verdict the user did not issue, and the resolve-by-author rule is
  stated where threads are handled (failure modes absent: a gate with an inferred or bespoke verdict; a
  thread the docs let the assistant resolve).

### #11: Extract `planning-workflow.md`; `on` becomes a thin orchestrator — DONE through QA

**Purpose**: Extract `on/SKILL.md`'s planning Steps 1–5 into `rn/references/planning-workflow.md`;
`on/SKILL.md` becomes an order-only orchestrator (parse the goal, run planning, begin task #1). See
`checks/11.md`.

**Completion criteria**:

- Running `/rn:on` behaves exactly as before the extraction (same prompts, same plan-gate sign-off via
  `/rn:ty`/`/rn:gm`, same `steering.md` produced) with all planning detail now living in
  `planning-workflow.md` and `on/SKILL.md` reduced to order-only orchestration (failure modes absent: a
  planning step lost in the move; `on/SKILL.md` still carrying step-level rationale or detail).

### #12: Split `task-workflow.md` into `task-execute-workflow.md` + `task-verify-workflow.md` — DONE through QA

**Purpose**: Split `task-workflow.md` along its Phase boundaries into `task-execute-workflow.md` and
`task-verify-workflow.md` (shared header duplicated into both, no third file), updating every reference
to the deleted file. See `checks/12.md`.

**Completion criteria**:

- A coordinator runs one task end-to-end by reading `task-execute-workflow.md` then
  `task-verify-workflow.md` in sequence, with behavior identical to the pre-split `task-workflow.md`
  (same gates, same escalation channel, same check-off marker); no file in `rn/` still points at the
  deleted `task-workflow.md` (failure modes absent: a rule/step dropped at the seam; a dangling
  reference).

### #13: Redefine the expert set — design / craft (per medium) / verification (per medium) + QA — DONE through QA

**Purpose**: Replace the fixed code-centric expert trio with function-axis experts — design / craft
(per medium) / verification (per medium) — with QA cross-cutting every task; which axes spawn is a
per-task judgment. See `checks/13.md`.

**Completion criteria**:

- Every place `rn/` names a review expert uses the design/craft/verification+QA axes, with which axes
  spawn stated as a per-task judgment keyed to what the task produces (not a fixed code/non-code
  branch); no reference to "language expert" or "software-engineering expert" survives, and the same
  axes that build a task also review it (failure modes absent: the old trio surviving anywhere; an axis
  that never fits prose/prompts/slides forced onto a non-code task).

### #14: Reposition design/evaluation gates as sign-off tasks placed by planning — DONE through QA

**Purpose**: Make the design and evaluation gates sign-off tasks placed by `planning-workflow.md`, not
logic hardcoded in `on` or `task-verify-workflow.md`; the plan gate stays planning's own closing
hand-off (never a task). See `checks/14.md`.

**Completion criteria**:

- A session's `steering.md` carries the design sign-off (when needed) and evaluation sign-off as
  ordinary tasks placed by planning, each gated on `/rn:ty`/`/rn:gm`; `on`/`task-verify-workflow.md`
  contain no hardcoded gate branch for either (failure modes absent: a session finishing without an
  evaluation sign-off task; the plan gate turned into a self-approving task).

# State

(written by `/rn:dn`, read and reset to this placeholder by `/rn:up`. `Status` is `paused` while a
session is suspended — the signal `/rn:up` and `/rn:dn` search for — and resets to `not suspended`
here, so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
