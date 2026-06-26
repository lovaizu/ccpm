Design: rn/DESIGN.md (→ rn/design.md, renamed in #4)

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

(Terse end-states; the grounds for each are recorded in `checks/{id}.md`, per A2.)

- `/rn:dn` from a worktree with test-run residue ends with `git status --porcelain` empty; recurring
  test/build artifacts are gitignored (committed) so residue does not recur; no untracked path that is
  not clearly residue is auto-deleted — ambiguous paths are surfaced, user-deferred ones recorded in
  State, and the suspend always completes.
- `steering-template.md`'s completion-criteria guidance directs the two-questions-with-grounds form and
  contrasts an objective criterion against a result ("the output exists") one, keeping the existing
  constraints (third-party verifiable, no vague terms, outcomes-not-actions); `task-workflow.md`'s use
  of criteria as the review bar stays consistent.
- Every rn skill/reference is pure numbered procedure (no rationale or rule-justification prose); all
  prior behavior survives; the intent lives in `design.md`, not read at runtime.
- `steering.md` carries exactly Goal, Acceptance criteria, Rules, Tasks (remaining only), State, and a
  one-line `design.md` pointer — no Decisions section, no completed-task bodies, no change narration;
  `steering-template.md` encodes this shape. The earlier Governs field, SHIPPED-collapse, and
  retire-on-ship machinery are gone — the content is simply not stored, so nothing manages it.
- `/rn:on` decides the session's `design.md` location with the user (proposes a default, e.g.
  `.rn/{slug}/design.md`, lowercase filename) and writes its path into `steering.md`; design content
  goes there, not into steering. A session with no design leaves it absent and the design gate folds
  into the plan gate.
- The workflow has exactly three scheduled user gates — plan (`/rn:on`), design, evaluation — and no
  per-task user gate; per-task quality is covered by self-check + QA/expert + coordinator review.
  Escalation is specified as a separate always-open channel, not a gate's exception.
- `rn/design.md` (renamed from `DESIGN.md`) carries all intent; `rn/CHANGELOG.md` records the
  user-facing changes under `## [Unreleased]`, one line each; `version` in `plugin.json` stays `0.6.0`;
  no rn doc contradicts another (grep-verified).

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
relocated to `design.md`, not read at runtime. See `checks/2.md` (assembled).

**Completion criteria**:

- Each rn skill/reference is pure procedure; every prior behavior, branch, and fallback survives.
- `design.md` carries the removed intent and is not read at runtime; the runtime prompt surface drops
  materially with no behavior change.

### #3: Completion criteria as two questions + grounds — DONE through QA

**Purpose**: Reframe `steering-template.md`'s completion-criteria guidance to two questions answered
with grounds (objective achieved? new problems absent?), and trim the `dn` residue flow to a single
forward pass. See `checks/3.md`.

**Completion criteria**:

- The guidance directs the two-questions-with-grounds form plus an objective-vs-result contrast, keeps
  all three existing constraints, and stays consistent with `task-workflow.md`'s review-bar use.
- Any applied change keeps the pure-procedure form and is reflected in `design.md`.

### #4: steering is a lean forward contract; design moves to an external design.md — NOT STARTED

**Purpose**: Make `steering.md` carry only what a resuming agent needs — Goal, Acceptance criteria,
Rules, remaining Tasks, State, and a one-line `design.md` pointer — with all design intent in an
external `design.md` whose location `/rn:on` decides with the user. This **replaces** the earlier
non-accumulation approach (Governs / SHIPPED-collapse / retire-on-ship): instead of machinery to prune
content, the heavy content is never stored. See D-redesign in `design.md` (to be written).

**Prerequisites**: #2 (lands on the pure-procedure base)

**Steps**:

- [ ] In `rn/references/steering-template.md`, reduce the template to Goal, Acceptance criteria, Rules,
      Tasks, State + a top `Design:` pointer line; **remove the Decisions section** and its 5-field
      format; state that a decision lands in a task / `design.md` / a rule, and deliberation lives in
      git + the PR.
- [ ] Remove the earlier non-accumulation machinery: the `Governs` field and live-working-set/
      SHIPPED-collapse notes in `steering-template.md`, and the decision-retirement + task-collapse
      steps added to `rn/skills/up/SKILL.md` Step 6. `/rn:up` no longer manages accumulation — the
      content isn't there to manage.
- [ ] In `rn/skills/on/SKILL.md`, add a step (alongside the slug decision) to decide the session's
      `design.md` location with the user — propose a default `.rn/{slug}/design.md` (lowercase) and
      write the confirmed path into `steering.md`'s `Design:` line.
- [ ] Keep the `dn` State→Notes forward-pointer cap (the one part of the earlier work that survives).
- [ ] Rename `rn/DESIGN.md` → `rn/design.md`; update every reference (skills, references, README).
- [ ] Record the redesign intent in `rn/design.md`; runtime files stay pure procedure.
- [ ] self-check (`checks/4.md`) + QA expert review (subagent).

**Completion criteria**:

- `steering-template.md` encodes the 5-section + `Design:` pointer shape with no Decisions section; the
  earlier `Governs`/collapse/retire machinery is removed from the template and `up/SKILL.md`.
- `/rn:on` decides and records the `design.md` path with the user; design content lives there, not in
  steering; `rn/design.md` exists (renamed) with all references updated.

### #5: Record the changes and verify cross-doc consistency — to reconcile after #1–#4, #6

**Purpose**: Record the user-facing changes in `rn/CHANGELOG.md` and confirm the rn docs are internally
consistent. The existing `## [Unreleased]` lines (`checks/5.md`) are reconciled to the final shape of
#3/#4/#6.

**Prerequisites**: #1, #2, #3, #4, #6

**Completion criteria**:

- `rn/CHANGELOG.md` has one user-facing line per user-impacting change under `## [Unreleased]`, in user
  terms; the behavior-preserving #2 rewrite gets no entry.
- A grep over the rn docs finds no statement contradicting the current docs; `version` in
  `plugin.json` is `0.6.0`.

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

- `task-workflow.md` has no per-task user-review gate; a task completes via the self-check + QA/expert +
  coordinator chain and the check-off.
- Exactly three scheduled user gates exist — plan, design, evaluation — and escalation is specified as a
  separate always-open channel, not an exception to a gate; the design and evaluation gates each sign
  off their object before/at the right moment.

# State

(written by `/rn:dn`, read and reset to this placeholder by `/rn:up`. `Status` is `paused` while a
session is suspended — the signal `/rn:up` and `/rn:dn` search for — and resets to `not suspended`
here, so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: —
- **Last completed**: —
- **Next**: —
- **Notes**: —
