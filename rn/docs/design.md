# rn — design

Why `rn` is shaped the way it is. Not read at runtime.

## What rn is for

A goal outlives a conversation: context runs out, `/clear` wipes the thread, a day ends. `rn` keeps
the session's contract in git as `steering.md`, so a fresh conversation resumes it, and stops the
user at exactly three decisions — the plan, a design when one has to be settled before build, and
the evaluation of the result. Everything else runs without asking.

## The three principles, and where each lands

1. **Work is instructed by purpose and intent.** Every numbered step in every `SKILL.md` and
   reference opens with one sentence saying what it is for, then what to do. A step whose purpose
   cannot be stated is not in `rn`. The implementer receives a task as its owner would state it —
   Purpose, Steps, Completion criteria — not a recipe (`references/task.md` step 1).
2. **Results are evaluated by a third party against essential viewpoints.**
   `references/evaluate.md` holds the whole of it: an evaluator that did not build the artifact,
   given only the Goal, the artifact, and a few fixed questions per kind — plan, design,
   deliverable, session — answering each with evidence. The verdict goes on the PR. `/rn:on` runs
   it on the plan before the user sees it; `task.md` runs it on every task's result.
3. **Judgment and execution use different models.** Planning happens in the conversation; the
   evaluator is dispatched with `model: opus`; the implementer with `model: sonnet`. The `Agent`
   tool's `model` parameter is the whole mechanism.

## What stays

- The five commands `/rn:on`, `/rn:dn`, `/rn:up`, `/rn:ty`, `/rn:gm`, user-invoked only.
- `steering.md` — its header (`Rn version:`, optional `Design:`) and sections (`Goal`,
  `Acceptance criteria`, `Assumptions`, `Rules`, `Tasks`, `State`) keep their 0.8.0 names, so an
  older file is readable without conversion.
- Three gates through `/rn:ty` and `/rn:gm`: the plan gate at the end of `on`, a "Design sign-off"
  task when planning places one, "Evaluation sign-off" as the last task. No per-task gate.
- One completion marker per task: `complete task #N` in the check-off commit alone; `/rn:up`
  reconciles with it.
- Suspend and resume through `State`; the session-status block at every stop; the draft PR whose
  body is a link to `steering.md`; the version check on every command and the migration it
  triggers.

## What goes, and why

0.8.0 put every task through a self-check, QA, Craft, Verification, and sometimes Design review,
each writing into `checks/{task}.md`, and put every session's design into a fixed question
template. [Issue #31](https://github.com/lovaizu/ccpm/issues/31) measured the result: 1,160 lines
of prompt, four fifths of a session directory as process residue, and checks that asked whether a
step ran rather than whether the output does its job. All of it goes — the check files, the expert
matrix, the iteration caps, the seven-element work-order, the design template, the GraphQL script
for PR feedback, the separate status-display file. One evaluation per artifact replaces the chain.

## What a session leaves

`steering.md` and the deliverable. Evaluations are PR comments. A design, when the session has one,
lives in the project's own documents and is pointed to by the `Design:` line.

## Models

Planning runs in the conversation on the model the user chose. `rn` fixes the two roles it
dispatches: implementer `sonnet`, evaluator `opus`. The split is what the principle asks for; the
parameter is where it is enforced.
