"""What overnight's integration cases share: a bench for each case, ended with it, and the fixture
`broken`, which takes the part that holds a case's principle item out of the bench's copy of
overnight where TRACE_BROKEN is 1, as the plugin guide's A principle's test seen to fail says. A
part taken out is an interface given again at the end of its module, wrapping or replacing the one
before, so the copy runs without what holds the item."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from typing import Any

import overnight_bench
import pytest
from overnight_bench import Bench, given_again


@pytest.fixture
def b(tmp_path: Any) -> Iterator[Bench]:
    """The bench: overnight, the walkthrough's repository, and the stand-in of Claude Code."""
    made = overnight_bench.bench(str(tmp_path))
    yield made
    made.end()


def stops_end_the_piece(b: Bench) -> None:
    """A run that the usage limit stopped is read as one that ended by an error of its own, so
    the runner never resumes it."""
    given_again(
        b,
        "domain/runner/reply.py",
        "_given_read = read\n\n\n"
        "def read(output):\n"
        "    given = _given_read(output)\n"
        "    return Failed('the usage limit') if isinstance(given, Limited) else given\n",
    )


def in_the_persons_folder(b: Bench) -> None:
    """A piece's worktree is the person's own folder, on the person's branch."""
    given_again(
        b,
        "domain/handover/worktree.py",
        "def make(repository, number):\n"
        "    import subprocess\n"
        "    branch = subprocess.run(\n"
        "        ['git', '-C', repository, 'branch', '--show-current'],\n"
        "        capture_output=True, text=True, check=True,\n"
        "    ).stdout.strip()\n"
        "    return Worktree(repository, branch)\n",
    )


def every_tool_allowed(b: Bench) -> None:
    """Claude Code runs in its mode that lets each call through, not only the named tools."""
    given_again(
        b,
        "domain/runner/claude.py",
        "def run(piece, conversation):\n"
        "    import subprocess\n"
        "    argv = ['claude', '-p', '--output-format', 'json',\n"
        "            '--permission-mode', 'bypassPermissions']\n"
        "    if conversation is not None:\n"
        "        argv += ['--resume', conversation]\n"
        "    done = subprocess.run(argv, input=piece.prompt, cwd=piece.folder,\n"
        "                          capture_output=True, text=True, check=False)\n"
        "    return Output(done.returncode, done.stdout, done.stderr)\n",
    )


def in_the_session(b: Bench) -> None:
    """The runner starts as a process of the session that hands the piece over, not apart."""
    given_again(
        b,
        "domain/runner/start.py",
        "def start(piece):\n"
        "    import subprocess\n"
        "    from runner.command import line\n"
        "    args, stdin = line(piece)\n"
        "    started = subprocess.Popen(\n"
        "        args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,\n"
        "        stderr=subprocess.DEVNULL, cwd=piece.folder, text=True,\n"
        "    )\n"
        "    started.stdin.write(stdin)\n"
        "    started.stdin.close()\n"
        "    return started.pid\n",
    )


def written_in_part(b: Bench) -> None:
    """A record of a wait is written in two parts, half a second apart."""
    given_again(
        b,
        "domain/pieces/record.py",
        "_given_wait = wait\n\n\n"
        "def wait(repository, number, began, resets):\n"
        "    import glob\n"
        "    import os\n"
        "    import time\n"
        "    given = _given_wait(repository, number, began, resets)\n"
        "    for path in glob.glob(os.path.join(repository, '.overnight', f'*-{number}', '*')):\n"
        "        with open(path, encoding='utf-8') as f:\n"
        "            text = f.read()\n"
        "        with open(path, 'w', encoding='utf-8') as f:\n"
        "            f.write(text[: len(text) // 2])\n"
        "            f.flush()\n"
        "            time.sleep(0.5)\n"
        "            f.write(text[len(text) // 2 :])\n"
        "    return given\n",
    )


def waits_unrecorded(b: Bench) -> None:
    """A wait leaves the record as it was."""
    given_again(
        b,
        "domain/pieces/record.py",
        "def wait(repository, number, began, resets):\n"
        "    return next(each for each in read(repository) if each.handed.number == number)\n",
    )


def stops_unseen(b: Bench) -> None:
    """Each piece stands as its record says, whether its runner still runs or not."""
    given_again(
        b,
        "domain/pieces/standing.py",
        "def stand(records):\n    return Night(tuple(Standing(each, None) for each in records))\n",
    )


def every_piece_counted(b: Bench) -> None:
    """The share stopped counts each piece."""
    given_again(
        b,
        "domain/pieces/standing.py",
        "Night.stopped = property(lambda self: len(self.standings))\n",
    )


BREAKS: dict[str, Callable[[Bench], None]] = {
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset": (
        stops_end_the_piece
    ),
    "test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts": (
        in_the_persons_folder
    ),
    "test_a_call_to_a_tool_not_named_is_refused_at_once_and_the_piece_goes_on_to_its_end": (
        every_tool_allowed
    ),
    "test_a_piece_goes_on_after_the_session_that_handed_it_over_closes": in_the_session,
    "test_a_record_read_while_its_runner_writes_it_is_read_whole_each_time": written_in_part,
    "test_a_pieces_changes_stay_on_its_branch_and_the_persons_branch_and_folder_as_they_were": (
        in_the_persons_folder
    ),
    "test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends": (
        waits_unrecorded
    ),
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing": (
        stops_unseen
    ),
    "test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call": (
        every_piece_counted
    ),
}


@pytest.fixture
def broken(b: Bench, request: pytest.FixtureRequest) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1."""
    if os.environ.get("TRACE_BROKEN") == "1":
        BREAKS[request.node.originalname](b)
