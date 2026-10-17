"""The generator's reply fills its form, the lines it meant to give each item or the question the
item waits on, so the orchestrator reads its claim the same way on every run."""

from typing import Any

import agents
import forms


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) != "generator":
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    said = forms.check(str(event.get("last_assistant_message", "")), kept, forms.CLAIM)
    if not said:
        return []
    return ["reply with your form alone, filled:"] + said
