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

# Rules

- edits stay within the `rn/` plugin (skills, references, `design.md`, CHANGELOG); touch no other plugin
- do not bump `version` in `plugin.json` — no release instruction is in scope (stays `0.6.0`)
- the plugin set is unchanged, so `marketplace.json` and the root `README.md` need no update
- prose/prompt edits only (no executable code) → non-code verification chain (self-check → QA expert →
  the gates)
- this steering must itself follow the lean form it introduces (dogfood B4)
- `ty`/`gm` are the only verdict vocabulary at every confirmation point; the assistant never infers a verdict the user did not issue
- only a review thread's author resolves it; the assistant/subagent never resolves a thread

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

### #4: steering is a lean forward contract; design becomes a whole-structure doc from a template — DONE through QA; awaiting consolidated PR review

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
- [x] self-check (`checks/4.md`) + QA expert review (subagent) + grep cross-doc consistency (no stray
      `Decisions` / per-task `user review` / retire-collapse references). — self-check done; QA round 1
      PASS (`17e2cfe`), two minor fixes in `30f8fc1`; QA round 2 PASS, nit fixed in `ace2f07`, re-review
      PASS. User review batched to the consolidated PR review (per user direction) — completion marker
      held until then.

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

### #5: Record the changes and verify cross-doc consistency — to reconcile after #1–#4, #6–#14

**Purpose**: Record the user-facing changes in `rn/CHANGELOG.md` (including the `gm`/`ty` commands and
the PR-feedback loop), record the verdict-command + FB-workflow structure in `rn/docs/design.md`, and
confirm the rn docs are internally consistent. The existing `## [Unreleased]` lines (`checks/5.md`) are
reconciled to the final shape of #3/#4/#6–#14.

**Prerequisites**: #1, #2, #3, #4, #6, #7, #8, #9, #10, #11, #12, #13, #14

**Completion criteria**:

- A user reading `rn/CHANGELOG.md` learns each user-facing change and why it helps — the `gm`/`ty`
  commands and the PR-feedback loop included, the behavior-preserving #2 rewrite excluded;
  `rn/docs/design.md` records the verdict-command + FB-workflow structure; no rn doc contradicts another;
  `version` is `0.6.0` (failure modes absent: a refactor listed or a real change missing; a surviving
  contradiction; an accidental release).

### #6: Review gates → plan/design/evaluation; escalation as a separate channel — DONE through QA; awaiting consolidated PR review

**Purpose**: Move the workflow's user-review gates to the three points where human judgment is
irreplaceable (plan, design, evaluation), remove the per-task user gate, and specify escalation as a
distinct always-open channel.

**Prerequisites**: #2, #4 (lands on the lean-steering + pure-procedure base)

**Steps**:

- [x] In `rn/references/task-workflow.md`, remove the per-task user-review gate from Phase: Complete; a
      task completes via self-check + QA/expert + coordinator review + check-off. Keep the coordinator's
      independent diff review and the expert reviews intact.
- [x] Generalize the existing "User's call" triage into an explicit **escalation** channel: any
      execution discovery/blocker/call that would change the agreed plan or design is surfaced to the
      user immediately, wherever it occurs — stated as a channel distinct from the gates, not an
      exception to one.
- [x] Add the **design gate**: a scheduled user sign-off on the approach/key decisions before they are
      built on, distinct from reviewing a task's deliverable (folds into the plan gate when design is
      settled at plan time; a separate stop before heavy build when it is not).
- [x] Strengthen the **evaluation gate**: make the end-of-session Acceptance-criteria run a user
      sign-off in `on`/`up`/`task-workflow` advance, not a bare proposal.
- [x] Confirm the **plan gate** in `rn/skills/on/SKILL.md` stays and is named as one of the three.
- [x] Record the gate-vs-escalation model in `rn/docs/design.md`; runtime files stay pure procedure.
- [x] self-check (`checks/6.md`) + QA expert review (subagent) + grep cross-doc consistency. — self-check
      OK; QA round 1 NG (1 blocking README defect + 1 nit, both fixed in `de1f835`), round 2 PASS;
      coordinator review PASS. User review batched to the consolidated PR review (per user direction) —
      completion marker held until then.

**Completion criteria**:

- The user is consulted only at plan, design, and evaluation — not per task — and no change to the
  agreed plan or design proceeds without reaching the user mid-flight via escalation, a separate
  always-open channel and not a gate's exception; per-task quality is still caught by self-check +
  QA/expert + coordinator review (failure modes absent: a surviving per-task user gate; a fourth or
  missing scheduled gate; escalation collapsed into an exception so a mid-flight change ships unseen).

### #7: `gm` skill — the revise / feedback verdict command — DONE through QA

**Purpose**: Add `rn/skills/gm/SKILL.md`, the "good, more" verdict command. With an argument, the
argument is the feedback to act on; with no argument, the feedback source is the current PR's review
comments and the command runs `pr-feedback-workflow.md`. Either way it registers a revise verdict at the
pending confirmation point.

**Prerequisites**: #9 (no-argument `gm` routes into the FB workflow)

**Steps**:

- [x] Add `rn/skills/gm/SKILL.md`: frontmatter (`name: gm`, one-line `description`); procedure — argument
      present → treat it as the feedback and act on it; argument absent → run `pr-feedback-workflow.md`
      against the current PR's review comments.
- [x] Confirm the skill resolves as `/rn:gm` (plugin skill namespace = `rn`). — frontmatter matches `on`/`dn`; YAML clean.
- [x] self-check (`checks/7.md`) + QA expert review (subagent) + grep cross-doc consistency. — self-check
      OK; QA PASS, two minor edge guards (blank-arg trim, cold-run fallback) added in `0e88ea8`.

**Completion criteria**:

- `/rn:gm <text>` acts on `<text>` as the feedback; `/rn:gm` with no argument processes the current PR's
  review comments through the FB workflow; both register a revise verdict and drop nothing (failure modes
  absent: the argument ignored; no-argument `gm` not locating/processing the PR comments; `gm` a no-op).

### #8: `ty` skill — the approve verdict command — DONE through QA

**Purpose**: Add `rn/skills/ty/SKILL.md`, the approve verdict command. Running it registers approval of
whatever the assistant last asked the user to confirm — a gate sign-off or a reviewed result — and the
flow advances.

**Prerequisites**: none

**Steps**:

- [x] Add `rn/skills/ty/SKILL.md`: frontmatter (`name: ty`, one-line `description`); procedure — register
      approval of the pending confirmation and proceed (pass the gate / mark the reviewed item accepted).
- [x] Confirm the skill resolves as `/rn:ty`. — frontmatter matches the `on`/`dn` shape; YAML clean.
- [x] self-check (`checks/8.md`) + QA expert review (subagent) + grep cross-doc consistency. — self-check
      OK; QA PASS with one should-fix (ambiguous approval target), fixed in `0a09993`.

**Completion criteria**:

- `/rn:ty` registers approval of the pending confirmation and the flow advances (the gate passes / the
  item is accepted), with no revision performed (failure modes absent: `ty` a no-op; `ty` triggering a
  revise).

### #9: `pr-feedback-workflow.md` — the light PR-feedback loop — DONE through QA

**Purpose**: Add `rn/references/pr-feedback-workflow.md`, a sibling of `task-workflow.md` that processes
PR review feedback: collect unresolved threads whose last comment is the author's; dispatch one at a time
to an execution subagent; each subagent either addresses→pushes→replies-with-the-commit-link or
replies-with-a-question; the coordinator reviews each result before the next. Verification is one
coordinator pass (not the QA-expert/multi-round chain); threads are resolved only by their author.

**Prerequisites**: none

**Steps**:

- [x] Add `rn/references/pr-feedback-workflow.md` as pure numbered procedure: **Collect** (GitHub review
      threads that are unresolved and whose last comment is the author's, via the API), **Dispatch** (one
      execution subagent per thread, sequential), the subagent's two allowed outcomes
      (address+push+reply-with-commit-link | reply-with-question), the coordinator review-before-next
      gate, the single-pass verification note, and the resolve-by-author rule.
- [x] Keep it rationale-free (proceduralize rule); the intent goes to `rn/docs/design.md` (#5).
- [x] self-check (`checks/9.md`) + QA expert review (subagent) + grep cross-doc consistency. — self-check
      OK; QA round 1 FAIL (pagination / push-fail / no-PR / owner-repo), all fixed (`b62ab33`); QA
      round 2 PASS (validated live against PR #14). Cosmetic `{owner}` nit accepted.

**Completion criteria**:

- An agent runs the loop from the reference alone: it collects exactly the unresolved threads whose last
  comment is the author's, processes them one at a time with a coordinator review between each, and each
  thread ends addressed-and-replied-with-its-commit-link or answered with a question; resolution is left
  to the author; verification is the single coordinator pass (failure modes absent: a thread dispatched
  past the review gate in parallel; a thread changed without a reply; the heavy QA chain present; the
  assistant resolving a thread).

### #10: Wire the gates + escalation to `gm`/`ty`; state the resolve-by-author rule — DONE through QA

**Purpose**: Connect the three scheduled gates (plan/design/evaluation) and the escalation channel to the
`gm`/`ty` verdict vocabulary across `on`/`up`/`task-workflow`, and state the resolve-by-author rule where
review threads are handled. The user approves with `ty` and asks for revision with `gm`; the assistant
infers no verdict.

**Prerequisites**: #7, #8

**Steps**:

- [x] In `rn/skills/on/SKILL.md`, `rn/skills/up/SKILL.md`, `rn/references/task-workflow.md`: state that
      each gate's sign-off is taken via `/rn:ty` (approve) or `/rn:gm` (revise), not an inferred yes/no.
- [x] State the resolve-by-author rule where PR review threads are processed (`pr-feedback-workflow.md`;
      the `push-and-review` rule is in `.claude/rules/`, out of the rn-plugin scope, so left untouched).
- [x] self-check (`checks/10.md`) + QA expert review (subagent) + grep cross-doc consistency (every gate
      references `gm`/`ty`; no confirmation point left with a bespoke verdict). — self-check OK; QA PASS
      (`a99c532`), no defects.

**Completion criteria**:

- Every scheduled gate and confirmation point in `on`/`up`/`task-workflow` resolves through `/rn:ty` or
  `/rn:gm`, the assistant records no verdict the user did not issue, and the resolve-by-author rule is
  stated where threads are handled (failure modes absent: a gate with an inferred or bespoke verdict; a
  thread the docs let the assistant resolve).

### #11: Extract `planning-workflow.md`; `on` becomes a thin orchestrator — DONE through QA

**Purpose**: Per `rn/docs/design.md` root (A), a skill should only orchestrate order — the planning
procedure's own detail (what/why/when) belongs in a dedicated workflow reference, mirroring how task
execution already defers to `task-workflow.md`. Extract `rn/skills/on/SKILL.md` Steps 1–5 (understand
goal, propose location, create `steering.md`, decompose tasks, persist + open the draft PR + take the
plan-gate sign-off) into a new `rn/references/planning-workflow.md`; `on/SKILL.md` keeps only the entry
steps (parse `$ARGUMENTS`, hand off) and Step 6 (begin task #1).

**Prerequisites**: #4 (design-template + doc-division already exist), #12 (planning places the design
sign-off task using the split verify/execute vocabulary)

**Steps**:

- [x] Add `rn/references/planning-workflow.md` containing Steps 1–5 verbatim from `on/SKILL.md` (goal
      understanding, slug + design.md location, `steering.md` creation via `steering-template.md`, task
      decomposition, persist/PR/plan-gate sign-off via `/rn:ty`/`/rn:gm`).
- [x] Rewrite `rn/skills/on/SKILL.md` to: parse the goal/`$ARGUMENTS`, read and run
      `planning-workflow.md`, then begin task #1 per `task-execute-workflow.md` (#12). No planning detail
      stays in `SKILL.md` itself.
- [x] self-check + QA/Design/Craft(writing)/Verification(fact-check) expert review (subagent, all 4 —
      task revises structure) + grep cross-doc consistency (no orphaned reference to the old inline
      steps; `up`'s pointers to `on` still resolve). — self-check OK (`checks/11.md`); round 1: all 4
      axes independently found the same defect (`on/SKILL.md` Step 1 duplicated `planning-workflow.md`'s
      goal-taking clause and inline-summarized its steps, instead of pure delegation) — fixed in
      `81ec8f4`; round 2 re-review: all 4 axes PASS.

**Completion criteria**:

- Running `/rn:on` behaves exactly as before the extraction (same prompts, same plan-gate sign-off via
  `/rn:ty`/`/rn:gm`, same `steering.md` produced) with all planning detail now living in
  `planning-workflow.md` and `on/SKILL.md` reduced to order-only orchestration (failure modes absent: a
  planning step lost in the move; `on/SKILL.md` still carrying step-level rationale or detail).

### #12: Split `task-workflow.md` into `task-execute-workflow.md` + `task-verify-workflow.md` — DONE through QA

**Purpose**: Per root (A), execution and verification are separate work-instructions. Split the current
`task-workflow.md` along its existing Phase boundaries: **Phase: Execute** → `task-execute-workflow.md`;
**Phase: Verify** + **Phase: Complete** (check-off, advance, evaluation-gate trigger) →
`task-verify-workflow.md`. The Roles / Review gates / Process selection sections and the Check file
format are shared context — duplicated into both files' tops (not a third shared file, per the
lean-steering precedent of never inventing accumulation machinery for a two-file split).

**Prerequisites**: #13 (split lands on the new expert axes, not the old language/software-engineering
pair, so the split doesn't happen twice)

**Steps**:

- [x] Add `rn/references/task-execute-workflow.md`: Roles, Review gates, Process selection (shared
      header) + the current Phase: Execute steps verbatim (work-order, starting-commit capture, dispatch).
- [x] Add `rn/references/task-verify-workflow.md`: same shared header + the current Phase: Verify +
      Phase: Complete steps verbatim (dispatch review experts, triage, escalation channel, check-off,
      commit marker, advance/evaluation-gate) + the Check file format.
- [x] Delete `rn/references/task-workflow.md`; update every reference to it (`on/SKILL.md`,
      `up/SKILL.md`, `pr-feedback-workflow.md`, `steering-template.md`) to point to
      `task-execute-workflow.md` then `task-verify-workflow.md` in sequence. (`planning-workflow.md` (#11)
      doesn't exist yet — nothing to update there until #11 lands.)
- [x] self-check + QA/Design/Craft(writing)/Verification(fact-check) expert review (subagent, all 4 —
      task revises structure) + grep cross-doc consistency (no dangling `task-workflow.md` reference
      anywhere in `rn/`). — self-check OK (`checks/12.md`); round 1: QA/Design/Verification PASS, Craft
      found 2 findings (capitalization typo in `steering-template.md:97`; unanchored "Execute element
      5/6" cross-reference in `task-verify-workflow.md`) — fixed in `e710e9f`; round 2 re-review
      (Craft + Verification): both PASS.

**Completion criteria**:

- A coordinator runs one task end-to-end by reading `task-execute-workflow.md` then
  `task-verify-workflow.md` in sequence, with behavior identical to the pre-split `task-workflow.md`
  (same gates, same escalation channel, same check-off marker); no file in `rn/` still points at the
  deleted `task-workflow.md` (failure modes absent: a rule/step dropped at the seam; a dangling
  reference).

### #13: Redefine the expert set — design / craft (per medium) / verification (per medium) + QA — DONE through QA

**Purpose**: Per root (B), replace the fixed code-centric trio (QA / language expert / software-engineering
expert) with function-axis experts — **design**, **craft** (per medium: coding, writing, visual),
**verification** (per medium: test, fact-check, dry-run) — with **QA** cross-cutting every task. Only the
axes a task needs are spawned. Update every place experts are named: `task-workflow.md`'s Roles/Process
selection/Check file format (ahead of #12's split, so the split lands on the new set directly), and the
task-execution work-order/review-prompt elements that name "language expert"/"software-engineering expert".

**Prerequisites**: none (lands before #12 per #12's own prerequisite)

**Steps**:

- [x] In `rn/references/task-workflow.md` Roles: replace "Language expert" / "Software-engineering
      expert" with **Craft expert** (per medium: coding/writing/visual — judges medium-specific best
      practice) and **Verification expert** (per medium: test/fact-check/dry-run — judges whether the
      artifact was actually checked) and add **Design expert** (judges whether the approach/structure
      fits, for tasks that produce or revise structure); QA stays cross-cutting on every task.
- [x] Update Process selection: which axes spawn is a per-task judgment (task states its medium/whether
      it touches structure), not a fixed code-vs-non-code branch — state the rule and give the
      code-task/docs-task examples as instances, not the only two branches.
- [x] Update the Check file format's per-expert tables (replace "Language Expert"/"Software-engineering
      Expert" sections with Craft/Verification/Design, each keyed to its medium).
- [x] Update Execute's work-order element 4 ("Best practices") and Verify's review-prompt elements
      (Role/Criteria/checklists) to name the new axes instead of language/software-engineering.
- [x] self-check + QA/Craft/Verification/Design expert review (subagent, all 4 — task revises
      structure/approach) + grep cross-doc consistency (no surviving "language expert"/
      "software-engineering expert" reference in `rn/`). — self-check OK (`checks/13.md`); round 1: all
      4 axes found real defects (build-time Verification axis code-only; QA/Design wrongly scoped "per
      medium"; stale "non-code vs code" reference in `steering-template.md`; QA/Verification "edge case
      coverage" jurisdiction overlap) — fixed in `5a5aa72`; round 2 re-review: all 4 axes PASS.

**Completion criteria**:

- Every place `rn/` names a review expert uses the design/craft/verification+QA axes, with which axes
  spawn stated as a per-task judgment keyed to what the task produces (not a fixed code/non-code
  branch); no reference to "language expert" or "software-engineering expert" survives, and the same
  axes that build a task also review it (failure modes absent: the old trio surviving anywhere; an axis
  that never fits prose/prompts/slides forced onto a non-code task).

### #14: Reposition design/evaluation gates as sign-off tasks placed by planning

**Purpose**: Per the standing decision in `rn/docs/design.md`, the design and evaluation gates become
**sign-off tasks** that `planning-workflow.md` (#11) places explicitly in the task sequence — not logic
hardcoded into `on`'s Step 5 or `task-verify-workflow.md`'s Phase: Complete. The plan gate stays
planning's own closing hand-off (never a task — a plan can't carry a task that approves itself).

**Prerequisites**: #11 (planning-workflow exists to place the tasks), #12 (verify-workflow's Complete
phase is the file being amended)

**Steps**:

- [ ] In `planning-workflow.md` (#11)'s task-decomposition step: when the session has a `design.md` not
      settled at plan time, place an explicit **"Design sign-off"** task in the sequence (Completion
      criteria: user approves via `/rn:ty`/`/rn:gm`) at the point heavy build would otherwise start on an
      unapproved design; when design is settled at plan time, fold it into the plan-gate hand-off instead
      (no separate task).
- [ ] Always place a final **"Evaluation sign-off"** task (Completion criteria: user approves the
      Acceptance-criteria run via `/rn:ty`/`/rn:gm`) as the session's last task.
- [ ] In `task-verify-workflow.md` (#12)'s Phase: Complete, remove the special-cased "if all tasks are
      done, propose the evaluation gate" branch — Advance just moves to the next task, which is the
      Evaluation sign-off task when planning placed it last; a sign-off task's own Steps carry the
      `ty`/`gm` gate mechanics (per design.md's task-loop: "sign-off task? → user gate").
- [ ] self-check + QA expert review (subagent) + grep cross-doc consistency (every session's task list
      carries an Evaluation sign-off task at its end; no leftover hardcoded gate branch in
      `on`/`task-verify-workflow.md`).

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
- **Notes**: context needed for resume
