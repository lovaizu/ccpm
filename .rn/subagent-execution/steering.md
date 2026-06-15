# Goal

Reshape rn's task-execution model into a **coordinator / experts** division. The coordinator (the
main agent) does the directing — decomposes the goal, decides *which domain's expert* each piece of
work needs, dispatches them, reviews results against `git diff`, re-instructs for fixes, and talks
with the user — while the actual work, the reviews, and the commit/push are carried out by **expert
subagents**, each applying its own domain's best practices. This is a division by domain, not a chain
of command: the coordinator delegates because that expert owns the domain, not by rank. The intent:
the coordinator's context holds only the diff, the verdicts, and the conversation with the user, so
an expert's trial-and-error never piles up in the coordinator. Crucially, the coordinator stays in
the loop as a reviewer rather than fully delegating — that is what keeps the user in the conversation
at every task boundary (full delegation would run start-to-finish with no place for the user to weigh
in).

# Acceptance criteria

Goal alignment — the coordinator / experts division (all defined in `task-workflow.md`):

- The Execute phase has the coordinator write a work-order and dispatch an **implementation expert
  subagent** to do the actual work; the coordinator performs no domain work itself.
- The implementation expert does the work plus its own self-check and returns only a **compact
  summary** to the coordinator; the expert's full output and trial-and-error stay inside the
  subagent, not in the coordinator's context.
- The Verify phase has the coordinator review each task independently: it inspects `git diff` itself
  and dispatches the adversarial review experts (QA / language / software-engineering), then triages
  the findings.
- When fixes are needed, the coordinator writes improvement instructions and **re-dispatches the
  implementation expert**; the coordinator does not edit the artifact itself. This review →
  re-instruct loop repeats until the bar is cleared.
- User review stays a required gate before any commit: the coordinator presents the result and waits
  for the user's approval, so the user is present at every task boundary.
- After approval, **commit and push are carried out by a subagent**, not by the coordinator.
- Each expert is told to apply **its domain's best practices** (the implementation expert in its
  work-order; the review experts in their review prompts).

Goal alignment — coherence and scope:

- The coordinator / experts workflow is defined once and authoritatively in `task-workflow.md`; `gm` and
  `hi` keep reaching task execution only through it, with no duplicated or divergent workflow text
  added to the skill files.
- Scope is explicit: this session changes the per-task execution loop in `task-workflow.md`. The
  session-lifecycle commits/pushes in `bb` and `hi` are left unchanged.

Quality:

- The review-expert safeguards already in `task-workflow.md` (independence, the 6-element
  neutral-framing prompt, withholding the self-check file and any verdict from reviewers) are
  preserved, not weakened.
- `README.md` conveys the coordinator / experts model to a reader in the file's existing scenario /
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
  message to the caller, so an expert's intermediate work does not enter the coordinator's context. —
  known harness capability.
- (fact) These are prompt / instruction (non-code) changes, so each task's verify path is
  Self-check → QA review → User review per `task-workflow.md` Process selection. — verified.
- (assumption) `bb` / `hi` session-lifecycle commits and pushes are out of scope for this session;
  only the per-task execution loop changes. — confirmed with the user during planning.
- (assumption) No version bump this session; user-facing changes wait under CHANGELOG `[Unreleased]`,
  and a release is a separate explicit instruction. — per the plugin authoring rules.
- (assumption, unverified) Real coordinator / experts behavior emerges only at runtime; once task #1
  lands the new workflow, tasks #2+ can serve as live dogfood of it, but reliability of expert
  dispatch for file-editing work is not proven up front.

# Rules

- 1 task = 1 commit
- Artifacts in English (per `.claude/rules/language.md`)
- No `version` bump without an explicit release instruction; user-facing changes go under CHANGELOG
  `[Unreleased]` (per `.claude/rules/plugin.md`)
- Keep the workflow authoritative in `task-workflow.md`; do not duplicate the model into `gm` / `hi`
- Preserve the review-expert independence and neutral-framing safeguards

# Tasks

### #1: Redesign the task-execution loop in task-workflow.md to the coordinator / experts model

**Purpose**: Rewrite `references/task-workflow.md` so the coordinator dispatches an implementation
expert for the actual work, reviews independently, re-instructs the expert for fixes, and
commits/pushes via a subagent — keeping the coordinator's context to diff, verdicts, and the user
conversation, with each expert applying its domain's best practices.

**Prerequisites**: none

**Steps**:

- [x] Rewrite the Execute phase: coordinator writes a work-order; dispatch an implementation expert to
      do the work and its own self-check; expert returns a compact summary only
- [x] Rewrite the Verify phase: coordinator inspects `git diff`, dispatches the adversarial review
      experts, triages findings; on valid findings the coordinator writes improvement instructions and
      re-dispatches the implementation expert (loop until the bar is cleared)
- [x] Rewrite the Complete phase: keep the user-review gate; after approval, commit and push are
      performed by a subagent
- [x] State explicitly which artifacts the coordinator may write (steering.md / check files only) so
      the "coordinator does no domain work itself" boundary is unambiguous
- [x] Have each expert apply its domain's best practices (implementation expert in its work-order;
      review experts in their prompts)
- [x] Unify the cast under "expert" vocabulary (QA expert / language expert / software-engineering
      expert) across the Process-selection table, prompts, checklists, and Check file format
- [x] Keep the review-expert independence and 6-element neutral-framing safeguards intact
- [x] self-check (OK/NG per completion criterion, record in checks/1.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `task-workflow.md`'s Execute phase delegates the actual work to an implementation expert dispatched
  by the coordinator, and the coordinator performs no domain work itself
- the implementation expert returns only a compact summary; the document instructs that the expert's
  full output and trial-and-error do not enter the coordinator's context
- the Verify phase has the coordinator inspect `git diff` and dispatch the review experts, and
  re-instruct the implementation expert for fixes (the coordinator edits no artifact itself)
- the Complete phase keeps the user-review gate before commit, and performs commit and push via a
  subagent
- each expert is instructed to apply its domain's best practices, and the cast reads uniformly as
  experts (QA / language / software-engineering) across table, prompts, checklists, and check format
- the review-expert independence and neutral-framing safeguards are present and unweakened
- `gm` and `hi` still reach task execution solely through `task-workflow.md`, with no workflow text
  duplicated into the skill files

### #2: Reflect the coordinator / experts model in README.md

**Purpose**: Update `README.md` so a reader understands that expert subagents do the work while the
coordinator directs and the user approves at each task boundary, in the file's scenario / plain style.

**Prerequisites**: #1

**Steps**:

- [ ] Add or adjust README content to convey the coordinator / experts model where it helps the reader
      (e.g. the "Why" section or the getting-started flow), in plain scenario language
- [ ] Keep to README's existing style — no mechanical lists or control-noun labels
- [ ] self-check (OK/NG per completion criterion, record in checks/2.md)
- [ ] QA expert review (subagent)
- [ ] user review

**Completion criteria**:

- `README.md` states that the work is carried out by expert subagents while the coordinator directs
  and the user approves at each task boundary
- the wording follows README's existing scenario / plain-language style, with no mechanical
  enumeration or control-noun labels

### #3: Record the change in CHANGELOG.md

**Purpose**: Add an `[Unreleased]` entry describing the coordinator / experts execution as a
user-facing benefit, without bumping the version.

**Prerequisites**: #1

**Steps**:

- [ ] Add a line under `## [Unreleased]` (in the right Added/Changed group) stating the benefit to
      the user
- [ ] Confirm `version` in `plugin.json` is unchanged
- [ ] self-check (OK/NG per completion criterion, record in checks/3.md)
- [ ] QA expert review (subagent)
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
- [ ] QA expert review (subagent)
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
