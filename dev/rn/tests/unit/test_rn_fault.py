"""The unit cases of fault.py's `end`, how each of rn's commands ends: with each exit code that a
`main` gives, 0, 1, and 2, what it prints on stdout and on stderr, and nothing printed on either."""

from __future__ import annotations

import pytest
from fault import end


@pytest.mark.supports("test_a_tree_change_out_of_form_is_refused_at_its_commit")
@pytest.mark.parametrize(
    ("code", "printed", "said"),
    [
        (0, "abc123\n", ""),
        (1, "", "tree.py: /deliverables/1/kind: takes one of rn's kinds\n"),
        (2, "", "usage: check.py <role> <cut>\n"),
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
        end((code, printed, said))
    assert raised.value.code == code
    assert capsys.readouterr() == (printed, said)
