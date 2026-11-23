"""The unit cases of checker/command.py, what `queue.py check` takes and prints: `main`, of a queue
file stacked, named whole and from the folder it runs in, of no argument, of a queue file never
stacked and of one not there, both with the version of the plugin's own manifest, of a runs' file
out of form, and of two arguments."""

from __future__ import annotations

import json
import os

import pytest
from checker.command import main
from overnight_bench import Bench, checked_text, the_morning

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def plugin(b: Bench, version: str) -> str:
    """A plugin's folder whose manifest gives the version."""
    root = b.path("plugin")
    b.write(
        os.path.join(root, ".claude-plugin", "plugin.json"),
        json.dumps({"name": "overnight", "version": version}),
    )
    return root


@pytest.mark.supports(
    "test_the_morning_check_shows_each_task_finished_with_its_reply_and_wait",
    "test_a_check_naming_the_queue_from_its_folder_shows_the_same",
)
@pytest.mark.parametrize("named", ["whole", "from the folder"])
def test_a_stacked_queue_is_told_where_its_tasks_stand(b: Bench, named: str):
    """Given the walkthrough's queue the next morning
    When `queue.py check` runs with its whole path, or with its path from the user's home
    Then it gives 0 with the README's text"""
    the_morning(b)
    path = b.queue_file if named == "whole" else os.path.join("overnight", "tonight.json")

    assert main([path], b.home, plugin(b, "0.1.0")) == (0, checked_text(b), "")


@pytest.mark.supports(
    "test_a_check_naming_no_queue_shows_the_version_and_what_to_name",
    "test_a_check_of_a_queue_never_stacked_shows_the_version_and_writes_nothing",
)
@pytest.mark.parametrize(
    "argv",
    [[], ["overnight/tonight.json"], ["overnight/tomorrow.json"]],
    ids=["none", "never stacked", "not there"],
)
def test_a_check_naming_no_stacked_queue_tells_the_manifests_version(b: Bench, argv: list[str]):
    """Given a plugin whose manifest gives 9.8.7, and no queue file, the walkthrough's never
    stacked, or one not there
    When `queue.py check` runs with it
    Then it gives 0 with 9.8.7 and what to name, and writes nothing beside the queue file"""
    code, out, err = main(argv, b.home, plugin(b, "9.8.7"))

    assert (code, out.rstrip("\n"), err) == (0, "overnight 9.8.7: name the queue file to check", "")
    assert not os.path.exists(b.folder)


@pytest.mark.supports("test_a_check_of_a_runs_file_out_of_form_says_whats_wrong")
def test_a_runs_file_out_of_form_gives_1_with_whats_wrong(b: Bench):
    """Given the walkthrough's queue whose `runs.json` isn't JSON
    When `queue.py check` runs with it
    Then it gives 1 naming the runs' file"""
    runs = b.write(os.path.join(b.folder, "runs.json"), "{")

    code, out, err = main([b.queue_file], b.home, plugin(b, "0.1.0"))

    assert code == 1 and runs in out + err


@pytest.mark.supports("test_a_check_naming_no_queue_shows_the_version_and_what_to_name")
def test_two_arguments_give_the_usage(b: Bench):
    """Given two queue files
    When `queue.py check` runs with them
    Then it gives 2 with the usage"""
    code, out, err = main([b.queue_file, b.queue_file], b.home, plugin(b, "0.1.0"))

    assert (code, "usage" in (out + err).lower()) == (2, True)
