# Goal

In rn's task execution, only review work is reliably delegated to experts today; the coordinator (the
main agent in the conversation) ends up doing the generation itself. This redesign removes that
asymmetry: **all hands-on work — generating and fixing the deliverable, and committing/pushing it — is
delegated to the implementation expert by default.** The coordinator confines itself to orchestration
and dialogue: decomposing the goal, dispatching experts, reviewing what comes back, re-instructing,
updating `steering.md`, and getting the user's approval — it never touches the deliverable or the git
history of the deliverable. The one carve-out is the coordinator's **own ledger**: `steering.md`, the
review verdicts it already holds (recorded into the check file), and the commits of those — these carry
no trial-and-error to isolate, so the coordinator does them directly. The split line is "does it carry
exploration/trial-and-error," not "does it write to the repo."

# Acceptance criteria

Goal alignment:

- `task-workflow.md`'s Execute phase has **no "delegate or act directly" decision** for generation; the
  implementation expert is dispatched unconditionally for deliverable work (the "trivial single-step
  edit, coordinator does it" escape hatch is removed from generation).
- The commit and push of the deliverable (code / docs / research) is defined as the implementation
  expert's work — it commits and pushes each change as it makes it, so deliverable commits may
  accumulate across feedback rounds within one task.
- The `complete task #{id}` completion marker that `/rn:hi` matches rides on the coordinator's
  post-approval steering check-off commit (exactly one per task), not on the expert's deliverable commits.
- The document states the coordinator writes directly only `steering.md` and the review verdicts it
  already holds (into the check file), plus the commits of those — and nothing of the deliverable.
- The Verify/triage section routes **every deliverable-touching fix** back to the implementation expert
  (the "no trial-and-error, coordinator fixes it directly" branch is removed for deliverable fixes).
- The intro/framing no longer says delegation is "governed by payoff — not an absolute" for generation;
  the whole document reads consistently under "all hands-on work is delegated."
- The user-review gate remains and is consistent with `push-and-review.md`: the deliverable is pushed
  before user review (review happens on the PR), and the coordinator advances only after approval.

Quality:

- The rewritten `task-workflow.md` has no internal contradiction — intro, Process selection, Execute,
  Verify, Complete, and Check file format all agree on the new division.
- `gm` / `hi` / `bb` SKILL.md and `steering-template.md` contain no statement that contradicts the new
  division (commit ownership, who generates, the `complete task #{id}` match still holds).
- `CHANGELOG.md` has a new line under `## [Unreleased]` stating the change in user terms.
- `plugin.json` `version` is unchanged (no release instruction was given).
- No rn doc nor `.claude/rules/push-and-review.md` states "1 task = 1 commit"; each states "commit and
  push every change; one completion marker per task."
- `claude plugin validate ./rn --strict` and `claude plugin validate . --strict` both pass.
- Wording and style stay consistent with the existing rn docs (English; existing heading structure).

Prompt quality (best-practice pass over all rn docs — added 2026-06-15 after a flat prompt-engineering review):

- `task-workflow.md` reads directive-first: each phase leads with the imperative, rationale is demoted to
  at most one `Why:` per phase, and the deliverable/ledger split, the single-marker rule, and the
  check-file ownership are each stated **once canonically** and referenced thereafter (no full restatement
  3–4×). **Every behavioral invariant is preserved verbatim** — the split line, the neutral-framing
  withhold-list, the 3-iteration counting rule, the `complete task #{id}` substring rule. Goal is
  instruction-following clarity, not a length target.
- `README.md` contains no stale-model statement: the bb sample commit carries a plain/`wip:` message
  (never `complete task #{id}`), and no line says the assistant makes changes "without involving an
  expert" (the unconditional-delegation model holds).
- `bb` SKILL.md states explicitly that a suspend-time commit must **not** contain `complete task #{id}`
  (so `/rn:hi` reconciliation cannot be tripped by a half-done task), and references `steering-template.md`
  for the `State`/`paused` semantics instead of re-explaining them.
- `gm` SKILL.md does not re-teach what `steering-template.md` / `task-workflow.md` already own (Acceptance
  criteria axes, task fields, the goal-restatement rule appear once and hand off to the reference).
- `plugin.json` `description` reflects the current model (it mentions executing each task via a
  coordinator that delegates hands-on work to domain experts and reviews it before approval).

Out of scope:

- Version bump, tag, or GitHub Release (not until an explicit release instruction).
- Changing the review side (QA / language / software-engineering experts) — it is already delegated and
  works; this session only changes the generation side.
- Adding any new skill or command.

# Assumptions

- Fact: `task-workflow.md` Execute currently has a delegate/act-directly decision that lets the
  coordinator generate directly (verified: lines 54-61).
- Fact: review is already always delegated to subagents in Verify (verified: lines 96-118).
- Fact: the deliverable commit currently happens in Complete, done by the coordinator (verified: lines
  178-186).
- Fact: `/rn:hi` matches a task to a commit by the `complete task #{id}` substring (verified: hi Step 4).
- Fact: `push-and-review.md` requires "push on every change" and "review happens on the PR."
- Fact (verified 2026-06-15 by empirical probe): a subagent dispatched via the Agent tool **can** run
  `git commit` and `git push` — commit succeeded, `git push` returned exit 0 with no sandbox/permission
  denial. The "expert commits/pushes" model is therefore viable in this environment. The remaining
  fallback need is only for an environment that lacks the capability, not this one.

# Rules

- Commit and push every change as it is made; the expert's deliverable commits accumulate freely on the
  branch. One task = one completion marker (a single `complete task #N`), not one git commit.
- Artifacts are written in English (`.claude/rules/language.md`)
- Commit and push on every change; review happens on the PR (`.claude/rules/push-and-review.md`)

# Tasks

### #1: Rewrite task-workflow.md to delegate all hands-on work to the implementation expert

**Purpose**: Remove the coordinator's discretion to generate/fix the deliverable directly, and make all
deliverable work — including its commit/push — the implementation expert's, leaving the coordinator with
orchestration plus its own ledger.

**Prerequisites**: none

**Steps**:

- [x] Rewrite the intro/framing (lines 5-37, including the `1 task = 1 commit` line) so delegating all hands-on work is the rule — drop "governed by payoff — not an absolute" and the "coordinator does trivial edits" carve-out for generation; keep the carve-out only for the coordinator's own ledger
- [x] Rewrite the Execute phase so the implementation expert is dispatched unconditionally for deliverable work, and its work-order ends with committing + pushing the deliverable (plain `feat:`/`fix:` message; commits may accumulate across feedback rounds)
- [x] Update "What the coordinator may write directly" to: `steering.md`, the review verdicts it already holds (into the check file), and the commits of those — nothing of the deliverable
- [x] Rewrite the Verify/triage section so every deliverable-touching fix is re-dispatched to the implementation expert (remove the coordinator-direct-fix branch for deliverables)
- [x] Update the Complete phase, the Process selection note, and the Check file format to the new ownership and `push-and-review.md`: the deliverable is pushed before user review, and the `complete task #{id}` marker lands on the coordinator's post-approval steering check-off commit
- [x] Tighten the document for instruction-following (best-practice pass): lead each phase with the imperative; demote rationale to ≤1 `Why:` per phase; state the deliverable/ledger split, the single-marker rule, and the check-file ownership **once canonically** and reference them thereafter (no 3–4× full restatement). Preserve every behavioral invariant **verbatim** — the split line, the neutral-framing withhold-list, the 3-iteration counting rule, the `complete task #{id}` substring rule. Not a length target; clarity is the goal
- [x] self-check (OK/NG per completion criterion, record in checks/1.md)
- [x] QA expert review (subagent)
- [x] user review (approved on PR #10)

**Completion criteria**:

- The Execute phase contains no delegate-or-act-directly decision for generation; deliverable work is
  always dispatched to the implementation expert.
- The document assigns the deliverable's commit + push to the implementation expert (each change pushed
  as made), and places the single `complete task #{id}` marker on the coordinator's post-approval
  steering check-off commit.
- The document limits the coordinator's direct writes to `steering.md` and the review verdicts (into the
  check file) plus their commits, and says so explicitly.
- The Verify/triage section sends every deliverable-touching fix to the implementation expert, with no
  coordinator-direct-fix path for deliverables.
- The intro, Process selection, Execute, Verify, Complete, and Check file format sections are mutually
  consistent under the new division, and the user-review gate matches `push-and-review.md`.
- The document is directive-first: the split / single-marker / check-file-ownership are each stated once
  canonically and referenced thereafter, rationale is ≤1 `Why:` per phase, and every behavioral invariant
  above is preserved verbatim.

### #2: Reconcile the rest of rn with the new model and run a best-practice pass

**Purpose**: Ensure every other rn doc and the project rules agree with the new division, fix the
stale-model contradictions the flat review found (including `README.md`, missed by the original plan),
harden the one implicit cross-file invariant, trim the cross-file/duplicated prose, and record the
change for users.

**Prerequisites**: #1

**Steps**:

- [x] Scan `gm` / `hi` / `bb` SKILL.md, `README.md`, and `steering-template.md` for statements that contradict the new division (commit ownership, who generates, the `complete task #{id}` match) and fix any
- [x] Fix `README.md`: the bb sample commit must carry a plain/`wip:` message (not `complete task #{id}`); remove the "the assistant just makes it itself, without involving an expert" line (stale delegate-or-do-it-yourself model)
- [x] Reword "1 task = 1 commit" in `steering-template.md` (`Rules` placeholder) and `.claude/rules/push-and-review.md` to "commit and push every change; one completion marker per task" (keeping push-and-review's primary "commit/push every change" intent)
- [x] Harden `bb` SKILL.md: state explicitly that a suspend-time commit must not contain `complete task #{id}`; replace the State/`paused` re-explanation with a reference to `steering-template.md`
- [x] Best-practice trim (no behavioral change): in `gm` SKILL.md remove re-teaching that `steering-template.md` / `task-workflow.md` already own (criteria axes, task fields, goal-restatement) and hand off; dedup the two overlapping `steering-template.md` requirement rows
- [x] Update `plugin.json` `description` to reflect the current model (executing each task via a coordinator that delegates hands-on work to domain experts and reviews it before approval); keep `version` `0.3.0`
- [x] Add a user-facing line under `## [Unreleased]` in `CHANGELOG.md` (scoped to the new delta: the deliverable is now authored/committed by the implementation expert; one completion marker per task)
- [x] Run `claude plugin validate ./rn --strict` and `claude plugin validate . --strict`
- [x] self-check (OK/NG per completion criterion, record in checks/2.md)
- [x] QA expert review (subagent)
- [x] user review (approved on PR #10)

**Completion criteria**:

- `gm` / `hi` / `bb` SKILL.md, `README.md`, and `steering-template.md` contain no statement that
  contradicts the new division (including the README bb-commit example and the "without involving an
  expert" line).
- Neither `steering-template.md` nor `.claude/rules/push-and-review.md` states "1 task = 1 commit"; each
  states "commit and push every change; one completion marker per task."
- `bb` SKILL.md explicitly forbids `complete task #{id}` in a suspend-time commit and references
  `steering-template.md` for the `State`/`paused` semantics.
- `gm` SKILL.md does not re-teach content owned by `steering-template.md` / `task-workflow.md`; no
  behavioral directive is lost in the trim.
- `plugin.json` `description` reflects the coordinator/experts execution model; `version` is `0.3.0`.
- `CHANGELOG.md` has a new line under `## [Unreleased]` describing the change in user terms.
- `claude plugin validate ./rn --strict` and `claude plugin validate . --strict` both report success.

### #3: Fix four task-workflow.md defects surfaced by an end-to-end simulation

**Purpose**: An end-to-end simulation of the rewritten `task-workflow.md` (run after #1/#2 were approved)
surfaced one internal contradiction and three gaps the flat acceptance pass missed. Fix all four in
`task-workflow.md` without altering any behavioral invariant, so the document is self-consistent and
robust to the failure modes the simulation exposed.

**Prerequisites**: #1

**Steps**:

- [x] **Fix 1 (internal contradiction)**: the Verify "Read the committed diff" step claims the working
  tree is clean / `git status` shows nothing. False — the expert wrote `checks/{task-id}.md` and did not
  commit it (Execute element 5), and that file is tracked, so `git status` shows it. Correct the wording:
  the *deliverable* is committed (no uncommitted deliverable change), the only uncommitted thing in the
  tree is the check-file ledger; inspect the committed change via `git show <sha>` / range diff
- [x] **Fix 2 (missing fallback branch)**: Execute element 6's fallback covers "expert cannot push" but
  not "expert cannot commit". Add the commit-unavailable case, symmetric to the push-only fallback: the
  expert reports it produced the change but its environment blocks `git commit`; the coordinator then runs
  the commit mechanically over the expert's already-written change (git mechanics only — the content stays
  the expert's, the coordinator never authors/edits the deliverable). Note commit/push capability is
  verified available via the Agent tool, so this is a last-resort path for capability-less environments
- [x] **Fix 3 (selective-staging fragility)**: Execute element 6 says "stage the deliverable change only
  (not the check file)" but a habitual `git add -A` / `git add .` would sweep the coordinator's check-file
  ledger into a plain deliverable commit. Add an explicit guard: stage the deliverable paths explicitly;
  never `git add -A` / `git add .`, so the check file is never committed by the expert
- [x] **Fix 4 (uncaptured starting commit)**: Verify offers `git diff <task's starting commit>..HEAD` for
  the cumulative change, but nothing tells the coordinator to record that starting commit. Add a one-line
  instruction in Execute (before dispatch) to capture the task's starting commit (HEAD before the first
  deliverable commit) so the range diff is computable across feedback rounds
- [x] self-check (OK/NG per completion criterion, record in checks/3.md)
- [x] QA expert review (subagent)
- [x] user review (approved on PR #10)

**Completion criteria**:

- The Verify step no longer claims the working tree is clean / `git status` shows nothing; it correctly
  states the deliverable is committed and only the check-file ledger is uncommitted, and directs the
  coordinator to inspect the committed change.
- Execute element 6 has a "cannot commit" fallback symmetric to the "cannot push" one, preserving "the
  coordinator never authors/edits the deliverable" (git mechanics only).
- Execute element 6 explicitly forbids `git add -A` / `git add .` and requires staging the deliverable
  paths explicitly, so the check file is never swept into a deliverable commit.
- Execute instructs the coordinator to capture the task's starting commit before dispatch, making the
  Verify range diff computable.
- **No behavioral invariant is altered**: the deliverable/ledger split, one-marker-per-task, the
  `complete task #{id}` substring rule, the neutral-framing withhold-list, and the 3-iteration counting
  rule all stand verbatim. Each fix is additive/corrective wording, not a model change.
- `claude plugin validate ./rn --strict` and `claude plugin validate . --strict` both report success.

### #4: Fix three more task-workflow.md defects surfaced by a second end-to-end simulation

**Purpose**: A second end-to-end simulation (run after #3's fixes, by the coordinator plus an
independent QA subagent) surfaced three more defects — all in the multi-round fix loop and the fallback
paths, the same class #3 targeted but in corners the first simulation never reached. Close them so the
document is robust across feedback rounds and last-resort paths, without altering any behavioral
invariant.

**Prerequisites**: #1, #3

**Steps**:

- [ ] **Fix A (check-file ledger overwritten on fix rounds)**: on a Verify fix round the implementation
  expert is re-dispatched with the original work-order, whose Execute element 5 tells it to write
  `checks/{task-id}.md` — overwriting the QA verdicts the coordinator already recorded there (Verify
  step), while Fix 1's "only the check file is dirty = normal" reasoning hides the corruption. Make the
  ownership unambiguous across rounds: the implementation expert only ever writes the **self-check
  columns** and never the review-verdict sections, and/or the re-dispatch narrows element 5 — so the
  coordinator's recorded verdicts are never clobbered and the check file stays the coordinator's ledger
- [ ] **Fix B (cannot-commit fallback: missing staging guard + missing push)**: Execute element 6's
  "expert cannot commit" fallback tells the coordinator to commit mechanically but neither re-asserts
  the explicit-path staging guard (so a habitual `git add -A` could sweep the check file into the
  deliverable commit — the very failure Fix 3 closes for the expert) nor ends by pushing. Add the
  staging guard to the fallback (stage deliverable paths explicitly; never `git add -A` / `git add .`)
  and have it end by pushing, symmetric to the "cannot push" branch
- [ ] **Fix C (starting-commit re-capture ambiguity)**: "reuse the original work-order … dispatch the
  implementation expert" in the Triage Valid branch can be read as re-entering the Execute dispatch step
  and re-capturing the starting commit, collapsing the range diff. Add a one-line note that on fix
  rounds the starting commit is **not** re-captured — it stays anchored at the task's original starting
  commit
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA expert review (subagent)
- [x] user review (approved on PR #10)

**Completion criteria**:

- On a Verify fix round, no instruction causes the implementation expert to overwrite the coordinator's
  recorded review verdicts in `checks/{task-id}.md`; the check file stays the coordinator's ledger
  across all rounds, with element 5 / the re-dispatch wording making the column ownership unambiguous.
- Execute element 6's "cannot commit" fallback re-asserts explicit-path staging (never `git add -A` /
  `git add .`) and ends by pushing, symmetric to the "cannot push" fallback.
- The document states the starting commit is captured once before the first deliverable commit and is
  not re-captured on fix rounds.
- **No behavioral invariant is altered**: the deliverable/ledger split, one-marker-per-task, the
  `complete task #{id}` substring rule, the neutral-framing withhold-list, and the 3-iteration counting
  rule all stand verbatim. Each fix is additive/corrective wording, not a model change.
- `claude plugin validate ./rn --strict` and `claude plugin validate . --strict` both report success.

# Decisions

## D-1: Deliverable commits accumulate; the completion marker rides on the steering check-off commit
- **Issue**: Once committing/pushing the deliverable is the expert's work, the push lands inside the
  expert's dispatch — and `push-and-review.md` wants every change pushed as it is made (reviewed on the
  PR). The coordinator's review then drives fixes, so a task spans several commits. How do "1 task = 1
  commit" and "where does `/rn:hi` read completion" resolve?
- **Conclusion**: Let the expert's deliverable commits **accumulate freely** on the branch (initial
  creation + each feedback round), pushed as made — no force-push. Drop the literal "1 task = 1 commit"
  in favour of "one task = one **completion marker**." The single `complete task #{id}` marker is placed
  on the coordinator's **post-approval steering check-off commit**, so exactly one marker exists per task
  and `/rn:hi` reconciliation still works.
- **Rationale**: On a dev branch, accumulating commits is normal and makes the work's progression
  visible — the user's stated preference; it also fits `push-and-review.md`'s primary rule (commit and
  push as soon as a change is made) better than a single end-of-task commit. Forcing one commit per task
  would need amend + force-push, which hides that progression for no benefit. Anchoring the marker to the
  check-off commit (made only after user approval) gives one unambiguous "task done" signal.
- **Evidence**: `push-and-review.md` — "Commit and push as soon as a change is made"; "the gate still
  stands — it just moves to the PR." `/rn:hi` matches a task by the `complete task #{id}` substring.
- **Sources**: `.claude/rules/push-and-review.md`; `rn/skills/hi/SKILL.md` Step 4.

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
