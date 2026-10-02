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
  repository.
- With the real `writ` merged (writ PR #15), the integration check passes, and
  `claude plugin validate --strict` passes for `rn` and the marketplace.

# Rules

- After every change to the prompts, an evaluator that did not write them reads all of them
  against `writ`'s essential viewpoints for prompts (`writ/references/essentials/prompt.md` on
  branch `worktree-writ`), and the change is not done until its Mores are settled. `writ` is still
  being built, so `rn`'s design document does not name it for this.
- A More is fixed from what the work should be for its purpose, and design changes reach both the
  design document and the prompts.

# Tasks

### [ ] #1: Settle the prompt-viewpoint evaluation of 2026-10-02
### [ ] #2: Update CHANGELOG for what changed for the user
### [ ] #3: Run the trials again, including pause and resume, /rn:gm, and the 0.8.0 migration
### [ ] #4: Integration check with the real writ after writ PR #15 merges
### [ ] #5: Close the practice repository's PRs #18, #20, #21, #22 and delete their branches
