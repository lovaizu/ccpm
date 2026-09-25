---
name: up
description: Resume an rn session in a fresh conversation — find its steering.md, bring an older session current, act on the decision recorded before the break, and run the session to its next decision. Has side effects (commits, pushes, runs tasks) — run only on explicit /rn:up.
disable-model-invocation: true
---

# /rn:up — Resume a session

Picks the session up where `State` and git say it stands and runs it on, so nothing is redone and
nothing the user decided is lost. Runs under the conductor's role:
`${CLAUDE_PLUGIN_ROOT}/references/conductor.md`.

## Steps

1. **Start from a known tree.** Find the session as in step 2, read-only. Clean, apart from paths
   its `Notes` say the user kept → go on. Otherwise propose a `wip:` commit or discarding the
   changes, and wait for the answer.
2. **Enter the session** as in Entering a session in
   `${CLAUDE_PLUGIN_ROOT}/references/steering.md`, and bring it current as in Migration there when
   its `Rn version:` differs from `version` in `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.
3. **Read `State`, then set it back to running.** Carry `Next`, `Feedback` word for word and
   `Notes` into what follows; replace `State` with `- **Status**: running`, commit
   `chore: resume — {slug}`, and push, so only a stopped session reads `paused`.
4. **Check the record against the repository.** A note or Assumption the commits have since
   overtaken is corrected in `steering.md`; a blocker in `Notes` is looked into for a way through
   before any task is dropped.
5. **Go on.** `Feedback` other than none → Revising on feedback in
   `${CLAUDE_PLUGIN_ROOT}/references/conductor.md`. Otherwise → Running the session to its next
   decision there, from `Next`.
