---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/48
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

When the current branch is not the default branch and has no commits of its own, `/rn:on` works on
it as it is, brought up to the latest default branch when it is behind, and pushes it under the same
name; it makes a new branch only from the default branch itself, or when the current branch already
holds other work. The user starts a worktree for the work and expects the session there, so a second
name for the same work leaves the worktree and its branch apart and costs turns asking why and
undoing it (#41).

# Acceptance criteria

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

- Fact, from `rn/docs/design.md` "Acceptance criteria": the deliverable is `rn` changed, so it is
  judged by `rn`'s own criteria, copied above with their IDs, which `rn/docs/verification.md` refers
  to.
- Fact, from #41 "Why it matters": this goal serves A2, since the user spends turns asking why the
  branch changed and undoing it; it adds no criterion of its own.
- Fact, from `rn/skills/on/SKILL.md:20`: today `/rn:on` makes a new branch on every form of the
  current branch: the default branch, a branch with no commits of its own at or behind the latest
  default branch, and a branch with commits of its own.
- Assumption: a branch with no commits of its own that is behind the latest
  default branch is kept too, since moving it up loses nothing and a new name leaves the worktree
  apart all the same; #41's words name only one at the latest default branch, the case it was seen
  in.

# Rules

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- What the deliverable needs, settled in the design.
