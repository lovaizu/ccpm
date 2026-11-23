"""The generators of what overnight's use brings, which its property-based tests draw from: from the
concepts and rules of the architecture's Concept model and the forms that the README's walkthrough
names, never from the branches of the code."""

from __future__ import annotations

import string
from datetime import datetime, timedelta, timezone

from hypothesis import strategies as st

# A task's name, as the queue file's form takes it: a letter or digit, then letters, digits, dots,
# underscores, and hyphens, such as `review-payments`.
NAMES = st.from_regex(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,20}\Z")
# A word of a folder's or a file's name, as a person or an AI writes one, spaces and letters beyond
# ASCII among them.
WORDS = st.text(string.ascii_letters + string.digits + " ._-éß", min_size=1, max_size=12).filter(
    lambda word: word.strip(" .") == word and word not in (".", "..")
)
# A moment of a night on the computer's clock, in any offset from UTC that a computer keeps.
OFFSETS = st.integers(-12 * 4, 14 * 4).map(
    lambda quarters: timezone(timedelta(minutes=15 * quarters))
)
MOMENTS = st.builds(
    lambda minutes, zone: datetime(2026, 1, 1, tzinfo=zone) + timedelta(minutes=minutes),
    st.integers(0, 2 * 365 * 24 * 60),
    OFFSETS,
)
# A moment on the computer's own clock, as `runner.clock` gives it, in its own offset from UTC.
LOCAL_MOMENTS = st.integers(0, 2 * 365 * 24 * 60).map(
    lambda minutes: (datetime(2026, 1, 1) + timedelta(minutes=minutes)).astimezone()
)
