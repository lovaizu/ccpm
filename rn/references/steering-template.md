# steering.md template

Read when creating a new `steering.md`.

## Steps

1. **Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields (`Purpose` / `Prerequisites` / `Steps` / `Completion criteria`).
2. **Leave placeholders in unpopulated sections.** `Tasks`, `State` start empty; fill later.
3. **Fill each section per the rules below.**

## Doc-division rule

Allocate content by kind, so steering stays a lean forward contract:

- **Requirements & acceptance criteria → `steering.md`** — the goal, the bar it is judged against, and the remaining tasks.
- **Structure & decisions (how the parts fit, and why) → `design.md`** — the whole-structure design; rationale lives only here, at the decision level.
- **User-facing UX → `README`** — what a user sees and does.

A decision lands in a task, in `design.md`, or in a rule. Deliberation and history live in git + the PR — never in steering.

The top `Design:` line points to the session's `design.md`. A session with no design omits this line entirely (no file, no pointer) — copy the rest of the block as-is.

---

```markdown
Design: <path to the session's design.md — omit this whole line if the session has no design>

# Goal

<why this is being done and what the user wants to change — the full intent, no added scope>

# Acceptance criteria

- <the states / conditions by which the goal is judged achieved>
- <two axes: goal alignment + quality>
- <write these exhaustively, never sample — the complete set is what defines scope (in / out)>

# Assumptions

- <things taken to be true in pursuit of the goal — if one proves false, the plan changes>
- <distinguish facts from assumptions — state explicitly if unverified>

# Rules

- commit and push every change; one completion marker per task
- <task-specific conventions>

# Tasks

### #1: <task name>

**Purpose**: what to achieve, 1-2 sentences

**Prerequisites**: tasks that must be completed first (or "none")

**Steps**:

- [ ] specific step 1
- [ ] specific step 2
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA expert review (subagent)
- [ ] (code changes only) language expert review (subagent)
- [ ] (code changes only) software-engineering expert review (subagent)
- [ ] user review

**Completion criteria**:

- write each criterion so a third party can answer two questions about it, each with grounds:
  - ① is the objective achieved? — the objective met, not that an output was produced (write "the residue no longer keeps the tree dirty", not "DESIGN.md exists"); includes the intended behavior being observably present
  - ② are new problems absent? — name the representative failure modes and require their absence
- objectively verifiable by a third party; no vague terms ("appropriate", "correct")
- state the end-state, never actions/reviews/gates (those belong in Steps); the grounds are recorded at verification (checks/{task-id}.md Evidence columns), not written into the criterion text

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: bounded forward pointer — branch/PR, next concrete action, open blockers, user-deferred paths, open questions / pending decisions not yet captured in `design.md`; not a re-narration of the session (that lives in `git log`)
```

---

## Task definition requirements

| Requirement | Rule |
|---|---|
| Granularity | Purpose expressible in one sentence; split if it grows |
| Specificity | Not "implement" but "implement `methodName()` in `ClassName`" |
| Objectivity | Completion criteria judgeable by a third party |
| Prerequisites | List dependencies explicitly; enables parallel/sequential judgment |
| Criteria vs steps | Completion criteria are written so a third party can answer, with grounds, ① is the objective achieved and ② are new problems absent (the bar) — not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable. `task-workflow.md` Process selection (non-code vs code) is the source of *which* reviews apply — keep the two in sync |
| Flat tasks | Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates — each task's own verify steps (QA / expert / user review) are its gate |
