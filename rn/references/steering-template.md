# steering.md template

Read when creating a new `steering.md`.

## Steps

1. **Copy the template block below verbatim.** Keep every heading. Keep the blank lines between fields (`Purpose` / `Prerequisites` / `Steps` / `Completion criteria`).
2. **Leave placeholders in unpopulated sections.** `Tasks`, `Decisions`, `State` start empty; fill later.
3. **Fill each section per the rules below.**

---

```markdown
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

- state the objective achieved, not that an output was produced — write "the residue no longer keeps the tree dirty", not "DESIGN.md exists"
- the intended behavior is observably present — a third party can verify it actually occurs
- the representative failure modes are absent — name them
- objectively verifiable by a third party
- no vague terms ("appropriate", "correct")
- outcomes / end-state only — never actions, reviews, or gates (those belong in Steps)

# Decisions

## D-N: <what was decided>
- **Issue**: <the decision being made — understandable without background>
- **Conclusion**: <the decision>
- **Rationale**: <the judgment reasoning that supports the conclusion — no facts here>
- **Evidence**: <facts/numbers backing the rationale>
- **Sources**: <where each piece of evidence comes from>

# State

(written by /rn:dn, read and reset to this placeholder by /rn:up. `Status` is `paused` while a
session is suspended — the signal /rn:up and /rn:dn search for — and resets to `not suspended` here,
so only a genuinely suspended session reads `paused`.)

- **Status**: not suspended
- **Date**: YYYY-MM-DD
- **Last completed**: #N description
- **Next**: #N description
- **Notes**: context needed for resume
```

---

## Task definition requirements

| Requirement | Rule |
|---|---|
| Granularity | Purpose expressible in one sentence; split if it grows |
| Specificity | Not "implement" but "implement `methodName()` in `ClassName`" |
| Objectivity | Completion criteria judgeable by a third party |
| Prerequisites | List dependencies explicitly; enables parallel/sequential judgment |
| Criteria vs steps | Completion criteria state the objective met / behavior observed (the bar) — not that an artifact was produced; actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable. `task-workflow.md` Process selection (non-code vs code) is the source of *which* reviews apply — keep the two in sync |
| Flat tasks | Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates — each task's own verify steps (QA / expert / user review) are its gate |
