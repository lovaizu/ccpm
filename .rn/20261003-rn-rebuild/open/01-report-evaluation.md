# Evaluation: the Acceptance criteria run on rn 0.9.0

Every scene in `rn/docs/verification.md` was run once on rn at 5fcc301–56bee40, with `writ` as
merged, on `lovaizu/rn-try` from `c3b5f8e`, one at a time, on 2026-10-06. `main` of the practice
repository kept `c3b5f8e` after every scene, and each run's pull request was closed with its branch.
The conductor read each run's transcript, commits, and session log against the scene's Passes when;
no first user read the records.

Conductor's view: every attractive criterion, A1 to A4, is close enough to put to real use.

## A1: the user gets what they really want, though they start from rough words

Good. Close enough for real use; as before.

- First scene (PR #53): after the languages, rn's first call asks why the user wants the goal, with
  four gains to choose from and their costs. The scene's start was set to after the languages,
  which the design asks first.
- Second scene (PR #54, 10 min): from `/rn:gm a user whose last name is null is shown "Ann null"`,
  the plan put up treats missing, `null`, `""`, and blank alike for nickname, first and last name,
  and asks only whether other forms exist.

## A2: the user is called only for decisions that are theirs

Good. Close enough for real use; reached for the first time (asked back in every run before).

- The user's aim for A2 (2026-10-06): rn asks the purpose and intent and proposes the means; one
  more question is no fault. The scene checks that (56bee40).
- First run (PR #58): asked what to do for these users, rn offered ways from a guessed intent, and
  the stand-in turned them down. Cause: the design had every question carry a recommended answer,
  so an intent question got a guessed one. The hearing was rewritten into intent questions, with no
  recommended answer and no way, and means questions, with ways only once the intent is written in
  the user's words; the plan's and the question's viewpoints now ask which gain the user did not say
  and which ways came before the intent. Closes #38.
- Two runs after the fix: each first call asked only what should be shown in place of the name; the
  stand-in's answer was written as A1 in its words; each second call asked a further intent (who
  needs to tell these users apart), offering no way.
- From #9: rn's progress messages tell the user how the work was checked ("最初の質問を第三者役の
  エージェントに試させたところ…", in PR #53's run).

  → to the user: whether this telling is acceptable

## A3: at a sign-off, the user decides from the proposal

Good. Close enough for real use; reached for the first time (not reached at b88afd0).

- Run (PR #55, 13 min): the stand-in reading only the proposal and the one reading the pull
  request both gave `/rn:ty`, on the same grounds. Every Good and More sits under its criterion ID
  with its place in `steering.md`, and each unchecked Assumption is a More.

## A4: work that takes days goes on from where it stopped

Good. Close enough for real use; first run on the minimal trials.

- Paused build task (PR #56, 1 min to the first edit): rn handed the pause note and the written
  test to its generator, which changed `src/` only; rn spoke Japanese.
- 0.8.0 session (PR #57, 9 min): the goal and its reason kept, `steering.md` in the current form,
  the old design kept in `open/01-notes-design.md`, and a new Plan sign-off as the design asks; it
  asked nothing the old record holds.

## Not part of this run

- The weight of writing documents (13 `writ` calls, 2 h 43 min in #9): rn calling `writ` again for
  each design point found while writing is to be proposed as a design change; writ's own runs are
  raised as #37.
