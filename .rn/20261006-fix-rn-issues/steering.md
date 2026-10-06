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
- Fact, `git diff --stat 5adb39a 3a80a90 -- rn`: rn 0.9.0, rebuilt to be simpler, grew from 0.8:
  +2858 / -1490 lines; 882 lines of hooks in 14 checks were added, and `conduct.md` alone is 285
  lines.
- Fact, read in `rn/docs/design.md` and `rn/references/conduct.md`: a first user is started for the
  plan, the design, each task, the deliverable, each question, each proposal, and again for each fix
  of an attractive More; nothing bounds how many runs a session makes, and every report feeds the
  proposal, whose template asks for the goal, every criterion, and every final Good and More.
- Fact, read in `rn/docs/design.md:86` and the hooks: rn's own policy is to improve by sharpening the
  viewpoints, not by adding steps, yet each fault met while building it became a step or a hook
  (the question check, checks 3, 7, 13, 14).
- Fact, read in `rn/docs/verification.md` and `rn/docs/design.md:176-187`: rn is verified scene by
  scene, each from the state just before one moment; no check measures a whole session, its time,
  or what the user reads, so #39's 2 h 43 min was seen in #33 and released.
- Fact, official docs (sub-agents) and seen in this session: a background agent's result reaches the
  main conversation as a notification that starts a later turn by itself, with nothing from the user.
- Fact, official docs (hooks): every hook input has `session_id`; a hook fired inside a subagent adds
  `agent_id` and `agent_type`; `SubagentStart` and `SubagentStop` exist; `UserPromptSubmit` fires on
  every user message with `session_id`.
- Fact, tried with `claude -p` 2.1.291 and a logging PreToolUse hook: a hook fired for a subagent's
  tool call carries the main conversation's `session_id`, with its own `agent_id` and `agent_type`.
- Fact, decided by the user: this session and PR #40 go on side by side; where they meet, the
  conflict is settled when the second of them is merged.

# Rules

- Judge every change from what rn should be for its user, and fix the cause wherever it shows; never
  patch only the line an issue names.
- Where rn 0.9.0's own procedure has a first user check what the conductor writes to the user (a
  question, the plan, a proposal), this session leaves it out: that is the fault it fixes, and the
  user decided so for questions.
- Releasing rn and writ (version bump, tags, GitHub Release) waits for an explicit release
  instruction, as `.claude/rules/plugin.md` says.

# Tasks

### [x] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified

- `verification` goes back to `rn/docs/verification.md` once the design stage writes A5, M8 and M9
  into it. rn 0.9.0's check (`rn/hooks/checks/trace.py:22-35`) stops every tool call until the
  verification document covers every criterion, so a session that adds criteria to a product with a
  verification document of its own cannot get past its plan; until then the field names a file that
  does not exist. This is a fault of rn this session fixes.

- The design, from the three causes the issues come from:
  1. Checks by a first user run everywhere (#39, #45): the viewpoints stay the form every maker
     writes to and every check uses, the conductor included; a first user uses only what its maker
     cannot see without use; writ is called once per document, with every design point settled.
  2. What the user reads grows with the work checked (#46): a proposal and every check's short
     result hold only the conductor's view, the points the user decides, and the next move; fixed in
     `.claude/rules/plugin.md`, rn and writ.
  3. The hooks know neither the session nor the stage (#41, #43, #44, the coverage check above): they
     act only in the session that runs rn and on the agents it started, check the verification
     document once the design writes it; the conductor waits for its agents one way; /rn:on keeps
     the worktree's branch.
- The design starts from an audit of rn 0.9.0 as a whole, its design, prompts and hooks, against
  what rn should be, and from why 0.9.0, rebuilt to be simpler, came out worse in use; the user asked
  for both when approving the plan.
- How it is shown to work: one rn session run end to end on the practice repository, compared with
  rn 0.9.0's run on time to the Design sign-off, the proposal's length, and what the user was asked.
