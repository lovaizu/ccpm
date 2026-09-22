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
   (`references/evaluate.md`). Each verdict is committed as a file in the session's own directory,
   so the user reads it rendered on the PR beside the diff it judged.
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
- **A session leaves `steering.md` and the deliverable.** Every round's verdict is a file under
  the session's `evaluations/`, committed as the evaluator wrote it, and the directory goes when
  "Evaluation sign-off" is approved. Committed rather than posted: a round then closes on something
  the repository holds and `git` alone can find on a resume, instead of on a comment that has to be
  fetched back to be trusted. A design lives in the project's own documents, pointed to by the
  `design` field. `rn` writes no process file of its own.
- **The evaluator is handed the contract, not a briefing.** It receives `steering.md` whole, the
  artifact and its kind's questions — never the builder's account, an exclusion list or an earlier
  verdict; a fresh agent every round. A scope decision that is not in `steering.md` is not a
  decision, so the evaluator and the user judge against the same record.
- **The user's word has two channels of equal weight.** `/rn:ty` / `/rn:gm` in the conversation
  and review threads on the session PR; a plan either one changes is judged again before work
  continues.
- **One completion marker per task, one mark in the file.** `complete task #N` appears in the
  check-off commit alone and the task's heading gains ` ✅`; `/rn:up` reconciles from the commit.
  Pushed history is never rewritten.
- **The session's fixed facts are frontmatter; its running record is prose.** `rn`, `issue`,
  `pr`, `design` and `status` sit in YAML at the top, which GitHub renders as a table and every
  command reads without parsing prose; `State` keeps what only a sentence can say — what was last
  done, what is next, what is pending.
- **`status` is a pair, and finished is not a status.** `running` or `paused`, nothing else: the
  field exists to signal a suspend, and `/rn:dn` sets `paused_at` beside it. That a session is
  finished is read from its last task, "Evaluation sign-off", carrying ` ✅` — a fact the record
  already holds, so no flag can contradict it.
- **A session is named after what it produces.** The directory slug comes from the Goal, never
  from a ticket id or a branch carrying one — those point at the work instead of naming it, and
  the issue has its own field.
- **Names are quoted, not summarized.** The status block carries the Goal's first sentence and the
  task names as `steering.md` writes them, so the user meets the same words in every conversation.
- **An older session is rebuilt, not patched.** A version mismatch rewrites `steering.md` from the
  current template with the old file as input, carrying every fact, so the session goes on at the
  current bar (`references/steering.md`, Migration).
- **Documents hold current intent only.** `steering.md`, a design, and this file record what is
  decided and why; history lives in git and on the PR.

## Shape

Five user-invoked commands — `/rn:on`, `/rn:dn`, `/rn:up`, `/rn:ty`, `/rn:gm` — and four
references: `conductor.md` (the role every command runs under), `steering.md` (the file, and the
operations every command shares — entering a session, judging the plan, checking off, the status
block, migration), `task.md` (the loop), `evaluate.md` (the questions). The session-status block
opens every stop.
