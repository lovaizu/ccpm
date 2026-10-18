"""Each role's reply fills its form, and is kept in the run for the step that takes it, so the
orchestrator and the script read every reply the same way on every run and no AI copies one."""

from typing import Any

import agents
import forms
import run

FORMS = {
    "generator": forms.CLAIM,
    "first-user": forms.GOOD,
    "evaluator": forms.GOOD,
    "learner": forms.LEARNT,
}


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    if role not in FORMS:
        return []
    result = agents.result(event)
    kept = run.running(result) if result else None
    if result is None or kept is None:
        return []
    reply = str(event.get("last_assistant_message", ""))
    # Not mutated: of the roles that reply, the learner's name sorts last.
    judged = kept["learning"] if role == "learner" else kept["items"]  # pragma: no mutate
    said = forms.check(reply, judged, kept["work"], FORMS[role], sources=run.sources(kept))
    if said:
        return ["reply with your form alone, filled:"] + said
    kept["next"].update(
        reply=forms.parse(reply, FORMS[role]), record=event["agent_transcript_path"]
    )
    run.write(result, {"running": kept})
    return []
