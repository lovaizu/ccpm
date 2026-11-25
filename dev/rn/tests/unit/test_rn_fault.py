"""The unit cases of fault.py's `end`, how each of rn's commands ends: with each exit code that a
`main` gives, 0, 1, and 2, what it prints on stdout and on stderr, and nothing printed on either;
and with 2 and the traceback where its `main` raises an error that no fault names."""

from __future__ import annotations

import pytest
from fault import Answer, end


@pytest.mark.parametrize(
    ("code", "printed", "said"),
    [
        (0, "abc123\n", ""),
        (1, "", "tree: /deliverables/1/kind: takes one of rn's kinds\n"),
        (2, "", "usage: check <role> <cut>\n"),
        (1, "a line\n", "another line\n"),
        (0, "", ""),
    ],
)
def test_end_exits_with_the_code_printing_each_stream(
    capsys: pytest.CaptureFixture[str], code: int, printed: str, said: str
):
    """Given what a command's main gave: an exit code, stdout, and stderr
    When the command ends with it
    Then it raises SystemExit with the code, having written stdout and stderr as given"""
    with pytest.raises(SystemExit) as raised:
        end(lambda: (code, printed, said))
    assert raised.value.code == code
    assert capsys.readouterr() == (printed, said)


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
