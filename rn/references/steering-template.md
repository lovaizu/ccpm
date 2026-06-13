# steering.md template

Read this file when creating a new `steering.md`. Copy the structure below verbatim, then
fill the sections. Keep every heading; leave a section's placeholder in place if it is not yet
populated (`Tasks`, `Decisions`, `State` start empty and are filled later). **Keep the blank lines
between fields** (`Purpose` / `Prerequisites` / `Steps` / `Completion criteria`) — without them
Markdown collapses the fields onto one line.

---

```markdown
# Goal

<a clear, faithful restatement of what the user wants to achieve — full intent, no added scope>

## Verification

- <how to verify the goal is achieved>
- <two axes: goal alignment + quality>

# Assumptions

- <distinguish facts from assumptions — state explicitly if unverified>
- <define complete scope, never sample>

# Rules

- 1 task = 1 commit
- <task-specific conventions>

# Tasks

### #1: <task name>

**Purpose**: what to achieve, 1-2 sentences

**Prerequisites**: tasks that must be completed first (or "none")

**Steps**:

- [ ] specific step 1
- [ ] specific step 2
- [ ] self-check (OK/NG per completion criterion, record in checks/{task-id}.md)
- [ ] QA engineer review (subagent)
- [ ] (code changes only) language expert review (subagent)
- [ ] (code changes only) software engineer review (subagent)
- [ ] user review

**Completion criteria**:

- objectively verifiable by a third party
- no vague terms ("appropriate", "correct")
- outcomes / end-state only — never actions, reviews, or gates (those belong in Steps)

# Decisions

## D-N: <what was decided>
- **Conclusion**: <the decision>
- **Rationale**: <why>
- **Evidence**: <facts/numbers backing the rationale>

# State

(written by /rn:bb, read and reset to this placeholder by /rn:hi)

- **Status**: paused
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
| Criteria vs steps | Completion criteria state outcomes/end-state only (the bar); actions, reviews, and gates go in Steps as `- [ ]` so their status stays trackable |
| Flat tasks | Number tasks `#1`, `#2`, …; do not group into phases or add phase-level gates — each task's own verify steps (QA / expert / user review) are its gate |
