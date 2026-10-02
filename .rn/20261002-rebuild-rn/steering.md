---
pr: https://github.com/lovaizu/ccpm/pull/33
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
---

# Goal

`rn` is rebuilt from zero (#31), so the user gets the goal they really want while spending their
time only on the three sign-offs and on what only they can decide.

# Goal achieved when

- Every benefit in `rn/README.md` passes its scene in `rn/docs/design.md`, run on the practice
  repository with the real `writ`.
- `claude plugin validate --strict` passes for `rn` and the marketplace.

# Rules

- After every change to the prompts, an evaluator that did not write them reads all of them
  against `writ`'s essential viewpoints for prompts (`writ/references/essentials/prompt.md` on
  branch `worktree-writ`), and the change is not done until its Mores are settled. `writ` is still
  being built, so `rn`'s design document does not name it for this.
- A More is fixed from what the work should be for its purpose, and design changes reach both the
  design document and the prompts.
- The README and design document are changed and approved on the PR first; the prompts and hooks
  are built from them only after.
- Points are put to the user one at a time, in plain Japanese, with grounds and one recommendation.

# Agreed on 2026-10-02/03, to go into the README and design document

1. Kano model, explicit. The plan's criteria section is named Acceptance criteria (for the goal),
   and a task's Completion criteria (for its purpose); each has subsections Attractive quality and
   Must-be quality. The same split carries through to verification, tasks, and the deliverable's
   evaluation. Tasks first raise attractive quality until the goal is nearly achieved, then finish
   must-be quality.
2. Verification is split from the design into its own document (e.g. `docs/verification.md`):
   for each acceptance criterion, the scene where it is checked and what passes, in the same
   attractive → must-be order. The Design sign-off approves design and verification together.
3. Traceability: each acceptance criterion has an ID (A1, A2… attractive; M1, M2… must-be). Design
   features, verification checks, tasks, and the deliverable's evaluation refer to criteria by ID.
4. Hooks check rn's rules mechanically, at three points: right after a file is written
   (PostToolUse), at the end of each stage before its evaluation, and again before every commit.
   What they check:
   1. steering.md form: front matter, headings, task headings `### [ ] #N: name`, unique IDs.
   2. `open/` file names `{NN}-{kind}-{about}.md`, kind evaluation | feedback | notes.
   3. Traceability: every referenced ID exists; every criterion has a verification check, and a
      task once tasks are planned.
   4. Every conductor commit ends with a decision line `● … ── … → …`.
   5. A settled `open/` item's text is whole in the commit message.
   6. A stop commit: `open/` holds only design points waiting for writ, the latest default branch is
      merged, and the line ends `waiting for #N …`.
   7. A sign-off is marked `[x]`, and `status: finished` set, only in an approval commit.
   8. Every commit is pushed.
   9. Only the conductor uses git: generator, evaluator, and writ agents are stopped from commit/push.
   10. An evaluator writes only its own evaluation file.
   11. An evaluator does not read the maker's account (commit messages, notes, earlier evaluations).
   Before building 9–11: confirm a PreToolUse hook can tell which subagent made the call.
   Content (whether it serves the purpose, the language, feedback kept whole) stays with the
   evaluator and conductor.
5. Hearing: adopt the know-how of `grilling` (mattpocock/skills, MIT, d81f3a1, 2026-09-29) — a tree
   of decisions, ask what its prerequisites allow with a recommended answer, facts are looked up not
   asked, done when nothing is silently assumed — and add rn's own part: find what the user really
   wants from the purpose behind their words and the ideal it calls for, and record each point as
   agreed. Know-how only, not a dependency: neither fits rn as it is.
6. Task creation: adopt the know-how of `wayfinder` (same source and version) — destination first,
   decisions resolved one at a time, what is not yet clear kept visible as not yet specified.
7. Name the sources where they explain a decision: grilling, wayfinder (with version), Kano model,
   generator/evaluator split, decision records (ways not chosen). Verify each attribution before
   writing it. Watch upstream changes of mattpocock/skills and decide whether to take them in.
8. Viewpoints ask about the state of what the receiver gets, not what the maker did (writ's
   essentials.md, 31dba86). Rewrite rn's viewpoint files to it with the Kano and naming changes,
   e.g. "Is each fact checked?" and "Has the work shown nothing…".
9. `writ` stays a dependency (same marketplace, updated together).
10. This work itself runs as an rn 0.8.0 session, so its state and plan are visible and it resumes.

# Tasks

### [ ] #1: Start an rn 0.8.0 session for this work from this file, then remove this file
### [ ] #2: README and design document carry points 1–9, approved on PR #33
### [ ] #3: Prompts, viewpoint files, and hooks built from the approved design
### [ ] #4: CHANGELOG updated for what changed for the user
### [ ] #5: Trials run again, including pause and resume, /rn:gm, and the 0.8.0 migration
### [ ] #6: Integration check with the real writ after writ PR #15 merges
### [ ] #7: Close the practice repository's PRs #18, #20, #21, #22 and delete their branches
