# steering.md

The one file a session keeps: what the user wants, how it will be judged, the work, and where the
session stands. Every `/rn:*` command reads it; a fresh conversation resumes from it and git alone.

## Template

`/rn:on` writes a session from this. Every command finds its way by the field names and headings,
so they stay exactly as written.

```markdown
---
rn: <installed rn version>
issue: <the issue this session serves — omit the line when there is none>
pr: <the session's pull request URL — added once it is open>
design: <path to the approach a Design sign-off settled — added once there is one>
status: running
---

# Goal

<what the user wants and why, as agreed with them — including the aim they had not put into words>

# Acceptance criteria

- <a state the user gains; the Goal is reached when every line holds>

# Assumptions

- **Fact** (<how it was checked>): <what the plan rests on>
- **Assumption**: <what the plan rests on without having checked it>

# Rules

- commit and push every change
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

- **Next**: #1 Plan sign-off
- **Feedback**: none
- **Notes**: none
```

## What each part is for

Read these when writing or changing a plan.

- **Frontmatter** — the session's fixed facts, in YAML so GitHub shows them as a table above the
  plan and a command reads them without parsing prose. `status` is `paused` from a hand-off until
  `/rn:up`, with `paused_at: <YYYY-MM-DD>` beside it for that time, and `running` otherwise. That
  a session is finished is not a field: its "Evaluation sign-off" is complete.
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
  are written from the approach once it is settled, and the user approves the approach and them
  together at its sign-off. A sign-off task has the one step `Approved by the user`. The session
  ends at "Evaluation sign-off", before the merge, which is the user's; work that can only follow
  the merge — a tag, a release — is written in `Notes` and named when the session closes. Tasks run
  in the order they appear; a task added later takes the next unused id, so ids already in commit
  messages keep pointing at their task.
- **State** — where the session stands between conversations, written at each hand-off and left as
  it is by `/rn:up` until acted on or rewritten. `Next` is the first task not yet complete and how
  far it got; `Feedback` the user's revision not yet acted on, or none; `Notes` what the next
  conversation needs that nothing else records.

A task is complete when every step under it is `[x]`. Beside `steering.md`, the session's
directory holds `evaluations/`, every verdict as its evaluator wrote it, until the "Evaluation
sign-off" is approved.

## Entering a session

Every command but `/rn:on` starts here, so it acts on the right session. A session lives on its own
branch, so the branch names it.

1. The path known in this conversation, if there is one.
2. Otherwise the `.rn/*/steering.md` this branch changed:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`. When
   `origin/HEAD` is not set, `git remote set-head origin --auto` sets it first.
3. Otherwise the sessions with an open pull request: for each branch in
   `gh pr list --state open --json headRefName`, the `.rn/*/steering.md` it changed, read at that
   branch. Propose one — a paused one first — with its branch to switch to, and wait.

More than one found → ask which. A session whose "Evaluation sign-off" is complete is finished →
say so and stop. None → say "No open session. Run `/rn:on` to start." and stop.

## Migration

`/rn:up` runs this when the session's `rn` field — or, written before 0.9.0, its `Rn version:`
line — differs from `version` in `.claude-plugin/plugin.json` under the rn plugin root, so a
session written under an older `rn` goes on under this one with nothing run by hand and nothing it
recorded lost.

1. Read the old `steering.md` and everything else in its directory.
2. Rewrite `steering.md` in the template's shape. Lift the old header lines, and the issue and pull
   request the old `State` names, into the frontmatter. Carry the Goal, criteria, Assumptions,
   Rules, and every task with its id, name, fields and check-offs; a checked step stays word for
   word. Drop an unchecked step that only ran the old `rn`'s own review — a self-check, an expert
   review, a record into `checks/`. A sign-off task gets the one step `Approved by the user` —
   checked if the old task was complete; its other unchecked steps that do work go into a task
   placed before it, with the next unused id, or into `Notes` when they wait on the merge. Carry
   every fact of the old `State` into the new fields, `Notes` taking what fits nowhere else. The
   old plan was approved when it started, so no Plan sign-off is added.
3. When the directory's slug names a ticket rather than the work, `git mv` it to a slug for what
   the work produces; the ticket has the `issue` field.
4. Remove the old `rn`'s process records — under 0.8.0, the `checks/` directory — and nothing else.
5. Set `rn` to the installed version; commit `chore: migrate session to rn <version>` and push.
6. Have the migrated plan evaluated as in `conductor.md`, kind Plan, handing the evaluator the
   commit before the migration as the old session, and plan again on its verdict there.
