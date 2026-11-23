"""The unit cases of remove/command.py, remove.py's command line as a maker runs it to remove what
it made for itself: a file and a folder of the git work tree by their paths from the current
folder, a path absolute in the system's temporary folder, several paths at once, a path out of a
subfolder of the work tree, a link removed as the link, alone or in a folder, a read-only folder,
and a path given within another; and each refusal, which removes none of the paths given and gives
2 with the usage, each wrong path with why, and what to do instead: a path missing, outside both
places, through a link to outside, the top of either, empty, holding a wildcard, a git repository's
`.git` or a folder that holds one, a work tree's path from a folder in none, and no path at all;
and a removal that the system refuses, which gives 2 saying what's left."""

from __future__ import annotations

import os
import stat
from collections.abc import Iterator
from typing import Any

import pytest
from remove.command import USAGE, main
from repo_files import git, write_files


@pytest.fixture
def work(tmp_path: Any) -> str:
    """A git work tree outside the system's temporary folder, holding the command and a cache of
    its tests, as a maker leaves it."""
    folder = os.path.join(str(tmp_path), "invoicer")
    os.makedirs(folder)
    git(folder, "init", "-q")
    write_files(
        folder,
        {
            "invoicer/__main__.py": "print('invoice')\n",
            "invoicer/__pycache__/__main__.cpython-314.pyc": "cache\n",
            "invoicer/__pycache__/lines.cpython-314.pyc": "cache\n",
        },
    )
    return folder


@pytest.fixture
def outside(tmp_path: Any) -> str:
    """A folder that lies neither in the work tree nor in the system's temporary folder, holding
    the user's notes."""
    folder = os.path.join(str(tmp_path), "elsewhere")
    write_files(folder, {"notes.txt": "the user's\n"})
    return folder


@pytest.fixture
def scratch(temp: str) -> str:
    """A folder of a maker's in the system's temporary folder, holding a log of its try."""
    folder = os.path.join(temp, "rn-try")
    write_files(folder, {"log.txt": "tried\n"})
    return folder


@pytest.fixture
def writable() -> Iterator[list[str]]:
    """The folders that a case makes read-only, each given write access again at its end so that
    pytest can remove the case's folder."""
    made: list[str] = []
    yield made
    for folder in made:
        if os.path.isdir(folder):
            os.chmod(folder, stat.S_IRWXU)


def refused(answer: tuple[int, str, str], *said: str) -> None:
    """The answer of a refusal: 2, nothing printed, and on stderr the usage, how to give the paths
    instead, and each of the words given."""
    code, printed, err = answer
    assert (code, printed) == (2, "")
    assert USAGE in err
    assert "exact path" in err
    for words in said:
        assert words in err


# The removals.


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_file_of_the_work_tree_by_its_path_from_the_current_folder_is_removed(work: str):
    """Given a git work tree holding the command and a cache file of its tests
    When remove.py is given the cache file's path from the work tree's top, run there
    Then it gives 0, printing nothing, the file is gone, and the command stays"""
    pyc = "invoicer/__pycache__/lines.cpython-314.pyc"
    assert main([pyc], work) == (0, "", "")
    assert not os.path.lexists(os.path.join(work, pyc))
    assert os.path.isfile(os.path.join(work, "invoicer", "__main__.py"))


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_folder_of_the_work_tree_is_removed_whole(work: str):
    """Given a git work tree whose __pycache__ holds two files
    When remove.py is given invoicer/__pycache__
    Then it gives 0, the folder is gone with both, and the command stays"""
    assert main(["invoicer/__pycache__"], work) == (0, "", "")
    assert not os.path.lexists(os.path.join(work, "invoicer", "__pycache__"))
    assert os.path.isfile(os.path.join(work, "invoicer", "__main__.py"))


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_folder_in_the_system_temporary_folder_by_its_absolute_path_is_removed(
    work: str, scratch: str, temp: str
):
    """Given a maker's folder in the system's temporary folder
    When remove.py is given its absolute path, run in the work tree
    Then it gives 0, the folder is gone, and the temporary folder stays"""
    assert main([scratch], work) == (0, "", "")
    assert not os.path.lexists(scratch)
    assert os.path.isdir(temp)


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_several_paths_at_once_are_each_removed(work: str, scratch: str):
    """Given a cache folder in the work tree and a maker's folder in the system's temporary folder
    When remove.py is given both, one argument each
    Then it gives 0, and both are gone"""
    assert main(["invoicer/__pycache__", scratch], work) == (0, "", "")
    assert not os.path.lexists(os.path.join(work, "invoicer", "__pycache__"))
    assert not os.path.lexists(scratch)


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_path_out_of_a_subfolder_within_the_work_tree_is_removed(work: str):
    """Given a git work tree whose folder docs/ is the current folder
    When remove.py is given ../invoicer/__pycache__
    Then it gives 0, and the cache folder is gone, as the work tree holds the current folder"""
    docs = os.path.join(work, "docs")
    os.makedirs(docs)
    assert main(["../invoicer/__pycache__"], docs) == (0, "", "")
    assert not os.path.lexists(os.path.join(work, "invoicer", "__pycache__"))


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_link_to_a_folder_outside_is_removed_as_the_link(work: str, outside: str):
    """Given a link in the work tree to a folder outside both places
    When remove.py is given the link
    Then it gives 0, the link is gone, and the folder outside still holds its file"""
    link = os.path.join(work, "notes")
    os.symlink(outside, link)
    assert main(["notes"], work) == (0, "", "")
    assert not os.path.lexists(link)
    assert os.path.isfile(os.path.join(outside, "notes.txt"))


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_folder_holding_a_link_to_outside_is_removed_without_following_it(
    work: str, outside: str
):
    """Given a folder in the work tree holding a link to a folder outside both places
    When remove.py is given the folder
    Then it gives 0, the folder is gone, and the folder outside still holds its file"""
    held = os.path.join(work, "build")
    os.makedirs(held)
    os.symlink(outside, os.path.join(held, "notes"))
    assert main(["build"], work) == (0, "", "")
    assert not os.path.lexists(held)
    assert os.path.isfile(os.path.join(outside, "notes.txt"))


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_read_only_folder_is_removed_whole(work: str, writable: list[str]):
    """Given a cache folder in the work tree that holds a file and is read-only, as a tool's cache
    can be
    When remove.py is given the folder
    Then it gives 0, and the folder is gone"""
    cache = os.path.join(work, "invoicer", "__pycache__")
    writable.append(cache)
    os.chmod(cache, stat.S_IRUSR | stat.S_IXUSR)
    assert main(["invoicer/__pycache__"], work) == (0, "", "")
    assert not os.path.lexists(cache)


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_path_given_within_another_given_is_removed_with_it(work: str):
    """Given a cache folder in the work tree
    When remove.py is given the folder, then a file in it, then the folder again
    Then it gives 0, and the folder is gone"""
    pyc = "invoicer/__pycache__/lines.cpython-314.pyc"
    assert main(["invoicer/__pycache__", pyc, "invoicer/__pycache__"], work) == (0, "", "")
    assert not os.path.lexists(os.path.join(work, "invoicer", "__pycache__"))


# The refusals, each of which leaves every path given in place.


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_a_missing_path_beside_a_good_one_removes_neither(work: str, scratch: str):
    """Given a maker's folder in the system's temporary folder
    When remove.py is given it and invoicer/build, which isn't there
    Then it gives 2 naming invoicer/build as missing, with the usage, and the folder stays"""
    refused(main([scratch, "invoicer/build"], work), "invoicer/build: no such file or folder")
    assert os.path.isfile(os.path.join(scratch, "log.txt"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_a_path_outside_both_places_is_refused(work: str, outside: str):
    """Given a folder outside the work tree and the system's temporary folder
    When remove.py is given its file and the work tree's cache folder
    Then it gives 2 naming the file as outside, and both stay"""
    notes = os.path.join(outside, "notes.txt")
    refused(main([notes, "invoicer/__pycache__"], work), f"{notes}: lies outside")
    assert os.path.isfile(notes)
    assert os.path.isdir(os.path.join(work, "invoicer", "__pycache__"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_a_path_through_a_link_to_outside_is_refused(work: str, outside: str):
    """Given a link in the work tree to a folder outside both places
    When remove.py is given the file within it through the link
    Then it gives 2 naming the path as outside, and the file stays"""
    os.symlink(outside, os.path.join(work, "notes"))
    refused(main(["notes/notes.txt"], work), "notes/notes.txt: lies outside")
    assert os.path.isfile(os.path.join(outside, "notes.txt"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
@pytest.mark.parametrize("top", [".", "./", "invoicer/.."])
def test_the_top_of_the_work_tree_is_refused(work: str, top: str):
    """Given a git work tree
    When remove.py is given its top, as . or another path to it
    Then it gives 2 naming the path as the work tree's top, and the work tree stays"""
    refused(main([top], work), f"{top}: is the top of the git work tree")
    assert os.path.isfile(os.path.join(work, "invoicer", "__main__.py"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_the_top_of_the_system_temporary_folder_is_refused(work: str, scratch: str, temp: str):
    """Given a maker's folder in the system's temporary folder
    When remove.py is given the temporary folder itself
    Then it gives 2 naming it as the temporary folder's top, and the maker's folder stays"""
    refused(main([temp], work), f"{temp}: is the top of the system's temporary folder")
    assert os.path.isdir(scratch)


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_an_empty_path_is_refused(work: str):
    """Given a git work tree
    When remove.py is given an empty argument beside the cache folder
    Then it gives 2 saying an empty path names nothing, and the cache folder stays"""
    refused(main(["", "invoicer/__pycache__"], work), "empty")
    assert os.path.isdir(os.path.join(work, "invoicer", "__pycache__"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
@pytest.mark.parametrize(
    "pattern",
    [
        "invoicer/__pycache__/*.pyc",
        "invoicer/__pycache__/lines.cpython-31?.pyc",
        "invoicer/__pycache__/[l]ines.cpython-314.pyc",
    ],
)
def test_a_path_holding_a_wildcard_is_refused(work: str, pattern: str):
    """Given a cache folder in the work tree
    When remove.py is given a pattern of its files that the shell didn't expand
    Then it gives 2 naming the pattern as a wildcard, and each file stays"""
    refused(main([pattern], work), f"{pattern}: ", "wildcard")
    assert os.path.isfile(os.path.join(work, "invoicer", "__pycache__", "lines.cpython-314.pyc"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_the_git_folder_of_the_work_tree_is_refused(work: str):
    """Given a git work tree
    When remove.py is given .git, and then a file within it
    Then it gives 2 naming each as git's, and the repository stays"""
    refused(main([".git", ".git/HEAD"], work), ".git: ", ".git/HEAD: ")
    assert os.path.isfile(os.path.join(work, ".git", "HEAD"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_a_folder_holding_another_work_tree_is_refused(work: str):
    """Given a git work tree holding another in .claude/worktrees/rn-run, as a run's worktree
    lies in the user's repository
    When remove.py is given .claude
    Then it gives 2 naming it as holding a git repository, and the other work tree stays"""
    run = os.path.join(work, ".claude", "worktrees", "rn-run")
    os.makedirs(run)
    git(run, "init", "-q")
    refused(main([".claude"], work), ".claude: holds a git repository")
    assert os.path.isdir(os.path.join(run, ".git"))


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_a_path_from_a_folder_in_no_work_tree_is_refused(outside: str, scratch: str):
    """Given a current folder that lies in no git work tree, holding the user's notes
    When remove.py is given the notes and a maker's folder in the system's temporary folder
    Then it gives 2 naming the notes as outside, and both stay"""
    refused(main(["notes.txt", scratch], outside), "notes.txt: lies outside", "no git work tree")
    assert os.path.isfile(os.path.join(outside, "notes.txt"))
    assert os.path.isdir(scratch)


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_path_in_the_temporary_folder_from_a_folder_in_no_work_tree_is_removed(
    outside: str, scratch: str
):
    """Given a current folder that lies in no git work tree
    When remove.py is given a maker's folder in the system's temporary folder
    Then it gives 0, and the folder is gone"""
    assert main([scratch], outside) == (0, "", "")
    assert not os.path.lexists(scratch)


@pytest.mark.supports("test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py")
def test_no_path_gives_the_usage(work: str):
    """Given a git work tree
    When remove.py is given no argument
    Then it gives 2 with the usage"""
    refused(main([], work))


# A removal that the system refuses.


@pytest.mark.supports("test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made")
def test_a_file_the_system_wont_remove_gives_2_saying_what_is_left(
    work: str, scratch: str, writable: list[str]
):
    """Given a cache file in a folder of the work tree that is read-only, so that the system
    refuses its removal, and a maker's folder in the system's temporary folder
    When remove.py is given the file, then the maker's folder
    Then it gives 2 saying it couldn't remove the file, and that it left the maker's folder"""
    cache = os.path.join(work, "invoicer", "__pycache__")
    writable.append(cache)
    os.chmod(cache, stat.S_IRUSR | stat.S_IXUSR)
    pyc = "invoicer/__pycache__/lines.cpython-314.pyc"
    code, printed, err = main([pyc, scratch], work)
    assert (code, printed) == (2, "")
    assert f"couldn't remove {pyc}" in err
    assert scratch in err
    assert os.path.isdir(scratch)
