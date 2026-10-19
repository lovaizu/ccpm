"""Each role's reply fills its form, and is kept in the run for the step that takes it, so the
orchestrator and the script read every reply the same way on every run and no AI copies one. The
agent of a role kept started is kept too, so what comes next is sent to it by message."""

from typing import Any

import agents
import forms
import run

FORMS = {
    "generator": forms.CLAIM,
    "first-user": forms.FIRST_READING,
    "evaluator": forms.GOOD,
    "learner": forms.LEARNT,
}


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    reply = agents.reply(event)
    if role not in FORMS or reply is None:
        return []
    result = agents.result(event)
    kept = run.running(result) if result else None
    # A reply no step waits on, such as one after a message the run did not send, is no step's.
    if result is None or kept is None or kept["next"]["agent"] != f"turn:{role}":
        return []
    # Every role but the learner judges every item; the learner judges none, as its form takes no
    # items, and quotes the records it was shown.
    said = forms.check(
        reply,
        kept["items"],
        kept["work"],
        FORMS[role],
        records=tuple(run.learnt_from(kept)),
        each=run.each(kept),
    )
    if said:
        return ["reply with your form alone, filled:"] + said
    kept["next"].update(reply=forms.parse(reply, FORMS[role]), record=agents.transcript(event))
    if kept["next"]["agent"] in run.KEPT:
        kept.setdefault("started", {})[kept["next"]["agent"]] = event["agent_id"]
    run.write(result, {"running": kept})
    return []
