# Goal

Reshape rn's task-execution model into a **leader / member** split. The leader (the main agent) does
the directing — decomposes tasks, writes work-orders, reviews results against `git diff` and via
adversarial reviewer subagents, re-instructs for fixes, and talks with the user — while the actual
work, and the commit/push, are carried out by **member subagents**. The intent: the leader's context
holds only the diff, the review verdicts, and the conversation with the user, so the member's
trial-and-error never piles up in the leader. Crucially, the leader stays in the loop as a supervisor
rather than fully delegating — that is what keeps the user in the conversation at every task boundary
(full delegation would run start-to-finish with no place for the user to weigh in).

# Acceptance criteria

Goal alignment — the leader / member division (all defined in `task-workflow.md`):

- The Execute phase has the leader write a work-order and dispatch a **member subagent** to do the
  actual work; the leader performs no implementation itself.
- The member does the work plus its own self-check and returns only a **compact summary** to the
  leader; the member's full output and trial-and-error stay inside the subagent, not in the leader's
  context.
- The Verify phase has the leader review each task independently: it inspects `git diff` itself and
  dispatches the adversarial reviewer subagents (QA / language expert / software engineer), then
  triages the findings.
- When fixes are needed, the leader writes improvement instructions and **re-dispatches the member
  subagent**; the leader does not edit the artifact itself. This review → re-instruct loop repeats
  until the bar is cleared.
- User review stays a required gate before any commit: the leader presents the result and waits for
  the user's approval, so the user is present at every task boundary.
- After approval, **commit and push are carried out by a subagent**, not by the leader.

Goal alignment — coherence and scope:

- The leader / member workflow is defined once and authoritatively in `task-workflow.md`; `gm` and
  `hi` keep reaching task execution only through it, with no duplicated or divergent workflow text
  added to the skill files.
- Scope is explicit: this session changes the per-task execution loop in `task-workflow.md`. The
  session-lifecycle commits/pushes in `bb` and `hi` are left unchanged.

Quality:

- The reviewer-subagent safeguards already in `task-workflow.md` (independence, the 6-element
  neutral-framing prompt, withholding the self-check file and any verdict from reviewers) are
  preserved, not weakened.
- `README.md` conveys the leader / member model to a reader in the file's existing scenario /
  plain-language style — no mechanical lists or control-noun labels.
- `CHANGELOG.md` has an `[Unreleased]` entry stating the change as a user-facing benefit, per the
  changelog rules; `version` in `plugin.json` stays `0.2.0` (no release this session).
- `claude plugin validate rn --strict` and `claude plugin validate <marketplace-root> --strict` both
  pass.

# Assumptions

- (fact) The task-execution loop is centralized in `references/task-workflow.md`; `gm` Step 6 and
  `hi` Step 7 both route task execution through it. So changing that one file changes both entry
  points. — verified by reading the files.
- (fact) The Agent tool launches a subagent with no conversation history and returns only its final
  message to the caller, so a member's intermediate work does not enter the leader's context. —
  known harness capability.
- (fact) These are prompt / instruction (non-code) changes, so each task's verify path is
  Self-check → QA review → User review per `task-workflow.md` Process selection. — verified.
- (assumption) `bb` / `hi` session-lifecycle commits and pushes are out of scope for this session;
  only the per-task execution loop changes. — confirmed with the user during planning.
- (assumption) No version bump this session; user-facing changes wait under CHANGELOG `[Unreleased]`,
  and a release is a separate explicit instruction. — per the plugin authoring rules.
- (assumption, unverified) Real leader / member behavior emerges only at runtime; once task #1 lands
  the new workflow, tasks #2+ can serve as live dogfood of it, but reliability of member dispatch for
  file-editing work is not proven up front.

# Rules

- 1 task = 1 commit
- Artifacts in English (per `.claude/rules/language.md`)
- No `version` bump without an explicit release instruction; user-facing changes go under CHANGELOG
  `[Unreleased]` (per `.claude/rules/plugin.md`)
- Keep the workflow authoritative in `task-workflow.md`; do not duplicate the model into `gm` / `hi`
- Preserve the reviewer-subagent independence and neutral-framing safeguards

# Tasks

### #1: Redesign the task-execution loop in task-workflow.md to the leader / member model

**Purpose**: Rewrite `references/task-workflow.md` so the leader dispatches a member subagent for the
actual work, reviews independently, re-instructs the member for fixes, and commits/pushes via a
subagent — keeping the leader's context to diff, review verdicts, and the user conversation.

**Prerequisites**: none

**Steps**:

- [ ] Rewrite the Execute phase: leader writes a work-order; dispatch a member subagent to do the
      work and its own self-check; member returns a compact summary only
- [ ] Rewrite the Verify phase: leader inspects `git diff`, dispatches the adversarial reviewer
      subagents, triages findings; on valid findings the leader writes improvement instructions and
      re-dispatches the member (loop until the bar is cleared)
- [ ] Rewrite the Complete phase: keep the user-review gate; after approval, commit and push are
      performed by a subagent
- [ ] State explicitly which artifacts the leader may write (steering.md / orchestration only) so the
      "leader edits nothing itself" boundary is unambiguous
- [ ] Keep the reviewer-subagent independence and 6-element neutral-framing safeguards intact
- [ ] Keep the check-file format and Process-selection table consistent with the new responsibilities
      (who writes the self-check, who records review verdicts)
- [ ] self-check (OK/NG per completion criterion, record in checks/1.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `task-workflow.md`'s Execute phase delegates the actual work to a member subagent dispatched by the
  leader, and the leader performs no implementation itself
- the member returns only a compact summary; the document instructs that the member's full output and
  trial-and-error do not enter the leader's context
- the Verify phase has the leader inspect `git diff` and dispatch the reviewer subagents, and
  re-instruct the member subagent for fixes (the leader edits no artifact itself)
- the Complete phase keeps the user-review gate before commit, and performs commit and push via a
  subagent
- the reviewer-subagent independence and neutral-framing safeguards are present and unweakened
- `gm` and `hi` still reach task execution solely through `task-workflow.md`, with no workflow text
  duplicated into the skill files

### #2: Reflect the leader / member model in README.md

**Purpose**: Update `README.md` so a reader understands that member subagents do the work while the
leader directs and the user approves at each task boundary, in the file's scenario / plain style.

**Prerequisites**: #1

**Steps**:

- [ ] Add or adjust README content to convey the leader / member model where it helps the reader
      (e.g. the "Why" section or the getting-started flow), in plain scenario language
- [ ] Keep to README's existing style — no mechanical lists or control-noun labels
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `README.md` states that the work is carried out by member subagents while the leader directs and
  the user approves at each task boundary
- the wording follows README's existing scenario / plain-language style, with no mechanical
  enumeration or control-noun labels

### #3: Record the change in CHANGELOG.md

**Purpose**: Add an `[Unreleased]` entry describing the leader / member execution as a user-facing
benefit, without bumping the version.

**Prerequisites**: #1

**Steps**:

- [ ] Add a line under `## [Unreleased]` (in the right Added/Changed group) stating the benefit to
      the user
- [ ] Confirm `version` in `plugin.json` is unchanged
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `CHANGELOG.md` `[Unreleased]` contains a line stating the change in user-facing benefit terms, per
  the changelog rules
- `plugin.json` `version` is unchanged at `0.2.0`

### #4: Pass the validation gates

**Purpose**: Confirm the plugin and the marketplace still validate strictly after the changes.

**Prerequisites**: #1, #2, #3

**Steps**:

- [ ] Run `claude plugin validate rn --strict`
- [ ] Run `claude plugin validate <marketplace-root> --strict`
- [ ] self-check (OK/NG per completion criterion, record in checks/4.md)
- [ ] QA engineer review (subagent)
- [ ] user review

**Completion criteria**:

- `claude plugin validate rn --strict` completes with no errors
- `claude plugin validate <marketplace-root> --strict` completes with no errors

# Decisions

(none yet)

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
