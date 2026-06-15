# Task Workflow

The shared execution loop for a single task, run by a **coordinator** who delegates to **experts**.
`gm` and `hi` read this file when they reach task execution. Run one task at a time.
**1 task = 1 commit.**

- **Coordinator** — the main agent (the one in the conversation). Decomposes the goal, decides *which
  domain's expert* each piece of work needs, dispatches them, reviews what comes back against
  `git diff`, triages findings, and talks with the user. The coordinator **does no domain work
  itself** — it routes work to the expert who owns that domain.
- **Experts** — subagents (Agent tool, no conversation history), each specialized in one domain and
  each applying **its domain's best practices**. The coordinator dispatches the right one for the job
  and gets back a **compact summary**. The experts in this loop:
  - **Implementation expert** — produces the task's deliverable (code/docs).
  - **QA expert** — adversarially verifies the result.
  - **Language expert** (code only) — judges language-level craft.
  - **Software-engineering expert** (code only) — judges design and system integrity.

This is a division by domain, not a chain of command: the coordinator delegates *because that expert
owns the domain*, not by rank. Two things fall out of it. The expert's trial-and-error stays inside
the subagent, so the coordinator's context holds only the diff, the verdicts, and the conversation.
And because the coordinator stays on to review rather than fully delegating, the user keeps a place to
weigh in at every task boundary (full delegation would run start-to-finish with nowhere to step in).

What the coordinator may write directly: `steering.md` and the check file (`checks/{task-id}.md`) —
session bookkeeping only. Everything that is the task's deliverable is written by the implementation
expert.

`{steering_dir}` below is the directory that holds the active `steering.md` (e.g.
`.rn/{slug}/`). Write check files under `{steering_dir}/checks/`.

## Process selection

The verification chain by task type (in order). Self-check is produced by the implementation expert
in Execute (work-order element 5); the QA / language / software-engineering reviews are run by the
coordinator in Verify; user review is the final gate in Complete.

| Task type | Verification chain |
|---|---|
| Non-code (docs, config, design) | Self-check → QA expert review → User review |
| Code changes | Self-check → QA expert review → Language expert review → Software-engineering expert review → User review |

## Phase: Execute — coordinator dispatches the implementation expert

**Step — Write the work-order**

The coordinator builds a work-order for the implementation expert. The expert has no conversation
history, so the work-order must carry everything it needs — but only that:

1. **Task** — the task's Purpose, Steps, and Completion criteria, copied from `steering.md`.
2. **Scope** — stay within this task; do not start adjacent tasks; the files expected to be in play.
3. **Method** — (code) write the test first: a failing test that captures the expected behavior, then
   implement until it passes. The work is a hypothesis; it is not done until its tests pass.
4. **Best practices** — apply the domain's best practices (for code: the language/framework's
   conventions, error handling, naming, no duplication; for docs: the repo's existing style).
5. **Self-check** — verify each completion criterion (OK/NG with specific evidence); (code) measure
   coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.) and record line/branch
   coverage and uncovered areas. Write the results to `{steering_dir}/checks/{task-id}.md` using the
   Check file format below.
6. **Return** — report back a **compact summary** only: what changed (files/functions touched), the
   self-check result, and anything the coordinator needs in order to review. Do **not** paste full
   file contents or the trial-and-error — the diff is on disk for the coordinator to read.

**Step — Dispatch the expert**

- Dispatch the implementation expert with the work-order and wait for its summary.
- The expert's intermediate work stays in the subagent; only its summary enters the coordinator's
  context.

## Phase: Verify — coordinator reviews independently

**Step — Read the diff**

- The coordinator inspects `git diff` (and `git status`) itself — its own look at the artifact, not
  the expert's report. Confirm the change matches the task's scope and Completion criteria before
  spending review experts on it.

**Step — QA expert review (subagent)**, then the language and software-engineering experts for code
tasks. Each review expert runs as an independent subagent (Agent tool, no conversation history) —
like the implementation expert, but for judging, not producing. All context the expert needs must be
passed in the prompt — but only that (element 6 says what to withhold). That independence is the
safeguard against bias — protect it.

- Build the review prompt with 6 elements:
  1. **Role** — the expert's domain (QA / language / software-engineering), told to review
     **adversarially** and from its domain's best practices: assume defects exist and actively try to
     break the artifact (boundaries, error paths, integration, missed cases) instead of confirming it
     works.
  2. **Artifact** — the full content or diff under review.
  3. **Criteria** — the expert checklist below.
  4. **Completion criteria** — the task's Completion criteria copied verbatim from `steering.md`.
     These are the bar to clear, not a verdict; passing them verbatim is required and is not
     "leading" — what you withhold is *your* assessment of whether the artifact meets them.
  5. **Output format** — OK/NG per criterion with concrete evidence, plus an overall pass/fail.
  6. **Neutral framing** — pass only what the expert needs to judge independently: goal, artifact,
     Completion criteria, and the checklist. **Never** pass the self-check file
     (`checks/{task-id}.md`), the implementation expert's summary, or any OK/NG verdict; do not defend
     the choices made, and do not hint at the verdict you expect. "All context" means the task
     context, not your conclusions — don't lead the expert; let the evidence decide.
- Dispatch the subagent and collect the verdict.

Expert checklists:

- **QA expert**: tests/verifications meaningful to the purpose (not just "passed"); edge cases
  covered (boundary, error, empty, max, type conversion).
- **Language expert** (code only): best practices (naming, error handling, null/thread safety);
  consistency with existing codebase style; test code in GWT (Given/When/Then) format.
- **Software-engineering expert** (code only): separation of concerns; system-wide integrity
  (interface contracts, API compatibility); maintainability (no duplication, deep nesting, magic
  numbers).

**Step — Triage and re-instruct**

Triage every finding (all experts) — judge it, don't swallow review feedback wholesale:

- Assess each finding on its merits: is it factually correct, and does acting on it serve the goal?
- **Valid** → the coordinator writes improvement instructions and **re-dispatches the implementation
  expert** to fix it (the coordinator does not edit the artifact itself), then re-runs the same review
  expert. Max 3 iterations; valid findings still NG after 3 → record them and escalate to user review
  with the unresolved items.
- **Invalid** → reject it, citing the evidence. A finding is Invalid **only** when it rests on a
  factual error, or falls outside a scope boundary written in the task's Completion criteria — cite
  the specific fact or criterion. Never accept a finding just because an expert raised it.
- Anything else — "valid but I'd rather not act on it", "not aligned with the goal", "minor" — is a
  *valid finding you want to drop*: get user confirmation first. The implementation expert produced
  the artifact, so the coordinator does not get to dismiss criticism of it on its own judgment alone.
- Every finding ends in an explicit fix, an evidence-cited rejection, or a user-confirmed drop —
  never silently dropped, never blindly accepted.

Record the review verdicts into `{steering_dir}/checks/{task-id}.md` (the coordinator already has them
from dispatching the experts — this is bookkeeping, not artifact editing).

## Phase: Complete

**Step — User review**

- The coordinator presents the results to the user. **DO NOT proceed without user approval.** This
  gate is what keeps the user in the conversation at every task boundary.

**Step — Commit and push (subagent)**

- The coordinator checks off the task in `steering.md` (bookkeeping).
- The coordinator dispatches a subagent to commit and push: stage the change, commit with the message
  `{type}: complete task #{id} — {description}` (where `{type}` matches the change — `feat` / `fix` /
  `docs` / `refactor` / `test` / …), then push so the commit lands on the session PR. (The exact
  `complete task #{id}` substring is what `/rn:hi` matches against `git log` when it reconciles
  tasks — keep that substring regardless of the prefix.)

**Step — Advance**

- The coordinator begins the next unchecked task immediately, restarting at Phase: Execute.
- If all tasks are done, propose running the `steering.md` Acceptance criteria.

## Check file format

Write to `{steering_dir}/checks/{task-id}.md`. The implementation expert fills the Completion Criteria
self-check columns; the coordinator fills the review verdicts it collected. Same file, written by
whoever holds the data.

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
- Ready for user review: Yes / No (reason)
```
