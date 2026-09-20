# rn — design

Why `rn` is shaped the way it is. Not read at runtime.

## What rn is for

A goal outlives a conversation: context runs out, `/clear` wipes the thread, a day ends. `rn` keeps
the session's contract in git as `steering.md`, so a fresh conversation resumes it, and stops the
user at exactly three decisions — the plan, a design when one has to be settled before build, and
the evaluation of the result. Everything else runs without asking.

## Principles, and where each lands

1. **Work is instructed by purpose and intent.** Every step in every `SKILL.md` and reference opens
   with what it is for, then what to do; a step whose purpose cannot be stated is not in `rn`. A
   task is stated by its Objective and Success criteria and handed to the implementer that way
   (`references/task.md` step 1), never as a recipe.
2. **Results are evaluated by a third party against essential viewpoints.** One evaluation per
   artifact, by an evaluator that did not build it, against a few fixed questions per kind that ask
   whether it does its job — never a chain of self-checks, never "did the step run"
   (`references/evaluate.md`). The verdict goes on the PR, where the user reads it rendered.
3. **Judgment and execution use different models.** The implementer is dispatched with
   `model: sonnet`, the evaluator with `model: opus`; the conductor plans in the conversation on the
   user's model. The `Agent` tool's `model` parameter is the whole mechanism.

## Decisions

- **Criteria are states, at both levels.** The Goal has Success criteria; each task has an
  Objective and its own Success criteria. A criterion names a state of the world, never an artifact
  or a step, so it survives a change of means and the evaluator judges outcomes. Each level is
  judged against the one above it: Success criteria against the Goal, an Objective against the
  Goal, a task's Success criteria against its Objective.
- **The conductor works toward the Goal; it does not only pass messages.** Every command takes
  the role up in its first step (`references/conductor.md`): it reads every result before the
  evaluator sees it, folds what each round teaches into `steering.md`, and interrupts the user
  only when the agreed Goal, criteria or design would change. Each check it makes sits in the step
  where it applies, not in a list.
- **Three gates, and no other stop.** The plan gate ends `/rn:on`; a "Design sign-off" task stops
  where planning placed one; "Evaluation sign-off" is always the last task. `/rn:ty` and `/rn:gm`
  are the only verdict vocabulary.
- **A session leaves `steering.md` and the deliverable.** Evaluations are PR comments; a design
  lives in the project's own documents, pointed to by the `Design:` line. `rn` writes no process
  file of its own.
- **One completion marker per task.** `complete task #N` appears in the check-off commit alone;
  `/rn:up` reconciles from it.
- **An older session is rebuilt, not patched.** A version mismatch rewrites `steering.md` from the
  current template with the old file as input, carrying every fact, so the session goes on at the
  current bar (`references/steering.md`, Migration).
- **Documents hold current intent only.** `steering.md`, a design, and this file record what is
  decided and why; history lives in git and on the PR.

## Shape

Five user-invoked commands — `/rn:on`, `/rn:dn`, `/rn:up`, `/rn:ty`, `/rn:gm` — and three
references: `conductor.md` (the role every command runs under), `steering.md` (the file and its
migration), `task.md` (the loop), `evaluate.md` (the questions). The session-status block opens every stop.
