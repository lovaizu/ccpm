"""Check 13: the conductor ends its turn only at a stop or with a question waiting in open/;
otherwise it is sent on once. A second end passes, for a turn that answered the user's own words."""
import re

from record import head_message, last_line, open_items

STOP = re.compile(r"→ waiting for #|── approved →|── feedback in |→ paused at ")


def check(data, top, sdir):
    stop = STOP.search(last_line(head_message(top)))
    asking = any("-notes-question" in n for n in open_items(sdir))
    if not stop and not asking and not data.get("stop_hook_active"):
        return ["nothing here is for the user to decide: go on with the next move. End the turn "
                "only at a sign-off or with a question, or again if you were answering the user's "
                "own words"]
    return []
