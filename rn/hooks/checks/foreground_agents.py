"""Check 12: the conductor starts no agent in the background, nor continues one by message, which
runs it in the background, since an agent left running reports to a turn that has already ended."""


def check(data):
    if data.get("agent_type"):
        return []
    tool = data.get("tool_name", "")
    if tool == "Agent" and (data.get("tool_input") or {}).get("run_in_background"):
        return ["start the agent in the foreground and wait for what it returns; your turn ends "
                "only when you stop for the user or ask them a question"]
    if tool == "SendMessage":
        return ["an agent continued by message runs in the background; start a fresh agent in the "
                "foreground with the paths of what the last one left, and wait for what it returns"]
    return []
