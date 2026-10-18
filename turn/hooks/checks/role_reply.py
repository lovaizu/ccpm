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
# The items each role judges, and the records its quotes and commands are found in: the learner
# judges the items not waiting on a question and quotes the records it was shown; every other role
# judges every item, and its commands are found in its own record.
JUDGES = {
    "learner": lambda kept, own: (kept["learning"], tuple(run.learnt_from(kept))),
}


def everything(kept: dict[str, Any], own: str) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    return kept["items"], (own,)


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    if role not in FORMS:
        return []
    result = agents.result(event)
    kept = run.running(result) if result else None
    if result is None or kept is None:
        return []
    reply = str(event.get("last_assistant_message", ""))
    judged, kept_records = JUDGES.get(str(role), everything)(kept, event["agent_transcript_path"])
    said = forms.check(
        reply,
        judged,
        kept["work"],
        FORMS[role],
        sources=run.sources(kept),
        records=kept_records,
    )
    if said:
        return ["reply with your form alone, filled:"] + said
    kept["next"].update(
        reply=forms.parse(reply, FORMS[role]), record=event["agent_transcript_path"]
    )
    run.write(result, {"running": kept})
    return []
