# Task Workflow

The shared execution loop for a single task, run by a **coordinator** who delegates to **experts**.
`gm` and `hi` read this file when they reach task execution. Run one task at a time.

**The deliverable/ledger split (canonical statement).** All hands-on work on the deliverable —
generating it, fixing it, committing and pushing it — is the **implementation expert's**, by default
and unconditionally. The split line is *does it carry exploration or trial-and-error*, not *does it
write to the repo*. The only direct-write carve-out is the coordinator's **own ledger**: `steering.md`,
the review verdicts it already holds (recorded into the check file), and the commits of those — these
carry no trial-and-error to isolate, so the coordinator does them directly. It never touches the
deliverable or its git history.

> Why: the coordinator's context stays light (an expert's trial-and-error stays in the subagent), and
> because the coordinator stays on as reviewer rather than fully delegating, the user keeps a place to
> step in at every task boundary.

**One task = one completion marker.** Deliverable commits accumulate freely on the branch, each pushed
as made; the single `complete task #{id}` marker rides on the coordinator's post-approval steering
check-off commit — so exactly one marker exists per task (canonical rule in Phase: Complete).

- **Coordinator** — the main agent (the one in the conversation). Decomposes the goal, decides *which
  domain's expert* each piece of work needs, dispatches them, reviews what comes back against the
  committed diff, triages findings, re-instructs, updates `steering.md`, and talks with the user. Owns
  orchestration, dialogue, and its own ledger — never the deliverable (per the split above).
- **Experts** — subagents (Agent tool, no conversation history), each specialized in one domain and
  each applying **its domain's best practices**. The coordinator dispatches the right one for the job
  and gets back a **compact summary**. The experts in this loop:
  - **Implementation expert** — produces, fixes, and commits/pushes the task's deliverable (code/docs).
  - **QA expert** — adversarially verifies the result.
  - **Language expert** (code only) — judges language-level craft.
  - **Software-engineering expert** (code only) — judges design and system integrity.

`{steering_dir}` below is the directory that holds the active `steering.md` (e.g.
`.rn/{slug}/`). Write check files under `{steering_dir}/checks/`.

## Process selection

The verification chain by task type, in order:

| Task type | Verification chain |
|---|---|
| Non-code (docs, config, design) | Self-check → QA expert review → User review |
| Code changes | Self-check → QA expert review → Language expert review → Software-engineering expert review → User review |

Self-check is produced in Execute (work-order element 5) by the implementation expert; the QA /
language / software-engineering reviews run in Verify; user review is the final gate in Complete, on
the pushed deliverable.

## Phase: Execute — coordinator dispatches the implementation expert

**Dispatch the implementation expert for the deliverable, unconditionally.** There is no "delegate or
act directly" decision (the coordinator never produces the deliverable — per the split). Write the
work-order, dispatch, wait for the summary.

**Step — Write the work-order**

The expert has no conversation history, so the work-order must carry everything it needs — but only
that:

1. **Task** — the task's Purpose, Steps, and Completion criteria, copied from `steering.md`.
2. **Scope** — stay within this task; do not start adjacent tasks; the files expected to be in play.
3. **Method** — (code) write the test first: a failing test that captures the expected behavior, then
   implement until it passes. The work is a hypothesis; it is not done until its tests pass.
4. **Best practices** — apply the domain's best practices (for code: the language/framework's
   conventions, error handling, naming, no duplication; for docs: the repo's existing style).
5. **Self-check** — verify each completion criterion (OK/NG with specific evidence); (code) measure
   coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.) and record line/branch
   coverage and uncovered areas. Write the results to `{steering_dir}/checks/{task-id}.md` using the
   Check file format below, but **do not commit it** — that file is the coordinator's ledger (see Check
   file format).
6. **Commit & push the deliverable** — stage the deliverable **paths explicitly** (`git add
   <path>…`); **never `git add -A` or `git add .`**, which would sweep the check-file ledger
   (`checks/{task-id}.md`) into a plain deliverable commit and break "the check file is the
   coordinator's ledger, committed by the coordinator." Commit with a plain conventional message
   (`feat:` / `fix:` / `docs:` / … matching the change), and push so it lands on the session PR. The
   message must **not** contain the string `complete task #` (that marker belongs to the coordinator's
   check-off — see Phase: Complete). Commits accumulate freely across feedback rounds within the task;
   push each as made and **never force-push**. Subagent commit and push capability has been verified
   available via the Agent tool, so the expert does this itself; the fallbacks below are last-resort
   paths for capability-less environments, not the normal flow. **If the expert cannot push** in its
   environment (sandbox/auth), it says so in its return summary and leaves the commit in place; the
   coordinator then pushes that already-made commit — a push only, the commit stays the expert's, never
   the coordinator authoring or amending the deliverable. **If the expert cannot commit at all** (its
   environment blocks `git commit`), it says so and reports that it produced the change, left in the
   working tree; the coordinator then runs the commit **mechanically** over the expert's already-written
   change — git mechanics only, the content stays the expert's, and the coordinator never authors,
   edits, or regenerates the deliverable.
7. **Return** — report back a **compact summary** only: what changed (files/functions touched), the
   self-check result, and the commit SHA(s) plus that the deliverable was pushed. Do **not** paste full
   file contents or the trial-and-error — the diff is on disk for the coordinator to read.

**Step — Dispatch the expert**

- Capture the task's **starting commit** — current `HEAD`, just before the expert's first deliverable
  commit — so Verify's `git diff <task's starting commit>..HEAD` is computable across feedback rounds.
- Dispatch the implementation expert with the work-order and wait for its summary.
- The expert's intermediate work stays in the subagent; only its summary enters the coordinator's
  context.

## Phase: Verify — coordinator reviews independently

**Step — Read the committed diff**

- The expert already committed and pushed the **deliverable** during Execute (work-order element 6),
  so there is no uncommitted deliverable change in the tree — but the expert also wrote
  `checks/{task-id}.md` and left it uncommitted (Execute element 5), and that file is tracked, so
  `git status` will show it. Expect exactly that: `git status` showing only the check-file ledger is
  normal, not a deliverable change. The coordinator inspects the **committed** deliverable change
  instead: `git show <sha>` for the SHA(s) the expert returned, or `git diff <task's starting
  commit>..HEAD` for this task's cumulative change. This is its own look at the artifact, not the
  expert's report. Confirm the change matches the task's scope and Completion criteria before spending
  review experts on it.

**Step — QA expert review (subagent)**, then the language and software-engineering experts for code
tasks. Each review expert runs as an independent subagent (Agent tool, no conversation history) — for
judging, not producing. Pass all context it needs in the prompt — but only that.

Why: independence is the safeguard against bias; the Neutral framing element (6, below) says what to
withhold so you do not lead the expert.

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

**Triage every finding against the bar** — the form the artifact ought to take to serve the goal:
correct, clear, and consistent with the codebase's standards (its **proper form**). Don't swallow
review feedback wholesale, and **don't bounce a decidable call to the user for lack of a standard**.
Assess each finding on its merits: is it factually correct, and does acting on it move the artifact
toward its proper form? Each finding ends in exactly one of:

- **Valid** → fix it. **Every deliverable-touching fix goes to the implementation expert** — no matter
  its size, because every line of the deliverable and its git history is the expert's. Write
  improvement instructions and dispatch the implementation expert (a fresh subagent, no memory of the
  first pass) rather than taking over its domain work: reuse the original work-order, point it at the
  current on-disk state to build on (not regenerate from scratch), and have it commit/push the fix as a
  fresh deliverable commit (work-order element 6 — accumulating, never force-pushed). **This includes
  minor improvements: if the fix is correct and makes the artifact better, dispatch it — do not ask the
  user.** After the expert returns, re-run the same review expert on the result before closing the
  finding; and if the fix could plausibly affect a dimension another expert already cleared (e.g. a
  correctness fix that reshapes design or wording), re-run that expert too, not only the originating
  one. Cap this at 3 iterations, where one iteration is a single fix and all its re-reviews (the
  originating expert plus any regression re-runs count together as one, not separately); valid findings
  still NG after 3 → record them and escalate to user review with the unresolved items.
- **Invalid** → reject it, citing the evidence. A finding is Invalid **only** when it rests on a
  factual error, or falls outside a scope boundary written in the task's Completion criteria — cite
  the specific fact or criterion. Never accept a finding just because an expert raised it.
- **User's call** → escalate to the user *only* when the decision is genuinely theirs: it would
  expand scope, change the agreed direction or a matter of taste, or trade effort against benefit in a
  way only the user can weigh. "It's minor, so I'll just ask" is **not** a reason — decide it against
  the bar.

Never silently drop, blindly accept, or bounce a finding for lack of a standard. Record the review
verdicts into the check file — the coordinator's ledger, not artifact editing (see Check file format).

## Phase: Complete

**Step — User review (on the PR)**

- The deliverable is already committed and pushed (by the implementation expert, during Execute and
  any Verify fix rounds), so the user reviews it on the session PR — where diffs and long documents
  render properly, per `.claude/rules/push-and-review.md`. The coordinator points the user there and
  presents the results. **DO NOT proceed without user approval** — this gate keeps the user in the loop
  at every task boundary.

**Step — Check off steering (coordinator's ledger)**

- After approval, check off the task in `steering.md` directly (coordinator's ledger, no
  trial-and-error to isolate).
- **Commit that check-off with the single completion marker** — message `{type}: complete task #{id} —
  {description}` (`{type}` matches the change — `feat` / `fix` / `docs` / `refactor` / `test` / …), then
  push to the session PR. This is the **canonical, single completion marker** for the task: deliverable
  commits carry plain messages, and only this check-off commit carries the `complete task #{id}`
  substring. That exact substring is what `/rn:hi` matches against `git log` when it reconciles tasks —
  keep it regardless of the prefix.

**Step — Advance**

- The coordinator begins the next unchecked task immediately, restarting at Phase: Execute.
- If all tasks are done, propose running the `steering.md` Acceptance criteria.

## Check file format

Write to `{steering_dir}/checks/{task-id}.md`. **This file is the coordinator's ledger (canonical
ownership rule).** The implementation expert writes the Completion Criteria self-check columns into it
but **does not commit it** (Execute element 6 commits the deliverable only). The coordinator fills in
the review verdicts it collected and commits the file as part of its ledger — naturally on the
post-approval steering check-off commit. Same file, written by whoever holds the data; committed by the
coordinator.

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
