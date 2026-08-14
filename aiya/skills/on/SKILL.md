---
name: on
description: Start a new aiya run from a rough purpose — power on, sit down, start. Creates the run directory, plans the Purpose phase, and stops at the first Planning Gate. Has side effects (writes files, commits, pushes, opens a PR) — run only on explicit /aiya:on.
disable-model-invocation: true
---

# /aiya:on — Start

`on` is power on: sit down, start. It applies when no run is active — `on` happens once per unit of work; after that the cycle is `dn` → `/clear` → `up`. `$ARGUMENTS` is the rough purpose, and rough is fine.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it — it is the entire loop; this skill only names the entry point.

2. **Enter at the top.** Create the run directory (conductor §2) from a short slug of `$ARGUMENTS`, then begin the Purpose phase: draft Plan(Purpose) (conductor §4), have it verified against the fixed viewpoints, and stop at the Purpose Planning Gate — a bounded console summary of how the purpose will be pinned down, answered with `/aiya:ty` or `/aiya:gm`.
