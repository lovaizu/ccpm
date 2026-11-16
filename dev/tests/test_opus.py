"""The cases of the judge's run on Opus, `opus.judged`: the verdict it gives from what `claude -p`
prints, run by a stand-in of `claude` that prints what a recorded run of it printed."""

from __future__ import annotations

import json
import os
import stat
from typing import Any

import opus
import pytest

# The judge's form, as Lane's E2E judge asks for it.
VERDICT = {
    "type": "object",
    "required": ["keeps", "places"],
    "additionalProperties": False,
    "properties": {"keeps": {"type": "boolean"}, "places": {"type": "array"}},
}
# The fields of what `claude -p --output-format json --json-schema` printed on Claude Code 2.1.326
# that judged reads, with `result` the reply of Lane's E2E judge, asked with no schema, that held
# prose with braces after its JSON, from which the stage of 2026-11-16 read the verdict and stopped
# with JSONDecodeError: Extra data. With a schema, Claude Code gave `result` as the JSON alone, and
# `structured_output` apart from it.
PRINTED = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": '{"keeps": true, "places": []}\n```\n\nIn run 1, writer gave {"keeps": true}.',
    "structured_output": {"keeps": True, "places": []},
}


@pytest.fixture
def claude(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """A stand-in of `claude` first on PATH, which keeps its arguments and standard input in the
    folder and prints PRINTED; gives the folder."""
    script = tmp_path / "claude"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "here = os.path.dirname(os.path.abspath(__file__))\n"
        "with open(os.path.join(here, 'asked.json'), 'w') as f:\n"
        "    json.dump({'argv': sys.argv[1:], 'stdin': sys.stdin.read()}, f)\n"
        f"print(json.dumps({PRINTED!r}))\n"
    )
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv(opus.TOKEN, "token")
    return str(tmp_path)


def test_the_verdict_is_the_reply_in_the_judges_form_whatever_prose_follows(claude: str) -> None:
    """Given: `claude` whose reply holds prose with braces after its JSON, with the object in the
    form asked as its structured output.
    When: judged asks the prompt, with the form of Lane's judge.
    Then: it gives that object, having asked on standard input with the form as the JSON schema."""
    assert opus.judged("Judge run 1.", VERDICT) == {"keeps": True, "places": []}
    with open(os.path.join(claude, "asked.json"), encoding="utf-8") as f:
        asked = json.load(f)
    schema = asked["argv"][asked["argv"].index("--json-schema") + 1]
    assert (json.loads(schema), asked["stdin"]) == (VERDICT, "Judge run 1."), "asked as the form"
