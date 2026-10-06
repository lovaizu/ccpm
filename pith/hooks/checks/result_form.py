"""A result file keeps its form whoever writes it: pith, or the caller settling its Mores."""

import os
import subprocess
import sys
from typing import Optional

CHECK_RESULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts",
                            "check_result.py")


def check(input_data: dict) -> Optional[str]:
    tool_input = input_data.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if not path.endswith(".md") or "/open/" not in path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as handle:
        if not handle.readline().startswith("# Check:"):
            return None
    run = subprocess.run([sys.executable, CHECK_RESULT, path], cwd=input_data.get("cwd") or None,
                         capture_output=True, text=True)
    if run.returncode == 0:
        return None
    return "pith: the result file is out of its form; fix it:\n" + run.stdout.strip()
