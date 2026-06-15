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
- Assumption (unverified): a subagent dispatched via the Agent tool can run `git commit` / `git push`.
  If it cannot, the "expert commits/pushes" model needs an alternative; this only manifests when rn is
  *used*, not when these docs are edited, so it does not block this session.

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

- [ ] Rewrite the intro/framing (lines 5-37, including the `1 task = 1 commit` line) so delegating all hands-on work is the rule — drop "governed by payoff — not an absolute" and the "coordinator does trivial edits" carve-out for generation; keep the carve-out only for the coordinator's own ledger
- [ ] Rewrite the Execute phase so the implementation expert is dispatched unconditionally for deliverable work, and its work-order ends with committing + pushing the deliverable (plain `feat:`/`fix:` message; commits may accumulate across feedback rounds)
- [ ] Update "What the coordinator may write directly" to: `steering.md`, the review verdicts it already holds (into the check file), and the commits of those — nothing of the deliverable
- [ ] Rewrite the Verify/triage section so every deliverable-touching fix is re-dispatched to the implementation expert (remove the coordinator-direct-fix branch for deliverables)
- [ ] Update the Complete phase, the Process selection note, and the Check file format to the new ownership and `push-and-review.md`: the deliverable is pushed before user review, and the `complete task #{id}` marker lands on the coordinator's post-approval steering check-off commit
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA expert review (subagent)
- [ ] user review

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

### #2: Reconcile the skills, template, changelog, and project rules with the new model

**Purpose**: Ensure the rest of the rn docs and the project rules do not contradict the new division,
and record the change for users.

**Prerequisites**: #1

**Steps**:

- [ ] Scan `gm` / `hi` / `bb` SKILL.md and `steering-template.md` for statements that contradict the new division (commit ownership, who generates, the `complete task #{id}` match) and fix any
- [ ] Reword "1 task = 1 commit" in `steering-template.md` and `.claude/rules/push-and-review.md` to "commit and push every change; one completion marker per task" (keeping push-and-review's primary "commit/push every change" intent)
- [ ] Add a user-facing line under `## [Unreleased]` in `CHANGELOG.md`
- [ ] Confirm `plugin.json` `version` stays `0.3.0`
- [ ] Run `claude plugin validate ./rn --strict` and `claude plugin validate . --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- `gm` / `hi` / `bb` SKILL.md and `steering-template.md` contain no statement that contradicts the new
  division.
- Neither `steering-template.md` nor `.claude/rules/push-and-review.md` states "1 task = 1 commit"; each
  states "commit and push every change; one completion marker per task."
- `CHANGELOG.md` has a new line under `## [Unreleased]` describing the change in user terms.
- `plugin.json` `version` is `0.3.0`.
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
- **Date**: 2026-06-15
- **Last completed**: none
- **Next**: #1 Rewrite task-workflow.md to delegate all hands-on work to the implementation expert
- **Notes**: session just started
