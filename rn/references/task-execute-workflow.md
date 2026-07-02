# Task Execute Workflow

The first half of the loop to execute one task: produces the deliverable and its self-check. Read
together with `task-verify-workflow.md` (the second half — review, triage, check-off) in sequence:
`on` and `up` read both files at task execution, this one first. Run one task at a time.

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
  thing being signed off (`design.md`, or the Acceptance criteria run result) to the user, opening
  the message with the session-status block per [`status-display.md`](./status-display.md), and take
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

## Phase: Execute

1. **Write the work-order.** The expert has no conversation history, so include everything it needs and
   only that, with these 7 elements:
   1. **Task** — Purpose, Steps, Completion criteria copied from `steering.md`.
   2. **Scope** — stay within this task; do not start adjacent tasks; name the files expected in play.
   3. **Method** — apply the task's Verification method as you build, not only after: coding — write the
      test first, a failing test capturing the expected behavior, then implement until it passes, not
      done until its tests pass; writing — verify each claim/reference against its source as you draft,
      not done until every claim is checked; visual — trace the diagram/flow step by step against the
      described behavior as you build it, not done until it holds end to end.
   4. **Best practices** — apply the axes the task needs: **Craft** (medium-specific best practice —
      coding: language/framework conventions, error handling, naming, no duplication; writing: prose
      clarity, style consistency with the repo's existing voice; visual: diagram clarity, notation
      consistency) and, when the task produces or revises structure/approach, **Design** (does the
      approach/structure fit, system-wide integrity).
   5. **Self-check** — verify each completion criterion (OK/NG with specific evidence), plus confirm the
      Method above was actually applied: coding — measure coverage with a project-appropriate tool
      (Jest, pytest, JaCoCo, gcov, etc.) and record line/branch coverage and uncovered areas; writing —
      confirm every claim was checked against its source and record which; visual — confirm the flow was
      traced end to end and record where. Write results to `{steering_dir}/checks/{task-id}.md`
      using the Check file format above, filling **only** the per-criterion Self-check and Evidence
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

Once the expert returns, continue to `task-verify-workflow.md`.
