---
name: dn
description: "Set down the current aiya run — done for the day, not quitting. Dispatches a final Turn(record) sweep so the resume point is confirmed durable, then hands off to a manual /clear and /aiya:up. Has side effects (under a git backend commits and pushes) — run only on explicit /aiya:dn."
disable-model-invocation: true
---

# /aiya:dn — Set down

`dn` is down: done for the day — setting the work down, not quitting. It applies when a run is active and the human is stopping: context filling up, a break, end of day.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it.

2. **Enter at suspend** (conductor §9). Dispatch a final Turn(record) — the adapter matching the run's recorded backend — to sweep anything pending and make the final push; you never commit or push yourself. Its job is to confirm, not to persist: Turn(record) already commits at every wave settle, and the latest CCS, the approved phase documents, and the current Plan are the entire resume point, so nothing extra is written on stopping (under local there is nothing to push — the files on disk already are the record). Then report: progress confirmed durable; run `/clear` yourself (a plugin cannot clear your context), and resume in a fresh conversation with `/aiya:up`.
