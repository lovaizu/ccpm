"""The unit cases of fault.py's `end`, how each of rn's commands ends: with the exit code that a
`main` gives and what it prints on stdout and on stderr; and with 2 and the traceback where its
`main` raises an error that no fault names."""

from __future__ import annotations

import pytest
from fault import Answer, end


def test_end_exits_with_the_code_printing_each_stream(capsys: pytest.CaptureFixture[str]):
    """Given what a command's main gave: the exit code 1, a line on stdout, and one on stderr
    When the command ends with it
    Then it raises SystemExit with the code, having written stdout and stderr as given"""
    with pytest.raises(SystemExit) as raised:
        end(lambda: (1, "a line\n", "another line\n"))
    assert raised.value.code == 1
    assert capsys.readouterr() == ("a line\n", "another line\n")


def test_end_of_a_main_that_raises_an_unexpected_error_exits_2_with_its_traceback(
    capsys: pytest.CaptureFixture[str],
):
    """Given a command's main that raises an error that no fault names, a KeyError
    When the command ends with it
    Then it raises SystemExit with 2, as a role reads 2 as a check that couldn't check, having
    written nothing on stdout and the error's traceback on stderr"""

    def main() -> Answer:
        raise KeyError("cut")

    with pytest.raises(SystemExit) as raised:
        end(main)
    assert raised.value.code == 2
    printed, said = capsys.readouterr()
    assert printed == ""
    assert said.startswith("Traceback (most recent call last):\n")
    assert said.endswith("KeyError: 'cut'\n")
