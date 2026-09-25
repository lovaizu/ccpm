# steering.md

The one file a session keeps: what the user wants, how it will be judged, the work, and where the
session stands. Every `/rn:*` command reads it; a fresh conversation resumes from it and git alone.

## Template

`/rn:on` writes a session from this. Every command finds its way by the header lines, headings and
field names, so they stay exactly as written.

```markdown
Rn version: <installed rn version>
Design: <path to the approach a Design sign-off settled — add the line once there is one>

# Goal

<what the user wants and why, as agreed with them — including the aim they had not put into words>

# Acceptance criteria

- <a state the user gains; the Goal is reached when every line holds>

# Assumptions

- **Fact** (<how it was checked>): <what the plan rests on>
- **Assumption**: <what the plan rests on without having checked it>

# Rules

- commit and push every change; one completion marker per task
- <conventions of this session and repository that every task follows>

# Tasks

### #1: Plan sign-off

**Purpose**: The user agrees this plan before any work starts.

**Prerequisites**: none

**Steps**:

- [ ] Approved by the user

**Completion criteria**:

- The user approved the plan.

### #2: <task name>

**Purpose**: <the outcome this task reaches, and the Acceptance criterion it serves>

**Prerequisites**: <task ids, or none>

**Steps**:

- [ ] <step>

**Completion criteria**:

- <a state that shows the Purpose reached>

# State

- **Status**: running
```

## What each part is for

Read these when writing or changing a plan.

- **Goal** — what everything below is judged against, so it holds what the user actually wants and
  why, not only the words of the request.
- **Acceptance criteria** — how the user will know the Goal is reached. Each is a state the user
  gains, not an artifact or a step, so it still holds if the means change.
- **Assumptions** — what the plan rests on, marked as checked or not, so a wrong one is found and
  corrected instead of built on. A scope decision lives here, so the evaluator and the user judge
  against the same record.
- **Rules** — the conventions an implementer could not know from the Goal: how this repository
  commits, where output lands, what it must not touch.
- **Tasks** — worked back from the Acceptance criteria. Each Purpose serves one; each Completion
  criterion shows that Purpose reached. The tasks run only as far as the next decision that is the
  user's — an approach choice where taste, scope, or cost against benefit is theirs to weigh —
  and end at a sign-off task for it: "Design sign-off" for that decision, "Evaluation sign-off"
  when no decision remains before the end. What lies past a decision depends on it, so those tasks
  are written once it is made. A sign-off task has the one step `Approved by the user`.
- **State** — `running` while a conversation holds the session. When the session stops for a fresh
  conversation it reads:

  ```markdown
  - **Status**: paused
  - **Next**: <the task where work picks up, and how far it got>
  - **Feedback**: <the user's revise feedback word for word, or "the unresolved review threads on
    the PR", or none>
  - **Notes**: <what the next conversation needs that nothing else records>
  ```

A task is complete when every step under it is `[x]`. Its check-off is one commit,
`<type>: complete task #N — <task name>`, the only commit whose message carries `complete task #`.

## Entering a session

Every command but `/rn:on` starts here, so it acts on the right session in its current shape.

1. Find `steering.md`. The path known in this conversation; otherwise
   `git log --format= --name-only --diff-filter=AM -- '*/steering.md' | awk 'NF && !seen[$0]++'`,
   keeping the paths that exist on disk and whose "Evaluation sign-off" is not yet complete. One →
   use it. Several → prefer `Status: paused`, then the most recently touched; `/rn:up` proposes it
   and waits, the other commands say which one they took. None → say "No open session. Run
   `/rn:on` to start." and stop.
2. Compare the `Rn version:` line with `version` in `plugin.json` under the rn plugin root. On a
   mismatch, run Migration below before going on.

## Migration

A session written under an older `rn` goes on under this one with nothing run by hand and nothing
it recorded lost.

1. Read the old `steering.md` and everything else in its directory.
2. Rewrite `steering.md` in the template's shape. Carry the Goal, criteria, Assumptions, Rules, the
   `Design:` line, and every task with its id, name, fields and check-offs; a checked step stays
   word for word. Drop an unchecked step that only ran the old `rn`'s own review — a self-check, an
   expert review, a record into `checks/`. Carry every fact of the old `State` into the new fields,
   `Notes` taking what fits nowhere else. The old plan was approved when it started, so no Plan
   sign-off is added.
3. Remove the old `rn`'s process records — under 0.8.0, the `checks/` directory — and nothing else.
4. Set `Rn version:` to the installed version; commit `chore: migrate session to rn <version>` and
   push.
5. Have the migrated plan evaluated as in `conductor.md`, kind Plan, handing the evaluator the
   commit before the migration as the old session, then go on with the command that found it.
