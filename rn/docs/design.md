# rn — design

Why `rn` is shaped the way it is. Not read at runtime.

## What rn is for

A goal outlives a conversation: context runs out, `/clear` wipes the thread, a day ends. `rn` keeps
the session in git as `steering.md`, so a fresh conversation resumes it, and brings the user in
only for what is theirs to decide.

## Principles, and where each lands

1. **Work is instructed by purpose.** The conductor, the implementer and the evaluator each open
   their brief on what their result is for (`references/conductor.md`, `implement.md`,
   `evaluate.md`). A task hands on its Purpose; its Steps are the planned way, which the implementer
   leaves when the Purpose is better served. Only what an agent could not judge from the purpose —
   where output lands, the commit convention, the shapes a later command reads — is written as a
   step.
2. **Results are evaluated by a third party against essential viewpoints.** A fresh evaluator reads
   the result and `steering.md`, never the implementer's account or an earlier verdict, and answers
   a few questions per kind — plan, one task's result, the finished session — about whether the
   result reaches its purpose. The conductor then decides the next move by the purpose, not by a
   count of rounds.
3. **Judgment and execution use different models.** The implementer runs on `sonnet`, the
   evaluator on `opus`; the conductor plans in the conversation.

## What stays

- `steering.md` in git is the session's contract, and its 0.8.0 shape — `Rn version:` line, Goal,
  Acceptance criteria, Assumptions, Rules, Tasks with Purpose and Completion criteria, State — so a
  0.8.0 session migrates by carrying its facts rather than translating them.
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
- **Verdicts are pull request comments.** The user reads each beside the change it judges, and the
  session leaves `steering.md` and the deliverable with nothing to clean up.

## What goes

The per-task chain of self-check, QA, design, craft and verification experts and its `checks/`
files; the per-session `design.md` template; the `complete task #` reconciliation on resume, since
the check-off and its marker are one commit.
