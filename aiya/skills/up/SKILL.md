---
name: up
description: Resume a set-down aiya run in a fresh conversation — back up, from where it left off. Re-reads the resume point (latest CCS, approved phase documents, current Plan) and the run's recorded backend, and continues the run. Has side effects (dispatches work; under a git backend commits and pushes) — run only on explicit /aiya:up.
disable-model-invocation: true
---

# /aiya:up — Resume

`up` is back up: continue from where the run left off. It applies in a fresh conversation after a `dn` → `/clear`. Resume is the ordinary between-wave handoff exercised across a conversation boundary — nothing special is restored because nothing special was saved.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it.

2. **Enter at resume** (conductor §9). Locate the run under `.aiya/` (the directory whose `ccs/` chain is most recent; if none exists, say so and point at `/aiya:on`), and reread its `backend` file so record dispatches go to the right adapter. Read exactly what the next wave would have read — the latest CCS, the approved phase documents, the current Plan — announce the position (e.g. "Resuming csv-export — Wave 2, #4, attempt 2"), and continue the dispatch round from there.
