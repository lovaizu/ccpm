# Task Workflow

The loop to execute one task. A **coordinator** delegates to **experts**. `on` and `up` read this file
at task execution. Run one task at a time.

`{steering_dir}` = the directory holding the active `steering.md` (e.g. `.rn/{slug}/`). Write check
files under `{steering_dir}/checks/`.

## Roles

- **Coordinator** — the main agent in the conversation. Decomposes the goal, picks which expert each
  piece needs, dispatches, reviews against the committed diff, triages findings, re-instructs, updates
  `steering.md`, talks with the user. Writes directly **only** `steering.md` and `checks/{task-id}.md`;
  never edits the deliverable or its git history.
- **Implementation expert** — subagent. Produces, fixes, and commits/pushes the deliverable (code/docs).
- **QA expert** — subagent. Adversarially verifies the result.
- **Language expert** (code only) — subagent. Judges language-level craft.
- **Software-engineering expert** (code only) — subagent. Judges design and system integrity.

All deliverable work (produce/fix/commit/push) goes to the implementation expert, every time, any size.
Each review expert runs as an independent subagent (Agent tool, no conversation history) and returns a
compact summary.

## Review gates

The user signs off at exactly **three** scheduled gates, never per task:

- **Plan gate** — the draft-PR plan approval in `on` before any task runs.
- **Design gate** — sign-off on the approach / key decisions before they are built on (folds into the
  plan gate when the design is settled at plan time; a separate stop before heavy build otherwise).
- **Evaluation gate** — the end-of-session run of the `steering.md` Acceptance criteria.

The per-task boundary is **not** a user gate. Per-task quality is caught by self-check + QA/expert
review + the coordinator's independent review. Mid-flight, **Escalation** (Verify, Triage) is a
separate always-open channel — not a gate.

## Process selection

- **Non-code task** (docs, config, design): Self-check → QA → coordinator review → check-off.
- **Code task**: Self-check → QA → Language expert → Software-engineering expert → coordinator review
  → check-off.

Self-check is produced in Execute by the implementation expert; QA / language / software-engineering
reviews run in Verify; the coordinator's independent review then clears the task into its check-off.

## Phase: Execute

1. **Write the work-order.** The expert has no conversation history, so include everything it needs and
   only that, with these 7 elements:
   1. **Task** — Purpose, Steps, Completion criteria copied from `steering.md`.
   2. **Scope** — stay within this task; do not start adjacent tasks; name the files expected in play.
   3. **Method** — (code) write the test first: a failing test capturing the expected behavior, then
      implement until it passes. Not done until its tests pass.
   4. **Best practices** — apply the domain's best practices (code: language/framework conventions,
      error handling, naming, no duplication; docs: the repo's existing style).
   5. **Self-check** — verify each completion criterion (OK/NG with specific evidence); (code) measure
      coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.) and record
      line/branch coverage and uncovered areas. Write results to `{steering_dir}/checks/{task-id}.md`
      using the Check file format below, filling **only** the per-criterion Self-check and Evidence
      columns and the Overall Verdict "Self-check" line. Never write or overwrite the review-verdict
      sections (QA / Expert Review / other Overall-Verdict lines and QA columns) — leave them untouched
      on every round, including fix rounds. **Do not commit the file.**
   6. **Commit & push the deliverable** — stage the deliverable paths explicitly (`git add <path>…`);
      never `git add -A` or `git add .`. Commit with a plain conventional message (`feat:` / `fix:` /
      `docs:` / … matching the change); the message must **not** contain `complete task #`. Push so it
      lands on the session PR. Commits accumulate across rounds; push each as made; **never force-push**.
      - If the expert **cannot push** (sandbox/auth): say so in the return summary, leave the commit in
        place; the coordinator pushes that already-made commit (push only; commit stays the expert's).
      - If the expert **cannot commit at all**: say so, report the change left in the working tree; the
        coordinator commits and pushes it mechanically — staging the deliverable paths explicitly
        (`git add <path>…`; never `-A`/`.`), the plain conventional message, push to the session PR.
        Git mechanics only; content stays the expert's.
   7. **Return** — a compact summary only: what changed (files/functions), the self-check result, the
      commit SHA(s) and that the deliverable was pushed. Do not paste full file contents or
      trial-and-error.
2. **Capture the task's starting commit** — current `HEAD`, just before the expert's first deliverable
   commit. Capture it **once**; do **not** re-capture on fix rounds.
3. **Dispatch the implementation expert** with the work-order and wait for its summary.

## Phase: Verify

1. **Read the committed diff yourself.**
   - The deliverable is already committed and pushed (Execute element 6); the only uncommitted change is
     the check file the expert wrote (Execute element 5). Expect `git status` to show **only** that
     tracked check file — that is normal, not a deliverable change.
   - Inspect the committed deliverable: `git show <sha>` for the returned SHA(s), or `git diff <task's
     starting commit>..HEAD` for the cumulative change.
   - Confirm the change matches the task's scope and Completion criteria before spending review experts.
2. **Dispatch the review experts as independent subagents** — QA always; for code, also language and
   software-engineering. Build each review prompt with 6 elements:
   1. **Role** — the expert's domain (QA / language / software-engineering), told to review
      **adversarially** from its domain's best practices: assume defects exist and try to break the
      artifact (boundaries, error paths, integration, missed cases).
   2. **Artifact** — the full content or diff under review.
   3. **Criteria** — the expert checklist below.
   4. **Completion criteria** — the task's Completion criteria copied **verbatim** from `steering.md`.
   5. **Output format** — OK/NG per criterion with concrete evidence, plus an overall pass/fail.
   6. **Neutral framing** — pass only goal, artifact, Completion criteria, and the checklist. **Never**
      pass the self-check file (`checks/{task-id}.md`), the implementation expert's summary, or any
      OK/NG verdict; do not defend the choices or hint at the verdict you expect.

   Expert checklists:
   - **QA expert**: tests/verifications meaningful to the purpose (not just "passed"); edge cases
     covered (boundary, error, empty, max, type conversion).
   - **Language expert** (code only): best practices (naming, error handling, null/thread safety);
     consistency with existing codebase style; test code in GWT (Given/When/Then) format.
   - **Software-engineering expert** (code only): separation of concerns; system-wide integrity
     (interface contracts, API compatibility); maintainability (no duplication, deep nesting, magic
     numbers).
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
   change to the agreed plan or design cannot ship unseen.

## Phase: Complete

There is no per-task user gate: once Verify clears (all expert reviews plus the coordinator's
independent review), the coordinator checks the task off directly.

1. **Check off steering.** With Verify cleared, check off the task in `steering.md` directly.
2. **Commit the check-off with the single completion marker** — message `{type}: complete task #{id} —
   {description}` (`{type}` matches the change: `feat` / `fix` / `docs` / `refactor` / `test` / …), then
   push to the session PR. This is the one completion marker for the task: deliverable commits carry
   plain messages; only this check-off commit carries the `complete task #{id}` substring. Keep that
   exact substring regardless of the prefix.
3. **Advance.** Begin the next unchecked task immediately at Phase: Execute. If all tasks are done, run
   the **evaluation gate**: propose running the `steering.md` Acceptance criteria and get the user's
   sign-off on the result — do not close the session without it.

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
| Meaningful tests/verification | OK / NG | |
| Edge case coverage | OK / NG | |

## Expert Reviews (code changes only)

(Experts assess the aspects below, not each completion criterion — QA is the per-criterion gate.)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK / NG | |
| Codebase style consistency | OK / NG | |
| GWT test format | OK / NG | |

### Software-engineering Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK / NG | |
| System integrity | OK / NG | |
| Maintainability | OK / NG | |

## Overall Verdict

- Self-check: OK / NG
- QA: OK / NG
- Language expert: OK / NG / N/A
- Software-engineering expert: OK / NG / N/A
- Ready to check off: Yes / No (reason)
```
