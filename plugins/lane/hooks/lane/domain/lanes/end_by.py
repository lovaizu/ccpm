"""Says the commands by which a role or the skill gives its result, on its last step, a sentence
that `lay.py write` lays from the routes and from the lanes checked at the end."""

from __future__ import annotations

# The commands are the result script's, which the work's own instructions don't cover, so a role
# told to run none of the work's scripts still gives its result.
WORDING = (
    "End by running `<commands>`. That command gives your result to the plugin and is no part of"
    " the work, so an instruction not to run the work's scripts doesn't cover it."
)
# Each wording that Lane laid before the current one, newest first.
EARLIER = (WORDING.replace("doesn't", "does not"), "End by running `<commands>`.")
COMMANDS = "commands"
