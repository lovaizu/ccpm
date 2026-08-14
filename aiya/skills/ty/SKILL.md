---
name: ty
description: Approve the pending aiya checkpoint — thank you, good, go ahead. Signs off whatever the Conductor last stopped on (a Planning Gate, G1, G2, or G3) and the run advances with no revision. Has side effects (continues the run) — run only on explicit /aiya:ty.
disable-model-invocation: true
---

# /aiya:ty — Approve

`ty` is thank you: good, go ahead. It applies when the Conductor is stopped and waiting at one of the six gates. An escalation (a Step that failed three times) is not approved with `ty` — it is adjudicated by answering the question it carries.

## Steps

1. **Load the Conductor's procedure.** Invoke the `aiya:conductor` skill and follow it.

2. **Enter at the pending gate** (conductor §3, §8). Record the approval — an Output Gate approval mints the document's version (G1/G2/G3) — and advance: a Planning Gate opens the phase's dispatch round; G1 and G2 fix the next phase's yardstick; G3 completes the run. If nothing is pending, say so and do nothing else.
