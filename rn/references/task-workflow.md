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
- Stay within the task's scope. Do not start adjacent tasks.

## Phase: Verify

**Step — Self-check**

- Verify each completion criterion, recording OK/NG with specific evidence.
- (code) Measure coverage with a project-appropriate tool (Jest, pytest, JaCoCo, gcov, etc.);
  record line/branch coverage and uncovered areas.
- Write results to `{steering_dir}/checks/{task-id}.md` using the Check file format below.

**Step — QA review (subagent)**, then the expert reviews for code tasks. Each reviewer runs as an
independent subagent (Agent tool, no conversation history), so all context must be passed in the
prompt.

- Build the review prompt with 5 elements:
  1. **Role** — the reviewer persona (QA engineer / language expert / software engineer).
  2. **Artifact** — the full content or diff under review.
  3. **Criteria** — the reviewer checklist below.
  4. **Completion criteria** — the task's Completion criteria copied verbatim from `steering.md`.
  5. **Output format** — OK/NG per criterion with evidence, plus an overall pass/fail.
- Dispatch the subagent and collect the verdict.
- Apply the iteration protocol: any NG → fix → re-run the same reviewer; max 3 iterations; still
  NG after 3 → record the findings and escalate to user review with the unresolved items.

Reviewer checklists:

- **QA engineer**: tests/verifications meaningful to the purpose (not just "passed"); edge cases
  covered (boundary, error, empty, max, type conversion).
- **Language expert** (code only): best practices (naming, error handling, null/thread safety);
  consistency with existing codebase style; test code in GWT (Given/When/Then) format.
- **Software engineer** (code only): separation of concerns; system-wide integrity (interface
  contracts, API compatibility); maintainability (no duplication, deep nesting, magic numbers).

Review policy (all reviewers):

- Address every finding. Never skip one as "minor" or "low priority".
- To skip a finding, get user confirmation first.
- Only dismiss a finding when it contains a factual error, and state the evidence.

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
