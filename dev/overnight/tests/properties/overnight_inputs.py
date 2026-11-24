"""The inputs that more than one of overnight's properties draws, as the product's use brings
them: the tools that the user names, and the zone of the machine that a runner reads its clock
in."""

from __future__ import annotations

from datetime import timedelta, timezone

from hypothesis import strategies as st

# A tool as the user names it: a tool's name, or a rule with words in its parentheses, spaces,
# commas, colons, and quotes among them.
NAMES = st.sampled_from(["Read", "Edit", "Write", "Bash", "WebFetch", "mcp__github__get_issue"])
RULE_WORDS = st.text(st.sampled_from("abcz019 -_.,:*/'\""), min_size=1, max_size=20)
TOOLS = st.lists(
    NAMES | st.builds(lambda name, words: f"{name}({words})", NAMES, RULE_WORDS),
    min_size=1,
    max_size=4,
    unique=True,
).map(tuple)
# Any zone of a machine, as a runner records the stop and the reset in it.
ZONES = st.integers(-12 * 60, 14 * 60).map(lambda minutes: timezone(timedelta(minutes=minutes)))
