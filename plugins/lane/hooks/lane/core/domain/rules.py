"""What every part of lane shares about a plugin's hooks: the names a hook's command carries and
the seconds Claude Code gives each hook lane lays."""

from __future__ import annotations

# A plugin's or a subagent's name, as a hook's command carries it unquoted.
NAME = r"[A-Za-z0-9._-]+"
# The seconds Claude Code gives each hook lane lays before it stops it, as lay.py writes it in the
# hook's entry.
TIMEOUT = 10
