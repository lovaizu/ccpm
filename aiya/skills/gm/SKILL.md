---
name: gm
description: Send back the pending aiya checkpoint — gimme a change; the counterpart to /aiya:ty. With an argument, /aiya:gm <one line> is the feedback under every backend; with no argument, it picks up the PR/MR's review comments — a form that exists only under a PR/MR backend. Has side effects (reworks artifacts; under a git backend commits and pushes) — run only on explicit /aiya:gm.
disable-model-invocation: true
---

# /aiya:gm — Send back

`gm` is gimme a change: not yet, change this. It applies when the Conductor is stopped and waiting at one of the six gates. The feedback is `$ARGUMENTS` when present — that form works under every backend. With no argument, the PR/MR's review comments are the feedback, fetched to a file by a Turn(record) — a form that exists only where a PR/MR exists (github, gitlab); under the local backend, feedback always rides the argument.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it.

2. **Enter at the pending gate with a send-back verdict** (conductor §3, §8). Rework the artifact through the same pipeline — Turns make, Turns verify; you never draft — and return to the gate. Re-approval mints a new version, and Verdicts measured against the old version are invalidated and re-verified per conductor §3. Every piece of feedback is acted on; none is dropped.
