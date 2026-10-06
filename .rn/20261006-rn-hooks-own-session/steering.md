---
rn: 0.9.0
pr: https://github.com/lovaizu/ccpm/pull/47
status: running
artifact-language: English
conversation-language: Japanese
readme: rn/README.md
design: rn/docs/design.md
verification: rn/docs/verification.md
---

# Goal

Fix #43 and #44: rn's checks know which session runs rn and which agents it started, so its
conductor can answer other sessions and no other session is taken for the conductor; and the
conductor waits for every agent it starts before it goes on, however Claude Code runs the agent, the
same way in every conversation. Also fix, as decided by the user, the same cause met in this session:
rn's checks take the criteria named in the documents for this session's own, so a second session on
the same documents is stopped before it has any criteria, and the Stop check sends the conductor
back on every end of its turn while it waits for the user.

# Acceptance criteria

## Attractive quality

## Must-be quality

# Assumptions

- Fact, read in `rn/hooks/record.py:69` (`find`): every check takes any conversation on a branch
  with a running `.rn/` session for its conductor; none looks at the hook input's `session_id`.
- Fact, read in `rn/hooks/checks/foreground_agents.py:12`: every `SendMessage` from the main
  conversation is stopped, whoever it is addressed to.
- Fact, seen in this session on Claude Code 2.1.291: the `Agent` tool has no `run_in_background`
  input, and its description says subagents run in the background and notify on completion.
- Fact, from the hooks reference (code.claude.com/docs/en/hooks): the Stop hook's input carries
  `background_tasks`, each with `type` (such as `subagent`), `status` and `agent_type`, so a Stop
  check can tell that the conductor's agents are still running.
- Fact, read in `rn/hooks/checks/turn_end.py:12`: the Stop check sends the conductor on whenever it
  is not at a stop or a question, agents running or not.
- Fact, met in this session: `rn/docs/verification.md` names criteria A1–A4 and M1–M7 of the rn
  rebuild session; `rn/hooks/checks/trace.py:27` reports each as undefined in this session's
  `steering.md` on every edit, stops the call to a first user, and `rn/hooks/stop.py:22` blocks every
  end of the turn on it, `stop_hook_active` or not, so the conductor was sent back over and over
  while it waited for the user's answer.
- Fact, decided by the user: until this is fixed, questions go to the user without a first user
  taking them up first.

# Rules

- Follow `.claude/rules/plugin.md` and `.claude/rules/final-check.md`.

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off

# Not yet specified
