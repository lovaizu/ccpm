"""Where a tool call reaches, for the checks on what an agent may touch."""
import os

PATHS = {"Read": "file_path", "Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path",
         "Grep": "path", "Glob": "path"}
CHANGES = ("Write", "Edit", "NotebookEdit")


def target(data):
    """The real path a file tool reaches, or None for any other tool."""
    tool = data.get("tool_name")
    if tool not in PATHS:
        return None
    given = (data.get("tool_input") or {}).get(PATHS[tool]) or "."
    return os.path.realpath(os.path.join(data.get("cwd", ""), given))


def inside(path, folder):
    folder = os.path.realpath(folder)
    return path == folder or path.startswith(folder + os.sep)


def spellings(path):
    """The ways a command may write the path: as given and as its real path."""
    real = os.path.realpath(path)
    return {path, real, real[len("/private"):] if real.startswith("/private/") else real}
