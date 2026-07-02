# Task Verify Workflow

The second half of the loop to execute one task: reviews, triages, and checks off the deliverable
produced in `task-execute-workflow.md` (the first half). Read together with it in sequence: `on` and
`up` read both files at task execution, this one second. Run one task at a time.

`{steering_dir}` = the directory holding the active `steering.md` (e.g. `.rn/{yyyymmdd}-{slug}/`). Write check
files under `{steering_dir}/checks/`.

## Roles

- **Coordinator** — the main agent in the conversation. Decomposes the goal, picks which expert each
  piece needs, dispatches, reviews against the committed diff, triages findings, re-instructs, updates
  `steering.md`, talks with the user. Writes directly **only** `steering.md` and `checks/{task-id}.md`;
  never edits the deliverable or its git history.
- **Implementation expert** — subagent. Produces, fixes, and commits/pushes the deliverable (code/docs/
  visual).
- **QA expert** (every task) — subagent. Adversarially verifies the result meets the objective.
- **Design expert** (tasks that produce or revise structure/approach) — subagent. Judges whether the
  approach/structure fits.
- **Craft expert** (per medium: coding / writing / visual) — subagent. Judges medium-specific best
  practice.
- **Verification expert** (per medium: test / fact-check / dry-run) — subagent. Judges whether the
  artifact was actually checked.

All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size.
Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a
compact summary.

## Review gates

The user signs off at exactly **three** scheduled gates, never on any other task:

- **Plan gate** — the draft-PR plan approval in `on` before any task runs.
- **Design gate** — sign-off on the approach / key decisions before they are built on (folds into the
  plan gate when the design is settled at plan time; a separate stop before heavy build otherwise —
  realized as the Design sign-off task below).
- **Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria (realized as the
  Evaluation sign-off task below).

All three gates resolve through the user's verdict commands — `/rn:ty` (approve) or `/rn:gm` (revise);
the assistant never records a verdict the user did not issue.

The per-task boundary is **not** a user gate for ordinary build tasks — the two sign-off tasks (Design
sign-off, Evaluation sign-off) are the exception: their own per-task boundary **is** the design/
evaluation gate itself. Per-task quality on every other task is caught by self-check + QA/expert review +
the coordinator's independent review. Mid-flight, **Escalation** (Verify, Triage) is a separate
always-open channel — not a gate; an escalation message opens with the session-status block per
[`status-display.md`](./status-display.md).

## Process selection

Which axes spawn is a per-task judgment: first, whether the task is a sign-off task or a build task; for
a build task, its medium (coding / writing / visual) and whether it produces or revises structure/
approach. QA always spawns for a task that builds something; a sign-off task spawns none. Craft and
Verification spawn for the task's medium. Design spawns only when the task produces or revises structure/
approach.

- **Code task** (instance): Self-check → QA → Craft (coding) → Verification (test) → coordinator review
  → check-off; add Design when the task also changes structure/approach.
- **Docs task** (instance): Self-check → QA → Craft (writing) → Verification (fact-check) → coordinator
  review → check-off; add Design when the task also changes structure/approach.
- **Visual/diagram task** (instance): Self-check → QA → Craft (visual) → Verification (dry-run) →
  coordinator review → check-off; add Design when the task also changes structure/approach.
- **Sign-off task** (instance): no axes spawn — no implementation expert builds it, no QA/Design/Craft/
  Verification review runs. It skips Phase: Execute and Phase: Verify entirely, going straight from
  picking the task to the gate. Its own Steps (written by planning) are the gate itself — present the
  thing being signed off (`design.md`, or the Acceptance criteria run result) to the user — opening
  the message with the session-status block per [`status-display.md`](./status-display.md) — and take
  the verdict via `/rn:ty` (approve → check off in `steering.md`) or `/rn:gm` (revise → address the
  feedback and re-present the gate; no check-off until later approved).

Self-check is produced in Execute by the implementation expert; QA / Design / Craft / Verification
reviews run in Verify; the coordinator's independent review then clears the task into its check-off. A
sign-off task has no self-check or review round — the gate verdict itself is what clears it.

## Check file format

Write to `{steering_dir}/checks/{task-id}.md`. Column ownership holds across every round, including fix
rounds: the implementation expert writes **only** the Completion Criteria Self-check and Evidence
columns (and the Overall Verdict "Self-check" line) and never the review-verdict sections (QA / Expert
Review / other Overall-Verdict lines and QA columns, which are the coordinator's). The expert does not
commit it. The coordinator fills in the review verdicts it collected and commits the file as part of its
ledger — on the post-Verify steering check-off commit.

```markdown
# {task-id} Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| (text) | OK / NG | (what was confirmed) | OK / NG | (findings) |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Verification approach meaningful to the objective (checks the right thing, not just "passed") | OK / NG | |

## Expert Reviews (axes the task needs)

(Experts assess the aspects below, not each completion criterion — QA is the per-criterion gate. Include
only the sections for the axes this task spawned.)

### Design Expert (tasks that produce or revise structure/approach)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Approach/structure fits | OK / NG | |
| System-wide integrity (interfaces, cross-doc consistency) | OK / NG | |

### Craft Expert (coding / writing / visual — per the task's medium)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Medium-specific best practice | OK / NG | |
| Consistency with existing style | OK / NG | |

### Verification Expert (test / fact-check / dry-run — per the task's medium)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Artifact actually checked (tests run / claims verified / flow traced) | OK / NG | |
| Coverage (edge cases / claims / steps) | OK / NG | |

## Overall Verdict

- Self-check: OK / NG
- QA: OK / NG
- Design expert: OK / NG / N/A
- Craft expert: OK / NG / N/A
- Verification expert: OK / NG / N/A
- Ready to check off: Yes / No (reason)
```

## Phase: Verify

1. **Read the committed diff yourself.**
   - The deliverable is already committed and pushed (`task-execute-workflow.md` Execute element 6); the
     only uncommitted change is the check file the expert wrote (`task-execute-workflow.md` Execute
     element 5). Expect `git status` to show **only** that tracked check file — that is normal, not a
     deliverable change.
   - Inspect the committed deliverable: `git show <sha>` for the returned SHA(s), or `git diff <task's
     starting commit>..HEAD` for the cumulative change.
   - Confirm the change matches the task's scope and Completion criteria before spending review experts.
2. **Dispatch the review experts as independent subagents** — QA always; Craft and Verification for the
   task's medium (coding / writing / visual); Design when the task produces or revises structure/
   approach. Build each review prompt with 6 elements:
   1. **Role** — the expert's domain (QA / Design / Craft / Verification — Craft and Verification scoped
      to the task's medium), told to review **adversarially** from its domain's best practices: assume
      defects exist and try to break the artifact (boundaries, error paths, integration, missed cases).
   2. **Artifact** — the full content or diff under review.
   3. **Criteria** — the expert checklist below.
   4. **Completion criteria** — the task's Completion criteria copied **verbatim** from `steering.md`.
   5. **Output format** — OK/NG per criterion with concrete evidence, plus an overall pass/fail.
   6. **Neutral framing** — pass only goal, artifact, Completion criteria, and the checklist. **Never**
      pass the self-check file (`checks/{task-id}.md`), the implementation expert's summary, or any
      OK/NG verdict; do not defend the choices or hint at the verdict you expect.

   Expert checklists:
   - **QA expert**: the verification approach is meaningful to the actual objective — does it check the
     right thing, not just "it ran"/"it passed"; no rubber-stamped or purpose-mismatched check.
   - **Design expert** (tasks that produce or revise structure/approach): does the approach/structure
     fit; separation of concerns; system-wide integrity (interface contracts, API compatibility,
     cross-doc consistency).
   - **Craft expert** — coding: best practices (naming, error handling, null/thread safety), no
     duplication, consistency with existing codebase style. writing: prose clarity and correctness,
     consistency with the doc's existing voice/terminology. visual: diagram/notation clarity and
     consistency with the doc's existing conventions.
   - **Verification expert** — test: tests are meaningful and in GWT (Given/When/Then) format, and cover
     the change's edge cases (boundary, error, empty, max, type conversion). fact-check: every
     claim/reference verified against its source, no unverified assertion stated as fact, and completeness
     of claim coverage — no material claim left unchecked. dry-run: the diagram/flow traced step by step
     against the described behavior and confirmed to match, covering every step/branch.
3. **Triage every finding.** Each ends in exactly one of:
   - **Valid** → fix it. Dispatch the implementation expert (fresh subagent) — every deliverable-touching
     fix, no matter its size, including minor improvements. Reuse the original work-order (element 5 still
     binds), point it at the current on-disk state to build on (not regenerate), have it commit/push the
     fix as a fresh deliverable commit (element 6, accumulating, never force-pushed). After it returns,
     re-run the same review expert; if the fix could affect a dimension another expert already cleared,
     re-run that expert too. Cap at 3 iterations (one iteration = a single fix plus all its re-reviews);
     valid findings still NG after 3 → record them and escalate to the user with the unresolved items.
   - **Invalid** → reject it, citing evidence. Invalid **only** when it rests on a factual error or falls
     outside a scope boundary written in the Completion criteria — cite the specific fact or criterion.
   - **Escalation** → raise to the user. A normal in-scope finding is **not** escalated — it is decided
     against the bar (Valid/Invalid) above. Escalate **only** when the decision is genuinely the user's:
     it expands scope, changes the agreed direction or a matter of taste, or trades effort against
     benefit only the user can weigh. "It's minor, so I'll just ask" is not a reason.

   Never silently drop, blindly accept, or bounce a finding for lack of a standard. Record the review
   verdicts into the check file.

   **Escalation is an always-open channel, not confined to triage.** This Triage outcome is **one
   place** it fires — during Verify. The same channel is always open: any execution discovery, blocker,
   or decision that would change the **agreed plan or design** is raised to the user **immediately,
   wherever it surfaces** — in Execute, Verify, or anywhere else — never deferred to a gate. It is
   distinct from the three scheduled gates (plan / design / evaluation) and counts as none of them; a
   change to the agreed plan or design cannot ship unseen. Wherever it fires, open the escalation
   message with the session-status block per [`status-display.md`](./status-display.md).

## Phase: Complete

There is no per-task user gate for a normal task: once Verify clears (all expert reviews plus the
coordinator's independent review) — or, for a sign-off task, once the user's gate verdict resolves as
approved — the coordinator checks the task off directly.

1. **Check off steering.** With Verify cleared — or, for a sign-off task, once its gate verdict is
   approved — check off the task in `steering.md` directly.
2. **Commit the check-off with the single completion marker** — message `{type}: complete task #{id} —
   {description}` (`{type}` matches the change: `feat` / `fix` / `docs` / `refactor` / `test` / …), then
   push to the session PR. This is the one completion marker for the task: deliverable commits carry
   plain messages; only this check-off commit carries the `complete task #{id}` substring. Keep that
   exact substring regardless of the prefix.
3. **Advance.** Begin the next unchecked task immediately — a sign-off task goes straight to the gate per
   the Process selection rule above; any other task begins at Phase: Execute
   (`task-execute-workflow.md`). If no unchecked tasks remain and no "Evaluation sign-off" task was ever
   encountered in this session, that is a planning defect (a session must always close via the
   Evaluation sign-off task) — escalate to the user immediately via the same always-open Escalation
   channel described in Triage above; do not close the session silently.
