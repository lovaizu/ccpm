"""The unit cases of resume's main, as resume's `__main__.py` calls it with the StopFailure hook's
input: the waiter that it leaves on a stop at the usage limit, in the session's last permission mode
that the transcript records whole at the top of a line, after 900 seconds or the seconds that
OVERNIGHT_INTERVAL_SECONDS holds; nothing left on any other error; and each refusal, which gives 1
with `resume: <what's wrong>` and leaves nothing: an input that isn't a JSON object, a field missing
or not a string, a transcript that can't be read or records no permission mode that claude accepts,
an interval that isn't a whole number from 1, and claude not on PATH, which `__main__.py` gives
main as None."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import claude_double
import pytest
import resume
from resume.command import PROMPT, main

# The command that starts wait.py, as resume's `__main__.py` gives it.
WAITER = [sys.executable, os.path.join(os.path.dirname(resume.__file__), "wait.py")]


class Left:
    """What resume leaves behind: each command it started, with the folder it started it in."""

    def __init__(self) -> None:
        self.started: list[tuple[list[str], str]] = []

    def __call__(self, argv: list[str], cwd: str) -> None:
        self.started.append((argv, cwd))


@pytest.fixture
def left() -> Left:
    return Left()


def stdin(given: dict[str, Any]) -> bytes:
    return json.dumps(given).encode("utf-8")


def resumed(claude: str, mode: str) -> list[str]:
    """The command that resumes the recorded session headless in the mode, told to go on."""
    session = claude_double.session_id()
    return [claude, "-p", "--resume", session, "--permission-mode", mode, PROMPT]


def refused(answer: tuple[int, str], left: Left, *named: str) -> None:
    """The answer of a refusal: 1, one line on stderr that starts `resume: ` and names each of the
    words given, and nothing left."""
    code, said = answer
    assert code == 1
    assert said.startswith("resume: ")
    assert said.endswith("\n")
    assert "\n" not in said[:-1]
    for words in named:
        assert words in said
    assert left.started == []


# The waiter left.


def test_leaves_the_waiter_that_resumes_the_session_after_900_seconds(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a session that ran in bypassPermissions and stopped at the usage limit
    When the hook runs resume with no interval set
    Then it gives 0, says nothing, and leaves in the session's folder the waiter that resumes the
    session in bypassPermissions after 900 seconds"""
    transcript = claude_double.transcript(
        sessions, claude_double.prompt("bypassPermissions") + claude_double.command()
    )
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == [([*WAITER, "900", *resumed(claude, "bypassPermissions")], project)]


def test_resumes_the_session_in_the_last_permission_mode_that_the_transcript_records(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a session that ran in plan, then in acceptEdits, then ran a command
    When the hook runs resume at the usage limit
    Then the waiter resumes the session in acceptEdits"""
    lines = [claude_double.prompt("plan"), claude_double.prompt("acceptEdits")]
    transcript = claude_double.transcript(sessions, "".join(lines) + claude_double.command())
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == [([*WAITER, "900", *resumed(claude, "acceptEdits")], project)]


def test_passes_over_the_transcripts_last_line_not_yet_whole(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a session that ran in default, whose transcript ends in a line of a prompt in plan that
    Claude Code hasn't written whole yet
    When the hook runs resume at the usage limit
    Then the waiter resumes the session in default"""
    plan = claude_double.prompt("plan")
    mode = '"permissionMode":"plan"'
    # Cut just past the mode, so that the half line names plan, and only passing it over gives
    # default.
    half = plan[: plan.index(mode) + len(mode)]
    transcript = claude_double.transcript(sessions, claude_double.prompt("default") + half)
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == [([*WAITER, "900", *resumed(claude, "default")], project)]


def test_passes_over_a_line_that_names_a_permission_mode_only_within_it(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a session that ran in default, then read a line of a transcript that records plan,
    which its transcript keeps within the line of the command's output
    When the hook runs resume at the usage limit
    Then the waiter resumes the session in default"""
    read = claude_double.output('{"type":"user","permissionMode":"plan"}\n')
    transcript = claude_double.transcript(sessions, claude_double.prompt("default") + read)
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == [([*WAITER, "900", *resumed(claude, "default")], project)]


def test_waits_the_seconds_that_overnight_interval_seconds_holds(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given OVERNIGHT_INTERVAL_SECONDS holding 1, the least it may hold
    When the hook runs resume at the usage limit
    Then the waiter resumes the session after 1 second"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("auto"))
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {"OVERNIGHT_INTERVAL_SECONDS": "1"}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == [([*WAITER, "1", *resumed(claude, "auto")], project)]


# Nothing left on another error.


def test_leaves_nothing_on_an_error_other_than_rate_limit(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a session that stopped on authentication_failed
    When the hook runs resume
    Then it gives 0, says nothing, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("default"))
    given = claude_double.stop_failure(transcript, project)
    given["error"] = claude_double.other_error()

    answer = main(stdin(given), {}, claude, WAITER, left)

    assert answer == (0, "")
    assert left.started == []


# The refusals.


def test_refuses_an_input_that_isnt_json(claude: str, left: Left) -> None:
    """Given the hook's input being the error's text, not JSON
    When the hook runs resume
    Then it gives 1, saying that the input isn't JSON, and leaves nothing"""
    answer = main(b"API Error: Rate limit reached", {}, claude, WAITER, left)

    refused(answer, left, "JSON")


def test_refuses_json_that_isnt_an_object(claude: str, left: Left) -> None:
    """Given the hook's input being a JSON array
    When the hook runs resume
    Then it gives 1, saying that the input must be a JSON object, and leaves nothing"""
    answer = main(b'["rate_limit"]', {}, claude, WAITER, left)

    refused(answer, left, "JSON object")


@pytest.mark.parametrize("field", ["session_id", "transcript_path", "cwd"])
def test_refuses_an_input_missing_a_field(
    field: str, sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit whose input lacks the field
    When the hook runs resume
    Then it gives 1, naming the field, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("default"))
    given = claude_double.stop_failure(transcript, project)
    del given[field]

    answer = main(stdin(given), {}, claude, WAITER, left)

    refused(answer, left, field)


@pytest.mark.parametrize("field", ["session_id", "transcript_path", "cwd"])
def test_refuses_an_input_whose_field_isnt_a_string(
    field: str, sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit whose input gives the field as the number 42
    When the hook runs resume
    Then it gives 1, naming the field, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("default"))
    given = claude_double.stop_failure(transcript, project)
    given[field] = 42

    answer = main(stdin(given), {}, claude, WAITER, left)

    refused(answer, left, field)


def test_refuses_a_transcript_that_cant_be_read(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit whose transcript isn't there
    When the hook runs resume
    Then it gives 1, naming the transcript, and leaves nothing"""
    transcript = os.path.join(sessions, "gone.jsonl")
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    refused(answer, left, transcript)


def test_refuses_a_transcript_that_records_no_permission_mode(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit whose transcript holds only a command that the user ran
    When the hook runs resume
    Then it gives 1, naming the transcript, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.command())
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    refused(answer, left, transcript)


def test_refuses_a_permission_mode_that_claude_doesnt_accept(
    sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit whose transcript's last mode is unrestricted, which claude's
    --permission-mode doesn't accept
    When the hook runs resume
    Then it gives 1, naming the transcript, and leaves nothing"""
    transcript = claude_double.transcript(
        sessions, claude_double.prompt("default") + claude_double.prompt("unrestricted")
    )
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, claude, WAITER, left)

    refused(answer, left, transcript)


@pytest.mark.parametrize(
    "seconds",
    [
        pytest.param("0", id="zero"),
        pytest.param("-60", id="negative"),
        pytest.param("1.5", id="fraction"),
        pytest.param("fifteen", id="words"),
        pytest.param("", id="empty"),
    ],
)
def test_refuses_an_interval_that_isnt_a_whole_number_from_1(
    seconds: str, sessions: str, project: str, claude: str, left: Left
) -> None:
    """Given a stop at the usage limit with OVERNIGHT_INTERVAL_SECONDS holding no whole number
    from 1
    When the hook runs resume
    Then it gives 1, naming OVERNIGHT_INTERVAL_SECONDS, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("default"))
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {"OVERNIGHT_INTERVAL_SECONDS": seconds}, claude, WAITER, left)

    refused(answer, left, "OVERNIGHT_INTERVAL_SECONDS")


def test_refuses_where_claude_isnt_on_path(sessions: str, project: str, left: Left) -> None:
    """Given a session that stopped at the usage limit, with no claude on PATH
    When the hook runs resume
    Then it gives 1, saying that claude isn't on PATH, and leaves nothing"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("default"))
    given = claude_double.stop_failure(transcript, project)

    answer = main(stdin(given), {}, None, WAITER, left)

    refused(answer, left, "claude", "PATH")
