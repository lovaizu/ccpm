---
name: on
description: Start a new aiya run from a rough purpose — power on, sit down, start. Creates the run directory, detects the platform backend, plans the Purpose phase, and stops at the first Planning Gate. Has side effects (writes files; under a git backend commits, pushes, and opens a PR/MR) — run only on explicit /aiya:on.
disable-model-invocation: true
---

# /aiya:on — Start

`on` is power on: sit down, start. It applies when no run is active — `on` happens once per unit of work; after that the cycle is `dn` → `/clear` → `up`. When a run is already active, say so and point at `/aiya:up` / `/aiya:dn`; start nothing. `$ARGUMENTS` is the rough purpose, and rough is fine.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it — it is the entire loop; this skill only names the entry point.

2. **Enter at the top.** Create the run directory (conductor §2) from a short slug of `$ARGUMENTS`, detect the platform backend and record it to the run's `backend` file, and dispatch the matching Turn(record) to open the review surface — the run branch, first push, and PR/MR under github or gitlab; under local the dispatch still happens — the adapter confirms the run directory and reports it as the surface (conductor §2). The surface exists before the first gate points at it. Then begin the Purpose phase: draft Plan(Purpose) (conductor §4), have it verified against the fixed viewpoints, dispatch the run's Turn(record) to carry the verified Plan onto the review surface (conductor §3; committed and pushed under github or gitlab, confirmed and reported under local — the gate must not point at a surface that lacks the Plan), and stop at the Purpose Planning Gate — a bounded console summary of how the purpose will be pinned down, answered with `/aiya:ty` or `/aiya:gm`.
