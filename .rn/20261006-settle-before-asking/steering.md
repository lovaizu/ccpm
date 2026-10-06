---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/49
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

`rn` puts a point to the user only when the goal, the request, the conversation, the repository, the
official documentation, and best practice leave more than one answer that gives the user something
different; what they settle goes into the plan as a Fact naming where it was settled, with no
question and no first user, so the user sees at the Plan sign-off what was decided for them and on
what ground. The user wants this because their time should go only to the sign-offs and to what only
they can decide: working out the plan for #36, `rn` wrote a question the issue and
`writ/docs/design.md:80` already answered, had a first user check it, and dropped it only after the
user asked why it could not decide the point itself (issue #45).

# Acceptance criteria

`rn`'s own criteria, as `rn/docs/design.md` words them, since this changes a plugin its users know
and the verification document checks it by them. This change aims at A2, for the point the request
and the repository already settle; the others are kept as they work today.

## Attractive quality

- A1: The user gets what they really want, though they start from rough words.
- A2: The user is called only for decisions that are theirs, and does not watch over the work.
- A3: At a sign-off, the user decides from the proposal, without re-reading all the work.
- A4: Work that takes days goes on, the next day or in a fresh conversation, from where it stopped,
  without the user explaining anything again.

## Must-be quality

- M1: The user's default branch changes only when they merge.
- M2: Every decision is committed and pushed as it is made, with a line that says what was decided
  and what comes next.
- M3: Every settled item is whole in the commit that settles it, so the record shows why things came
  out as they did.
- M4: `steering.md`, the names of the files in `open/`, and the verification document keep the form
  every command reads them by, and every ID they refer to exists.
- M5: A sign-off is passed only by the user's approval, and is put to the user with nothing
  unsettled behind it.
- M6: What the first user reports is what the user would get, since it knows nothing of how the work
  was made.
- M7: `rn` installs from the marketplace and passes its strict validation.

# Assumptions

- Fact, read in `.claude/rules/plugin.md` (Validation) and `rn/hooks/`: a change to a plugin its
  users already use is judged by whether it improves what it set out to without making worse what
  worked before, and `rn`'s checks hold the session's criterion IDs to those its verification
  document uses; so this session is judged by `rn`'s own criteria.
- Fact, read in `rn/references/essentials/conductor.md:69-70`: the sources that can settle a point
  are the goal, the conversation, the repository, the official documentation, and best practice.
- Fact, read in `rn/references/conduct.md`: line 58 reads as asking an intent question every time,
  with no word for a request and repository that already give the why and leave one outcome; line 70
  ("Look facts up, never ask them") covers facts only.
- Fact, read in `rn/references/conduct.md:225-231` and `rn/references/essentials/conductor.md:69`: the
  only guard against a needless question, the Question viewpoint asking what the goal or the
  repository could have settled, runs after the question is written and a first user is started.
- Fact, read in `rn/docs/verification.md:61`: the A1 scene starts from rough words with no reason
  given and passes when `rn` asks why; that question is the user's and stays, so A1 must not get
  worse.

# Rules

- Hold the change by how the conductor's steps are built, not by a further sentence asking it to
  judge better, as issue #45 asks: for example a question item names what was looked at and why it
  leaves the point open.
- Follow `.claude/rules/plugin.md`: user-facing changes go under `## [Unreleased]` in
  `rn/CHANGELOG.md` and `version` is not bumped; tests in `dev/rn/tests/`, trials in
  `dev/rn/trials/`.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- Which steps of `conduct.md`, which viewpoints, and which hook checks change.
- The A2 scene and trial that show a settled point going into the plan unasked, and which forms a
  point takes are covered: from an issue, rough words, `/rn:gm` feedback, or an older record; an
  intent, a means, or a fact point.
