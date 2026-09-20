# rn — design notes

Not read at runtime — for whoever maintains `rn` and must judge whether a decision is still right
when requirements change.

## What rn is for

A goal outlives a single conversation: context runs out, `/clear` wipes the thread, a session pauses
overnight. `rn` keeps the goal in `steering.md`, tracked in git, so work can suspend and resume
across conversations without losing the thread. The user decides at exactly three points — the plan,
a design when one is needed, and the evaluation of the result — everything else runs without
stopping them.

## The three principles, and where each lands

1. **Every step states its purpose.** Every numbered step in every `SKILL.md` and reference opens
   with one bold sentence saying what it's for, then what to do. Lands in all five skills
   (`skills/on`, `dn`, `up`, `ty`, `gm`) and in `references/steering.md`, `task.md`, `evaluate.md`. A
   step with no purpose doesn't exist.
2. **Third-party evaluation against named questions.** `references/evaluate.md` holds who evaluates
   (an `Agent` subagent with no conversation history, launched without a `model` override, given
   only the Goal, the artifact, its kind, and the fixed questions for that kind — never the author's
   summary), the questions per kind, the output shape, and where the verdict goes: the session PR,
   via `gh pr comment`.
3. **Judgment and execution run on different models.** Planning happens in the conversation itself.
   `references/task.md` dispatches the implementer with `model: sonnet`; `evaluate.md` dispatches
   the evaluator with no override, so it runs on the conversation's own model — the one that
   planned.

## What stays

- Commands `/rn:on`, `/rn:dn`, `/rn:up`, `/rn:ty`, `/rn:gm`, with the same frontmatter contract
  (`name`, `description`, `disable-model-invocation: true`).
- `steering.md`'s shape and field names, so an 0.8.0 file is readable without conversion:
  `Rn version:`, optional `Design:`, `Goal` / `Acceptance criteria` / `Assumptions` / `Rules` /
  `Tasks` / `State`.
- The three gates — plan, design (when planning places a "Design sign-off" task), evaluation — taken
  via `/rn:ty` / `/rn:gm`, and no other per-task user gate.
- One completion marker per task (`complete task #N`), the draft PR opened by `on`, the version
  check and migration on `dn` / `up` / `ty` / `gm`, the session-status block, `/rn:gm`'s PR-feedback
  loop.

## What goes, and why

0.8.0 ran every deliverable through self-check, QA review, Craft review, Verification review, and —
for structural tasks — Design review, each writing to a `checks/{task-id}.md` ledger, before a task
could close. A session directory under `.rn/` ended up four-fifths process residue: check files
nobody but the mechanism read, per-session `design.md`s written to a fixed question contract
regardless of whether the work had a design decision to record, and an iteration-count cap tuned to
that same machinery. [Issue #31](https://github.com/lovaizu/ccpm/issues/31) named the result:
procedure that had stopped serving the purpose it was built for. This round replaces the whole
review chain with one third-party evaluation per task, run against a few named questions instead of
a fixed checklist.

## What a session leaves

Only `steering.md` and the deliverable. No `checks/`, no per-session `design.md` — the evaluation
that used to live in those files now lives as PR comments, addressable and readable in their
rendered form.

## Models

Planning runs in the conversation — no dispatch, no separate model. The implementer runs on
`sonnet` (`task.md`). The evaluator runs with no model override, so it always matches whatever model
is doing the planning in that conversation (`evaluate.md`).
