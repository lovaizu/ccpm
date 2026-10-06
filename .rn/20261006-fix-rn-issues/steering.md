---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/50
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification-next.md
---

# Goal

Make rn give in real use what its design promises (`rn/docs/design.md`, A1-A4): the user starts from
rough words, is called only for what is theirs to decide, decides each sign-off from the proposal
alone, and picks the work up in any conversation. Today it does not: the design stage takes hours, a
proposal runs to 72 lines, the user is asked what rn could settle itself, its checks misfire on other
sessions, it cannot wait for its own agents, and it moves the user to a branch they did not ask for
(#39, #41, #43, #44, #45, #46). The user finds rn unusable as it is. Every open rn issue is closed by
building rn as it should be, never by patching the place each issue names.

# Acceptance criteria

rn's own criteria (`rn/docs/design.md`), word for word, with what this session adds after them.

## Attractive quality

- A1: The user gets what they really want, though they start from rough words.
- A2: The user is called only for decisions that are theirs, and does not watch over the work.
- A3: At a sign-off, the user decides from the proposal, without re-reading all the work.
- A4: Work that takes days goes on, the next day or in a fresh conversation, from where it stopped,
  without the user explaining anything again.
- A5: Other sessions work beside an rn session: its conductor can message them, and none of them is
  taken for its conductor or stopped by its checks (#43).

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
- M8: The conductor waits for every agent it starts before it goes on, the same way in every
  conversation, however Claude Code runs the agent (#44).
- M9: rn and writ keep `.claude/rules/plugin.md`: tests that run every line in CI, trials, and a
  CHANGELOG entry.

# Assumptions

- Fact, `gh issue view`: each of #39, #41, #43, #44, #45, #46 states, under "What it should be",
  what rn should do in its place.
- Fact, issue #46: what the user reads is settled once for `.claude/rules/plugin.md` and every plugin
  following it (rn and writ), not for rn alone.
- Fact, `gh pr list`: the open writ issues are taken by other sessions: #35 and #37 by PR #40
  (split pith out of writ, with rn on it), #36 by PR #42.
- Fact, the issues' own text: each issue falls short of a criterion above: #41 and #45 of A2 (the
  user is moved to a branch they did not ask for, and asked what rn could settle itself); #39 of A2
  (the user waits hours through rounds of writing in the design stage); #46 of A3 (a 72-line proposal
  the user cannot decide from); #43 of A5; #44 of M8.

- Fact, decided by the user: a question to the user is not checked by a first user before it is
  asked. The conductor makes it right before writing it, by looking up what can be settled; rn 0.9.0's
  check of every question by a first user (`rn/references/conduct.md`, "Asking the user") is a fault
  this session removes.

# Rules

- Judge every change from what rn should be for its user, and fix the cause wherever it shows; never
  patch only the line an issue names.
- Releasing rn and writ (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- `verification` goes back to `rn/docs/verification.md` once the design stage writes A5, M8 and M9
  into it. rn 0.9.0's check (`rn/hooks/checks/trace.py:22-35`) stops every tool call until the
  verification document covers every criterion, so a session that adds criteria to a product with a
  verification document of its own cannot get past its plan; until then the field names a file that
  does not exist. This is a fault of rn this session fixes.

- How this session and PR #40 meet, since both change how rn checks its work.
