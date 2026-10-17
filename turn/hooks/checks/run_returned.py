"""The orchestrator ends only once its run has returned, so the calling AI always finds the result
where its call said."""

from typing import Any

import agents


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) != "up" or agents.running(event) is None:
        return []
    return ["the run has not returned; record your reading with `turn.py read` until it does"]
