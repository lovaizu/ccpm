"""The tests of the double of `claude plugin validate` in plugin_validate.py, as the architecture
best practice's N14.5 tests a double as the part's unit tests test the part: each result it gives
is the one that the real `claude plugin validate` gives on the same plugin. The double is built, so
these cases carry no mark of a part not yet built."""

from __future__ import annotations

import os
import subprocess
from typing import Any

import pytest
from lane_example import put
from plugin_validate import fails, passes


def real(root: str) -> tuple[bool, str]:
    """What the real `claude plugin validate` gives on the plugin: whether it passed, and what it
    printed."""
    done = subprocess.run(
        ["claude", "plugin", "validate", root], capture_output=True, text=True, check=False
    )
    return done.returncode == 0, done.stdout + done.stderr


@pytest.mark.supports("test_a_persons_yes_lays_the_proposal_and_validation_passes")
def test_the_double_passes_a_valid_plugin_as_the_real_one_does(tmp_path: Any):
    """Given a plugin whose plugin.json holds a name and a version
    When the double and the real `claude plugin validate` each check it
    Then both pass, and the real one's output holds what the double says"""
    root = os.path.realpath(str(tmp_path))
    put(root, ".claude-plugin/plugin.json", '{"name": "changelog", "version": "0.1.0"}')
    passed, said = real(root)
    assert passes(root)[0] is passed is True
    assert passes(root)[1] in said


@pytest.mark.supports("test_a_failed_validation_puts_back_each_file_that_laying_changed")
def test_the_double_fails_a_version_that_is_a_number_as_the_real_one_does(tmp_path: Any):
    """Given a plugin whose plugin.json holds the number 1 as its version
    When the double and the real `claude plugin validate` each check it
    Then both fail, and the real one's output holds the error that the double gives"""
    root = os.path.realpath(str(tmp_path))
    put(root, ".claude-plugin/plugin.json", '{"name": "changelog", "version": 1}')
    passed, said = real(root)
    assert fails(root)[0] is passed is False
    assert fails(root)[1].splitlines()[1].strip() in said
