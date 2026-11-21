"""What the unit cases of rn's prompts share: a throwaway copy of invoicer for each case, as
rn_prompts.room_in makes it."""

from __future__ import annotations

from typing import Any

import pytest
import rn_prompts


@pytest.fixture
def room(tmp_path: Any) -> rn_prompts.Room:
    """A copy of invoicer committed on main, with copies of rn and Lane beside it."""
    return rn_prompts.room_in(str(tmp_path))
