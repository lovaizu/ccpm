---
name: dn
description: "Set down the current aiya run — done for the day, not quitting. Commits and pushes the run records so the resume point survives, then hands off to a manual /clear and /aiya:up. Has side effects (commits, pushes) — run only on explicit /aiya:dn."
disable-model-invocation: true
---

# /aiya:dn — Set down

`dn` is down: done for the day — setting the work down, not quitting. It applies when a run is active and the human is stopping: context filling up, a break, end of day.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it.

2. **Enter at suspend** (conductor §9). Commit and push the run records and any settled work — the latest CCS, the approved phase documents, and the current Plan are the entire resume point, so nothing extra is written on stopping. Then report: progress committed and pushed; run `/clear` yourself (a plugin cannot clear your context), and resume in a fresh conversation with `/aiya:up`.
