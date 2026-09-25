# rn — design

Why `rn` is shaped the way it is. Not read at runtime.

## What rn is for

A goal outlives a conversation: context runs out, `/clear` wipes the thread, a day ends. `rn` keeps
the session in git as `steering.md`, so a fresh conversation resumes it, and brings the user in
only for what is theirs to decide.

## How the prompt is built

`rn`'s prompt text is judged as any prompt is, on four points; each lands in it as follows.

- **Structure — generation and evaluation are split, and a role between them decides.** The
  implementer builds, a fresh evaluator judges without the implementer's account or an earlier
  verdict, and the conductor decides each next move by the Goal, not by a count of rounds
  (`references/conductor.md`).
- **Generation — handed the purpose, checked against it.** A task hands on its Purpose and the Goal
  it serves; its Steps are the planned way, which the implementer leaves when the Purpose is better
  served, and it checks its result on the thing itself before returning (`implement.md`).
- **Evaluation — a few viewpoints drawn from the purpose.** Each kind — plan, one task's result,
  the finished session — has a few questions about whether the result reaches its purpose, answered
  by running it where it runs (`evaluate.md`).
- **Work steps — only what the purpose cannot tell.** Where output lands, the commit convention and
  the shapes a later command reads are steps in the flow; everything an agent can judge from the
  purpose is left to it.

## What stays

- `steering.md` in git is the session's contract, and its 0.8.0 sections — Goal, Acceptance
  criteria, Assumptions, Rules, Tasks with Purpose and Completion criteria, State — so a 0.8.0
  session migrates by carrying its facts rather than translating them.
- Sign-offs through `/rn:ty` and `/rn:gm`, and the session map heading every stop.

## What changes

- **The goal is drawn out, not taken.** `/rn:on` shows its reading one point at a time until the
  aim the user had not put into words is agreed, because a plan built on the literal request is
  judged against the wrong thing.
- **The plan reaches only the next decision.** Tasks past a decision the user makes depend on it,
  so they are written after it, when they can be right.
- **The plan's approval is a task.** "Plan sign-off" joins "Design sign-off" and "Evaluation
  sign-off", so every pending decision is the first incomplete task and a resume finds it without
  a separate record.
- **Every verdict ends the conversation's part.** `/rn:ty`, `/rn:gm` and `/rn:dn` record the
  decision and `State` and stop; `/rn:up` is the one way back in. A long session then runs in fresh
  conversations by default, and the user goes on without clearing just by saying so.
- **Verdicts are committed files.** Each goes into the session's `evaluations/` as the evaluator
  wrote it, so the user reads it on the pull request beside the change it judges, and a resume
  finds it in git instead of fetching a comment back to trust it. The directory goes at the
  Evaluation sign-off; the verdicts stay in the PR's history.
- **The session's fixed facts are frontmatter.** Version, issue, pull request, design and
  `running` / `paused` sit in YAML that GitHub shows as a table and a command reads without
  parsing prose. Finished is not a status: it is read from the Evaluation sign-off being complete,
  so no field can contradict the record.
- **A session is found by its branch.** It lives on its own branch and pull request, so a command
  takes the session its branch changed, or offers the ones with an open pull request; history
  across branches is not searched, since it turns up other branches' and merged sessions.
- **Work a sign-off asks for is a task.** A sign-off has nothing to rebuild, so a verdict or
  feedback that asks for work there becomes a new task placed before it, with the next unused id,
  and ids in commit messages keep pointing at their task.

## What goes

The per-task chain of self-check, QA, design, craft and verification experts and its `checks/`
files; the per-session `design.md` template; the `complete task #` reconciliation on resume, since
the check-off and its marker are one commit.
