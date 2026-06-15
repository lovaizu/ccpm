# Task Workflow

The shared execution loop for a single task, run by a **coordinator** who delegates to **experts**.
`gm` and `hi` read this file when they reach task execution. Run one task at a time.
**1 task = 1 commit.**

The loop exists to **keep the coordinator's context light while preserving quality and keeping the
user in the loop at every task boundary**. An expert's trial-and-error must not pile up in the
coordinator's context; the coordinator stays on as reviewer so the user always has a place to step in.
**Delegation is the means, governed by payoff — not an absolute.** The coordinator delegates a piece
of work *when delegation pays off*: when the work carries real trial-and-error or exploration that
should stay out of its context (code, research, multi-attempt work). For trivial single-step edits and
pure bookkeeping there is no trial-and-error to isolate, and delegation would only add ceremony — the
coordinator does those directly.

- **Coordinator** — the main agent (the one in the conversation). Decomposes the goal, decides *which
  domain's expert* each piece of work needs, dispatches them, reviews what comes back against
  `git diff`, triages findings, and talks with the user. It routes work that carries trial-and-error to
  the expert who owns that domain, and handles trivial edits and bookkeeping itself.
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

What the coordinator may write directly: `steering.md`, the check file (`checks/{task-id}.md`), trivial
single-step edits, and the bookkeeping commit — session bookkeeping plus work with no trial-and-error
to isolate. Everything that carries real trial-and-error or exploration is written by the
implementation expert.

`{steering_dir}` below is the directory that holds the active `steering.md` (e.g.
`.rn/{slug}/`). Write check files under `{steering_dir}/checks/`.

## Process selection

The verification chain by task type (in order). Self-check is produced in Execute (work-order element
5) — by the implementation expert when the work is delegated, or by the coordinator when it edited
directly; the QA / language / software-engineering reviews are run by the coordinator in Verify; user
review is the final gate in Complete.

| Task type | Verification chain |
|---|---|
| Non-code (docs, config, design) | Self-check → QA expert review → User review |
| Code changes | Self-check → QA expert review → Language expert review → Software-engineering expert review → User review |

## Phase: Execute — coordinator dispatches the implementation expert

**Decide: delegate or act directly.** The trigger is whether there is trial-and-error to isolate from
the coordinator's context. If the work carries real trial-and-error or exploration — code, research,
multi-attempt work — dispatch the implementation expert (the steps below). If it is a trivial
single-step edit with no exploration, the coordinator makes the edit itself, performs the self-check
itself (work-order element 5, recorded in the check file), and proceeds to Verify; spinning up an
expert would only add ceremony. Either way the Verify chain (QA review onward) is unchanged.

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

The coordinator holds **the bar**: the artifact should reach the form it ought to take to serve the
goal — correct, clear, and consistent with the codebase's standards (its **proper form**). Triage
every finding against that bar — don't swallow review feedback wholesale, and **don't bounce a
decidable call to the user for lack of a standard**.

- Assess each finding on its merits: is it factually correct, and does acting on it move the artifact
  toward its proper form for the goal?
- **Valid** → the coordinator writes improvement instructions and **re-dispatches the implementation
  expert** to fix it (the coordinator does not edit the artifact itself), then re-runs the same review
  expert. **This includes minor improvements: if the fix is correct and makes the artifact better,
  just apply it — do not ask the user.** Max 3 iterations; valid findings still NG after 3 → record
  them and escalate to user review with the unresolved items.
- **Invalid** → reject it, citing the evidence. A finding is Invalid **only** when it rests on a
  factual error, or falls outside a scope boundary written in the task's Completion criteria — cite
  the specific fact or criterion. Never accept a finding just because an expert raised it.
- **User's call** → escalate to the user *only* when the decision is genuinely theirs: it would
  expand scope, change the agreed direction or a matter of taste, or trade effort against benefit in a
  way only the user can weigh. "It's minor, so I'll just ask" is **not** a reason — decide it against
  the bar.
- Every finding ends in an explicit fix, an evidence-cited rejection, or a user-owned decision —
  never silently dropped, never blindly accepted, never bounced for lack of a standard.

Record the review verdicts into `{steering_dir}/checks/{task-id}.md` (the coordinator already has them
from dispatching the experts — this is bookkeeping, not artifact editing).

## Phase: Complete

**Step — User review**

- The coordinator presents the results to the user. **DO NOT proceed without user approval.** This
  gate is what keeps the user in the conversation at every task boundary.

**Step — Commit and push (coordinator bookkeeping)**

- The coordinator checks off the task in `steering.md` (bookkeeping).
- The coordinator commits and pushes directly — there is no trial-and-error to isolate, so this is its
  own bookkeeping: stage the change, commit with the message
  `{type}: complete task #{id} — {description}` (where `{type}` matches the change — `feat` / `fix` /
  `docs` / `refactor` / `test` / …), then push so the commit lands on the session PR. (The exact
  `complete task #{id}` substring is what `/rn:hi` matches against `git log` when it reconciles
  tasks — keep that substring regardless of the prefix.)

**Step — Advance**

- The coordinator begins the next unchecked task immediately, restarting at Phase: Execute.
- If all tasks are done, propose running the `steering.md` Acceptance criteria.

## Check file format

Write to `{steering_dir}/checks/{task-id}.md`. Whoever did the work fills the Completion Criteria
self-check columns (the implementation expert when delegated, the coordinator when it edited directly);
the coordinator fills the review verdicts it collected. Same file, written by whoever holds the data.

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
