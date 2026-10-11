"""Never hand the first user the acceptance criteria: knowing them, it would use the deliverable the way
they describe, and the receiver's stumbles would not show."""


def check(data, t):
    given = data.get("tool_input") or {}
    if data.get("tool_name") != "Agent" or given.get("subagent_type") != "turn:first-user":
        return []
    prompt = given.get("prompt", "")
    if any(a in prompt for a in t["acceptance"]):
        return ["the first user's prompt holds the acceptance criteria; hand it only the copy, the "
                "deliverable's place, the receiver, the use and its report file"]
    return []
