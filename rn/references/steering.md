# steering.md

The one file a session keeps: what the user wants, how it will be evaluated, the work, and where the
session stands. Every `/rn:*` command reads it; a fresh conversation resumes from it and git alone.

## Template

Every command finds its way by the field names and headings, so they stay exactly as written.

```markdown
---
rn: <installed rn version>
issue: <the issue this session serves — omit the line when there is none>
pr: <the session's pull request URL — added once it is open>
design: <path to the document setting out a Design sign-off's choices — added once there is one>
status: running
---

# Goal

<what the user wants and why, as agreed with them — including what they had not put into words>

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

**Purpose**: <what this task reaches, and the line of Goal reached when it serves>

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
- **Goal** — what everything below is evaluated against, so it holds what the user actually wants and
  why, not only the words of the request.
- **Goal reached when** — how the user will know the Goal is reached. Each line is a state the user
  gains, not an artifact or a step, so it still holds if the means change. The heading is the start
  of each line's sentence, so a line reads as a state reached, not work done.
- **Assumptions** — what the plan rests on, marked as checked or not, so a wrong one is found and
  corrected instead of built on. A scope decision, what was ruled out of scope, and each choice the
  user made at a sign-off live here, so the evaluator and the user evaluate against the same record.
- **Rules** — the conventions an implementer could not know from the Goal: how this repository
  commits, where output lands, what it must not touch.
- **Tasks** — worked back from Goal reached when. Each Purpose serves a line of it; each line of Purpose
  reached when is a state that shows that Purpose reached, as Goal reached when does for the Goal. The
  tasks run only as far as the next decision that is the user's — an approach where taste, scope, or
  cost against benefit is theirs to weigh — and end at a sign-off task for it: "Design sign-off" for
  that decision, "Evaluation sign-off" when no decision remains before the end. What lies past a
  decision depends on it, so those tasks are written once the user has chosen. A sign-off task has the
  one step `Approved by the user`. The session ends at the Evaluation sign-off, before the merge, which
  is the user's. Tasks run in the order they appear; a task added later takes the next unused id, so ids
  already in commit messages keep pointing at their task.
- **State** — where the session stands between conversations. `Next` is the first task not yet
  complete and how far it got — its work done but not yet evaluated, or evaluated but not yet
  decided on; `Feedback` the user's words asking for a revision, kept until the revision passes its
  evaluation, or none; `Notes` what the next conversation needs that nothing else records.

A task is complete when every step under it is `[x]`. Beside `steering.md`, the session's directory
holds `evaluations/`, every evaluation as its evaluator wrote it, until the Evaluation sign-off.

## Finding the session

Every command but `/rn:on` starts here, so it acts on the right session. A session lives on its own
branch, so the branch names it.

1. The `steering.md` this conversation has been working on, if there is one.
2. Otherwise the `.rn/*/steering.md` this branch changed:
   `git diff --name-only $(git merge-base HEAD origin/HEAD) HEAD -- '.rn/*/steering.md'`. When
   `origin/HEAD` is not set, `git remote set-head origin --auto` sets it first.
3. Otherwise the sessions with an open pull request: for each branch in
   `gh pr list --state open --json headRefName`, the `.rn/*/steering.md` it changed. Propose one, a
   paused one first, with its branch to switch to, and wait for the user.

More than one found → ask which. A session whose Evaluation sign-off is complete is finished → say so
and stop. None → say "No open session. Run `/rn:on` to start." and stop.

A session started under an earlier `rn` has no `rn` field in its frontmatter, or one that differs from
`version` in `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`. `/rn:up` brings it up to date, below;
any other command says so, and stops: "This session was started under an earlier rn. Run `/rn:up`
first."

## Bringing an older session up to date

Rewrite `steering.md` in the shape of the template, so this `rn` can run it, with none of its plan or
progress lost:

- Carry the Goal, the Assumptions, the Rules, and every task with its id, name, fields, and
  check-offs; a checked step stays word for word. Old names for the same thing take the template's
  names: Acceptance criteria become Goal reached when, Completion criteria become Purpose reached
  when. Wording the user approved stays as it is.
- Lift the old header lines, the issue and pull request the old `State` names, and a paused status
  with its date, into the frontmatter; carry every other fact of the old `State` into `Next`,
  `Feedback`, and `Notes`.
- Drop an unchecked step that only ran the old `rn`'s own review — a self-check, an expert review, a
  record into `checks/` — and remove those records. A task whose work steps are checked but whose
  review was not finished has its work done but not yet evaluated: keep one unchecked step
  `Evaluated`, and say so in `Next` with its commits. A sign-off task gets the one step `Approved by
  the user`, checked if the old task was complete.
- When the user has not yet approved the plan — no task has a checked step and nothing records their
  approval — add a Plan sign-off as the first task, and set `Next` to it.
- Tasks after a Design sign-off not yet approved move into `Notes`, as tasks planned before the
  choice, to be rewritten once the user has chosen.

Check the rewrite against the commit before it, part by part, so nothing is lost. Set `rn` to the
installed version, commit `chore: bring session up to rn {version}`, push, and have the plan
evaluated as in `${CLAUDE_PLUGIN_ROOT}/references/turn.md`, deciding on it as there. A More on wording
the user approved is not acted on: name it to the user at the next stop.
