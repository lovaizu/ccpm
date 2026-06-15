# Goal

Reshape rn's task-execution model into a **coordinator / experts** division whose real purpose is to
**keep the coordinator's context light, keep quality high, and keep the user present at every task
boundary**. The coordinator (the main agent) directs — decomposes the goal, decides *which domain's
expert* each piece of work needs, dispatches them, reviews results against `git diff`, re-instructs
for fixes, and talks with the user. Domain work — the writing, the reviews — is carried out by
**expert subagents**, each applying its own domain's best practices.

Delegation is a **means, not the end.** The coordinator delegates **when delegation pays off — when a
piece of work carries real trial-and-error or exploration that should stay out of the coordinator's
context** (typically code, research, or any work expected to need several attempts). The point is
that an expert's dead-ends never pile up in the coordinator; its context holds only the diff, the
verdicts, and the conversation with the user. For trivial, single-step work (e.g. a one-line doc
edit) and pure session bookkeeping (commit/push, `steering.md`, check files) — where there is no
trial-and-error to isolate — the coordinator acts directly; delegating there would add ceremony
without serving the purpose.

This is a division by domain, not a chain of command: the coordinator delegates because that expert
owns the domain, not by rank. And crucially the coordinator stays in the loop as a reviewer rather
than fully delegating — that is what keeps the user in the conversation at every task boundary (full
delegation would run start-to-finish with no place for the user to weigh in).

# Acceptance criteria

Goal alignment — the coordinator / experts division (all defined in `task-workflow.md`):

- The purpose leads and is explicit: the model exists to keep the coordinator's context to the diff,
  the verdicts, and the user conversation — an expert's trial-and-error must not pile up in the
  coordinator — with quality and the user-in-loop preserved alongside it.
- Delegation is a means governed by **payoff, not an absolute**: the Execute phase has the coordinator
  write a work-order and dispatch an **implementation expert** for work that carries real
  trial-and-error or exploration (e.g. code, substantial writing); it may do trivial single-step edits
  and pure bookkeeping directly. The bar is whether trial-and-error is isolated from the coordinator's
  context, not whether the coordinator ever touches an artifact.
- When an implementation expert is dispatched, it does the work plus its own self-check and returns
  only a **compact summary**; the expert's full output and trial-and-error stay inside the subagent,
  not in the coordinator's context.
- The Verify phase has the coordinator review each task independently: it inspects `git diff` itself
  and dispatches the adversarial review experts (QA / language / software-engineering), then triages
  the findings.
- When fixes are needed on delegated work, the coordinator writes improvement instructions and
  **re-dispatches the implementation expert** rather than silently taking over its domain work. This
  review → re-instruct loop repeats until the bar is cleared.
- User review stays a required gate before any commit: the coordinator presents the result and waits
  for the user's approval, so the user is present at every task boundary.
- Commit/push and `steering.md` / check files are session bookkeeping the coordinator does directly
  (no trial-and-error to isolate); delegating them would add ceremony without serving the purpose.
- Each expert is told to apply **its domain's best practices** (the implementation expert in its
  work-order; the review experts in their review prompts).

Goal alignment — coherence and scope:

- The coordinator / experts workflow is defined once and authoritatively in `task-workflow.md`; `gm` and
  `hi` keep reaching task execution only through it, with no duplicated or divergent workflow text
  added to the skill files.
- Scope is explicit: this session changes the per-task execution loop in `task-workflow.md`, plus a
  small `gm` follow-up that makes the session PR body a single link to `steering.md` (no duplicated
  plan). The session-lifecycle commits/pushes in `bb` and `hi` are left unchanged.

Quality:

- The review-expert safeguards already in `task-workflow.md` (independence, the 6-element
  neutral-framing prompt, withholding the self-check file and any verdict from reviewers) are
  preserved, not weakened.
- `README.md` conveys the corrected model — experts carry out the work that warrants it while the
  coordinator directs (handling trivial and bookkeeping steps itself) and the user approves at each
  task boundary — in the file's existing scenario / plain-language style, with no mechanical lists or
  control-noun labels.
- `CHANGELOG.md` has a single `[Unreleased]` entry stating the change as a user-facing benefit (the
  corrected delegate-by-payoff model, not the superseded absolute), per the changelog rules; `version`
  in `plugin.json` stays `0.2.0` (no release this session).
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

- [x] Add or adjust README content to convey the coordinator / experts model where it helps the reader
      (e.g. the "Why" section or the getting-started flow), in plain scenario language
- [x] Keep to README's existing style — no mechanical lists or control-noun labels
- [x] self-check (OK/NG per completion criterion, record in checks/2.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `README.md` states that the work is carried out by expert subagents while the coordinator directs
  and the user approves at each task boundary
- the wording follows README's existing scenario / plain-language style, with no mechanical
  enumeration or control-noun labels

### #3: Correct task-workflow.md from "coordinator does no domain work" to "delegate by payoff"

**Purpose**: Revise `references/task-workflow.md` so delegation is governed by payoff — the coordinator
dispatches an implementation expert for work that carries real trial-and-error / exploration, and
handles trivial single-step edits and pure bookkeeping (incl. commit/push) directly — aligning the
document with the corrected Goal (light context is the end; "no domain work" was an over-strict means).
Per D-2.

**Prerequisites**: #1

**Steps**:

- [x] Reframe the intro to lead with the purpose (light context / quality / user-in-loop) and state
      that delegation is a means governed by payoff, not an absolute
- [x] Execute phase: delegate the implementation expert for work carrying real trial-and-error; permit
      the coordinator to do trivial single-step edits directly, with the trigger stated
- [x] Complete phase: make commit/push coordinator bookkeeping (remove the mandatory commit subagent),
      keeping the user-review gate and the `complete task #{id}` message convention
- [x] Keep "what the coordinator may write directly" consistent with the corrected means
      (steering / check files, trivial edits, bookkeeping commits)
- [x] Preserve the review-expert independence and 6-element neutral-framing safeguards
- [x] self-check (OK/NG per completion criterion, record in checks/3.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `task-workflow.md` leads with the purpose and frames delegation as payoff-governed, not "the
  coordinator performs no domain work itself"
- the Execute phase delegates work carrying real trial-and-error and permits coordinator-direct trivial
  edits, with the trigger stated
- the Complete phase performs commit/push as coordinator bookkeeping (no mandatory subagent) and keeps
  the user-review gate and the `complete task #{id}` message convention
- the review-expert independence and neutral-framing safeguards are present and unweakened
- `gm` and `hi` still reach task execution solely through `task-workflow.md`

### #4: Align README.md with the corrected model

**Purpose**: Adjust `README.md` so it does not overstate that the assistant "never does the work
itself"; convey that experts carry out the work that warrants it while the coordinator directs
(handling trivial and bookkeeping steps) and the user approves at each task boundary — in README's
scenario style.

**Prerequisites**: #3

**Steps**:

- [x] Adjust the README wording so the delegate-by-payoff model reads accurately (no absolute "doesn't
      do the work itself"), keeping the user-approval-at-each-boundary point
- [x] Keep README's existing scenario / plain-language style — no mechanical lists or control-noun labels
- [x] self-check (OK/NG per completion criterion, record in checks/4.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `README.md` conveys that experts carry out the work that warrants it while the coordinator directs and
  the user approves at each task boundary, without claiming the coordinator never does any work itself
- the wording follows README's existing scenario / plain-language style

### #5: Update CHANGELOG.md to the corrected user benefit

**Purpose**: Replace the superseded `[Unreleased]` lines with an entry stating the corrected model's
benefit (a lighter conversation because real iteration stays out of sight, you still approve at every
task boundary, and routine fixes are decided against a quality bar), without bumping the version.

**Prerequisites**: #3

**Steps**:

- [x] Rewrite the `[Unreleased]` `Changed` entry to state the corrected delegate-by-payoff benefit in
      user-facing terms (a single coherent entry, not v1 + correction)
- [x] Confirm `version` in `plugin.json` is unchanged at `0.2.0`
- [x] self-check (OK/NG per completion criterion, record in checks/5.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `CHANGELOG.md` `[Unreleased]` states the corrected model's change in user-facing benefit terms, per
  the changelog rules
- `plugin.json` `version` is unchanged at `0.2.0`

### #6: Pass the validation gates

**Purpose**: Confirm the plugin and the marketplace still validate strictly after the changes.

**Prerequisites**: #1, #2, #3, #4, #5

**Steps**:

- [x] Run `claude plugin validate rn --strict`
- [x] Run `claude plugin validate <marketplace-root> --strict`
- [x] self-check (OK/NG per completion criterion, record in checks/6.md)
- [x] QA expert review (subagent)
- [x] user review

**Completion criteria**:

- `claude plugin validate rn --strict` completes with no errors
- `claude plugin validate <marketplace-root> --strict` completes with no errors

# Decisions

## D-1: Give the coordinator an explicit quality bar so it stops bouncing decidable calls to the user
- **Issue**: The triage step let the coordinator send minor-but-valid quality findings to the user for
  a decision, instead of deciding them itself.
- **Conclusion**: The coordinator holds an explicit bar — the artifact's *proper form* (correct,
  clear, consistent with the codebase's standards, in service of the goal). Valid improvements
  (including minor ones) are applied by re-dispatching the implementation expert without asking;
  escalate to the user *only* for decisions genuinely theirs (scope expansion, agreed direction or
  taste, an effort-vs-benefit tradeoff only they can weigh) or valid findings unresolved after the
  3-iteration cap.
- **Rationale**: Without a standard, every do/don't leaks to the user as a question. A clear bar lets
  the coordinator judge, reserving the user's involvement for real ownership calls; the end-of-task
  user-review gate stays as the final safeguard, so coordinator autonomy mid-verify does not remove
  the user from the loop.
- **Evidence**: This session, a minor pronoun-ambiguity finding on the README was reflexively bounced
  to the user as an "A: keep / B: polish" choice; the user pointed out this happened for lack of a
  judgment criterion ("あるべき姿にして欲しい、だと判断できない？").
- **Sources**: conversation 2026-06-15; `rn/references/task-workflow.md` → "Step — Triage and
  re-instruct".

## D-2: "Coordinator does no domain work" was an over-strict means; the goal is light context, so delegate by payoff
- **Issue**: The Goal and Acceptance criteria encoded "the coordinator performs no domain work itself"
  as if it were the objective. Dogfooding #1–#3 exposed the cost: a one-line CHANGELOG edit was
  dispatched to an implementation expert, and commit/push to a separate subagent — dispatch ceremony
  heavier than the task, serving no purpose because such trivial work has no trial-and-error to isolate.
- **Conclusion**: The objective is to keep the coordinator's context light (the expert's trial-and-error
  stays in the subagent), with quality and the user-in-loop preserved. "No domain work" is demoted to a
  means and corrected: delegate when the work carries real trial-and-error / exploration to isolate
  (code, research, multi-attempt work); the coordinator acts directly on trivial single-step edits and
  pure bookkeeping (commit/push, `steering.md`, check files).
- **Rationale**: A trivial edit has nothing to isolate, so doing it directly costs the coordinator no
  context — while delegating it adds a full agent briefing and dispatch. Tying delegation to payoff
  serves the goal that the absolute rule was mistakenly standing in for.
- **Evidence**: This session the user challenged the framing — "実作業をしない、が目的？本当？" — and the
  Goal's own *狙い* names light context and the user-in-loop, with "no domain work" only the mechanism.
- **Sources**: conversation 2026-06-15; this `steering.md` Goal; `rn/references/task-workflow.md`.

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)
