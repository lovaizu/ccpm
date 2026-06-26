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
  change and why it helps; no rn doc contradicts another; `version` stays `0.6.0`. (Failure modes
  absent: a behavior-preserving refactor listed or a real change missing; a surviving contradictory
  instruction; an accidental release.)

# Rules

- edits stay within the `rn/` plugin (skills, references, `design.md`, CHANGELOG); touch no other plugin
- do not bump `version` in `plugin.json` — no release instruction is in scope (stays `0.6.0`)
- the plugin set is unchanged, so `marketplace.json` and the root `README.md` need no update
- prose/prompt edits only (no executable code) → non-code verification chain (self-check → QA expert →
  the gates)
- this steering must itself follow the lean form it introduces (dogfood B4)

# Tasks

(#1–#3 are done through QA on the branch, awaiting the new gates — kept compact, full bodies in their
`checks/{id}.md` and git. #4 and #6 carry the B-thread redesign. #5 reconciles the record. Numbering is
preserved so `checks/{id}.md` stay aligned.)

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

### #4: steering is a lean forward contract; design becomes a whole-structure doc from a template — NOT STARTED

**Purpose**: Make `steering.md` carry only what a resuming agent needs — Goal, Acceptance criteria,
Rules, remaining Tasks, State, and a one-line `design.md` pointer — with design intent in an external
`design.md` whose location `/rn:on` decides with the user. Introduce a **design-doc template** so every
`design.md` is a *whole-structure* doc (context/constraints → approach → actors + structure → flow →
open questions) — decisions and how the parts fit, never per-step rationale. The **doc-division** rule
(requirements/criteria → `steering`, structure → `design.md`, UX → `README`) lives in
`steering-template` and `/rn:on` applies it when allocating content at planning. This **replaces** the
earlier non-accumulation approach (Governs / SHIPPED-collapse / retire-on-ship): heavy content is never
stored, not pruned. See `rn/docs/design.md`.

**Prerequisites**: #2 (lands on the pure-procedure base)

**Steps**:

- [x] In `rn/references/steering-template.md`, reduce the template to Goal, Acceptance criteria, Rules,
      Tasks, State + a top `Design:` pointer line; **remove the Decisions section** and its 5-field
      format; **add the doc-division working rule** (requirements/criteria → steering, structure →
      `design.md`, UX → README); state that a decision lands in a task / `design.md` / a rule, and
      deliberation lives in git + the PR.
- [x] Remove the earlier non-accumulation machinery: the `Governs` field and live-working-set/
      SHIPPED-collapse notes in `steering-template.md`, and the decision-retirement + task-collapse
      steps added to `rn/skills/up/SKILL.md` Step 6. `/rn:up` no longer manages accumulation — the
      content isn't there to manage.
- [x] Add `rn/references/design-template.md` (new): five sections — **Context & constraints** /
      **Approach** (decisions + rejected alternative) / **Structure** (actors + wiring, with a diagram)
      / **Flow** / **Open questions**. No preamble guard — each section's form (why-less tables, a
      numbered sequence) forecloses per-step memos structurally.
- [x] In `rn/skills/on/SKILL.md`: alongside the slug, decide the session's `design.md` location
      (default `.rn/{slug}/design.md`, lowercase) and write it into the `Design:` line; read the
      doc-division rule + `design-template` and allocate content at planning; drop `Decisions` from
      Step 3's placeholder line; force no empty `design.md` on a session that has none (its design gate
      folds into the plan gate).
- [x] Keep the `dn` State→Notes forward-pointer cap (the one part of the earlier work that survives).
- [x] Relocate the plugin design doc to `rn/docs/design.md` (done — lowercase, under `docs/`).
- [x] Rewrite `rn/docs/design.md` as a conforming instance of `design-template` (whole-structure),
      dropping all per-step memos — including the `up`/`task-workflow` memos that describe the
      now-removed retire/collapse machinery; runtime files stay pure procedure.
- [ ] self-check (`checks/4.md`) + QA expert review (subagent) + grep cross-doc consistency (no stray
      `Decisions` / per-task `user review` / retire-collapse references). — self-check done; QA round 1
      PASS (`17e2cfe`), two minor fixes in `30f8fc1`; **re-QA of the fixes + user review still pending**.

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

### #5: Record the changes and verify cross-doc consistency — to reconcile after #1–#4, #6

**Purpose**: Record the user-facing changes in `rn/CHANGELOG.md` and confirm the rn docs are internally
consistent. The existing `## [Unreleased]` lines (`checks/5.md`) are reconciled to the final shape of
#3/#4/#6.

**Prerequisites**: #1, #2, #3, #4, #6

**Completion criteria**:

- A user reading `rn/CHANGELOG.md` learns each user-facing change and why it helps, with the
  behavior-preserving #2 rewrite absent; no rn doc contradicts another; `version` is `0.6.0` (failure
  modes absent: a refactor listed or a real change missing; a surviving contradiction; an accidental
  release).

### #6: Review gates → plan/design/evaluation; escalation as a separate channel — NOT STARTED

**Purpose**: Move the workflow's user-review gates to the three points where human judgment is
irreplaceable (plan, design, evaluation), remove the per-task user gate, and specify escalation as a
distinct always-open channel.

**Prerequisites**: #2, #4 (lands on the lean-steering + pure-procedure base)

**Steps**:

- [ ] In `rn/references/task-workflow.md`, remove the per-task user-review gate from Phase: Complete; a
      task completes via self-check + QA/expert + coordinator review + check-off. Keep the coordinator's
      independent diff review and the expert reviews intact.
- [ ] Generalize the existing "User's call" triage into an explicit **escalation** channel: any
      execution discovery/blocker/call that would change the agreed plan or design is surfaced to the
      user immediately, wherever it occurs — stated as a channel distinct from the gates, not an
      exception to one.
- [ ] Add the **design gate**: a scheduled user sign-off on the approach/key decisions before they are
      built on, distinct from reviewing a task's deliverable (folds into the plan gate when design is
      settled at plan time; a separate stop before heavy build when it is not).
- [ ] Strengthen the **evaluation gate**: make the end-of-session Acceptance-criteria run a user
      sign-off in `on`/`up`/`task-workflow` advance, not a bare proposal.
- [ ] Confirm the **plan gate** in `rn/skills/on/SKILL.md` stays and is named as one of the three.
- [ ] Record the gate-vs-escalation model in `rn/design.md`; runtime files stay pure procedure.
- [ ] self-check (`checks/6.md`) + QA expert review (subagent) + grep cross-doc consistency.

**Completion criteria**:

- The user is consulted only at plan, design, and evaluation — not per task — and no change to the
  agreed plan or design proceeds without reaching the user mid-flight via escalation, a separate
  always-open channel and not a gate's exception; per-task quality is still caught by self-check +
  QA/expert + coordinator review (failure modes absent: a surviving per-task user gate; a fourth or
  missing scheduled gate; escalation collapsed into an exception so a mid-flight change ships unseen).

# State

(written by `/rn:dn`, read and reset to this placeholder by `/rn:up`. `Status` is `paused` while a
session is suspended — the signal `/rn:up` and `/rn:dn` search for — and resets to `not suspended`
here, so only a genuinely suspended session reads `paused`.)

- **Status**: paused
- **Date**: 2026-06-26
- **Last completed**: #4 deliverable + both fix rounds, pushed. Commits `17e2cfe` (lean steering +
  design-template + design.md rewrite) and `30f8fc1` (two QA fixes: dn Step 2 adds tasks only;
  no-design omits the `Design:` line). Self-check + QA round 1 (PASS, both criteria) recorded in
  `checks/4.md`.
- **Next**: Finish #4's verify step. (1) Re-run the QA expert (subagent) on just the two fixes in
  `30f8fc1` — dn Step 2 wording and the no-design `Design:`-line omission — to close round 2; record
  the verdict in `checks/4.md` QA columns. (2) Then user review on PR #14 (the task gate, on the PR
  per push-and-review rule) — DO NOT mark #4 complete or write the `complete task #4` marker until the
  user approves. After #4: #6 (move review gates to plan/design/evaluation + escalation channel), then
  #5 (CHANGELOG + cross-doc consistency).
- **Notes**: branch `rn-update`, PR #14 (draft), all pushed; tree clean. No `complete task #` markers
  in git yet (none of #1–#6 formally checked off). #1–#3 done-through-QA on the branch, re-verify under
  the new gates when #6 lands. checks/4.md is the coordinator's ledger (committed with this suspend).
  Pre-existing, out-of-scope: `claude plugin validate rn --strict` fails on `rn/skills/dn/SKILL.md`
  frontmatter YAML (reproduces without #4's changes) — flag for a separate fix, not part of #4. The
  CHANGELOG `[Unreleased]` line was updated in `17e2cfe` to drop the removed-machinery description;
  #5 still owns final CHANGELOG reconciliation across #3/#4/#6.
