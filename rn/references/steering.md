# steering.md

The one file a session keeps: what the user wants, how it will be judged, the work, and where the
session stands. Every `/rn:*` command reads it; a fresh conversation resumes from it and git alone.

## Template

Every command finds its way by the field names and headings, so they stay exactly as written.

```markdown
---
rn: <installed rn version>
issue: <the issue this session serves — omit the line when there is none>
pr: <the session's pull request URL — added once it is open>
design: <path to the approach a Design sign-off settled — added once there is one>
status: running
---

# Request

<the user's words that started the session, as they wrote them, and the issue they named>

# Goal

<what the user wants and why, as agreed with them — including the aim they had not put into words>

# Goal reached when

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

**Purpose reached when**:

- The user approved the plan.

### #2: <task name>

**Purpose**: <the outcome this task reaches, and the line of Goal reached when it serves>

**Prerequisites**: <task ids, or none>

**Steps**:

- [ ] <step>

**Purpose reached when**:

- <a state that shows the Purpose reached>

# State

- **Next**: #1 Plan sign-off
- **Feedback**: none
- **Notes**: none
```

## What each part is for

- **Frontmatter** — the session's fixed facts, in YAML so GitHub shows them as a table above the
  plan and a command reads them without parsing prose. `status` is `paused` from `/rn:dn` until
  `/rn:up`, with `paused_at: <YYYY-MM-DD>` beside it, and `running` otherwise. That a session is
  finished is not a field: its Evaluation sign-off is complete.
- **Request** — the user's own words, kept as they wrote them, so the Goal can always be checked
  against what was asked and not only against what was understood.
- **Goal** — what everything below is judged against, so it holds what the user actually wants and
  why, not only the words of the request.
- **Goal reached when** — how the user will know the Goal is reached. Each line is a state the user
  gains, not an artifact or a step, so it still holds if the means change. The heading is the start
  of each line's sentence, so a line reads as a state reached, not work done.
- **Assumptions** — what the plan rests on, marked as checked or not, so a wrong one is found and
  corrected instead of built on. A scope decision, and what was ruled out of scope, lives here, so
  the evaluator and the user judge against the same record.
- **Rules** — the conventions an implementer could not know from the Goal: how this repository
  commits, where output lands, what it must not touch.
- **Tasks** — worked back from Goal reached when. Each Purpose serves a line of it; each line of Purpose
  reached when is a state that shows that Purpose reached, as Goal reached when does for the Goal. The
  tasks run only as far as the next decision that is the user's — an approach where taste, scope, or
  cost against benefit is theirs to weigh — and end at a sign-off task for it: "Design sign-off" for
  that decision, "Evaluation sign-off" when no decision remains before the end. What lies past a
  decision depends on it, so those tasks are written once it is settled, and the user approves the
  approach and them together at its sign-off. A sign-off task has the one step `Approved by the user`.
  The session ends at the Evaluation sign-off, before the merge, which is the user's. Tasks run in the
  order they appear; a task added later takes the next unused id, so ids already in commit messages keep
  pointing at their task.
- **State** — where the session stands between conversations. `Next` is the first task not yet
  complete and how far it got; `Feedback` the user's revision not yet acted on, or none; `Notes`
  what the next conversation needs that nothing else records.

A task is complete when every step under it is `[x]`. Beside `steering.md`, the session's directory
holds `evaluations/`, every verdict as its evaluator wrote it, until the Evaluation sign-off.
