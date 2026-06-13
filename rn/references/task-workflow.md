# Task Workflow

The shared execution loop for a single task, structured as **Phase > Step > Action**. `gm` and
`hi` read this file when they reach task execution. Run one task at a time. **1 task = 1 commit.**

`{steering_dir}` below is the directory that holds the active `steering.md` (e.g.
`.rn/{slug}/`). Write check files under `{steering_dir}/checks/`.

## Process selection

Choose the Verify-phase steps by task type:

| Task type | Verify phase steps |
|---|---|
| Non-code (docs, config, design) | Self-check → QA review → User review |
| Code changes | Self-check → QA review → Language expert review → Software engineer review → User review |

## Phase: Execute

**Step — Do the work**

- Carry out the task's Steps from `steering.md` until each step is complete.
- (code) Write the test first — a failing test that captures the expected behavior — then implement
  until it passes. The work is a hypothesis; it is not done until its tests pass.
- Stay within the task's scope. Do not start adjacent tasks.

## Phase: Verify

**Step — Self-check**

- Verify each completion criterion, recording OK/NG with specific evidence.
- (code) Measure coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.);
  record line/branch coverage and uncovered areas.
- Write results to `{steering_dir}/checks/{task-id}.md` using the Check file format below.

**Step — QA review (subagent)**, then the expert reviews for code tasks. Each reviewer runs as an
independent subagent (Agent tool, no conversation history), so all context must be passed in the
prompt. That independence is the safeguard against bias — protect it.

- Build the review prompt with 6 elements:
  1. **Role** — the reviewer persona (QA engineer / language expert / software engineer), told to
     review **adversarially**: assume defects exist and actively try to break the artifact
     (boundaries, error paths, integration, missed cases) instead of confirming it works.
  2. **Artifact** — the full content or diff under review.
  3. **Criteria** — the reviewer checklist below.
  4. **Completion criteria** — the task's Completion criteria copied verbatim from `steering.md`.
  5. **Output format** — OK/NG per criterion with concrete evidence, plus an overall pass/fail.
  6. **Neutral framing** — present the artifact and criteria only. Do not reveal your own
     conclusions or self-check verdict, defend the choices made, or hint at the verdict you expect.
     Don't lead the reviewer; let the evidence decide.
- Dispatch the subagent and collect the verdict.

Reviewer checklists:

- **QA engineer**: tests/verifications meaningful to the purpose (not just "passed"); edge cases
  covered (boundary, error, empty, max, type conversion).
- **Language expert** (code only): best practices (naming, error handling, null/thread safety);
  consistency with existing codebase style; test code in GWT (Given/When/Then) format.
- **Software engineer** (code only): separation of concerns; system-wide integrity (interface
  contracts, API compatibility); maintainability (no duplication, deep nesting, magic numbers).

Triage every finding (all reviewers) — judge it, don't swallow review feedback wholesale:

- Assess each finding on its merits: is it factually correct, and does acting on it serve the goal?
- **Valid** → fix it, then re-run the same reviewer. Max 3 iterations; valid findings still NG after
  3 → record them and escalate to user review with the unresolved items.
- **Invalid** (factual error, out of scope, or not aligned with the goal) → reject it and state the
  rationale and evidence for rejecting. Never accept a finding just because a reviewer raised it.
- Every finding ends in an explicit fix or a reasoned rejection — never silently dropped, never
  blindly accepted. To drop a *valid* finding without fixing it, get user confirmation first.

## Phase: Complete

**Step — User review**

- Present the results. **DO NOT proceed without user approval.**

**Step — Commit**

- Check off the task in `steering.md`.
- Commit with the message: `docs: complete task #{id} — {description}`.
  (This exact `complete task #{id}` phrasing is what `/rn:hi` matches against `git log` when it
  reconciles tasks — keep the format.)

**Step — Advance**

- Begin the next unchecked task immediately, restarting at Phase: Execute.
- If all tasks are done, propose running the `steering.md` Verification criteria.

## Check file format

Write to `{steering_dir}/checks/{task-id}.md`:

```markdown
# {task-id} Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| (text) | OK / NG | (what was confirmed) | OK / NG | (findings) |

## QA Engineer Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Meaningful tests/verification | OK / NG | |
| Edge case coverage | OK / NG | |

## Expert Reviews (code changes only)

### Language Expert

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Best practices | OK / NG | |
| Codebase style consistency | OK / NG | |
| GWT test format | OK / NG | |

### Software Engineer

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Separation of concerns | OK / NG | |
| System integrity | OK / NG | |
| Maintainability | OK / NG | |

## Overall Verdict

- Self-check: OK / NG
- QA: OK / NG
- Language expert: OK / NG / N/A
- Software engineer: OK / NG / N/A
- Ready for user review: Yes / No (reason)
```
