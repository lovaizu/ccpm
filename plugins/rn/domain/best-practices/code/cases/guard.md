# Guard, a fail on every question

A hook that stops a write to a protected file, in Python, built the way the maker built Lane's
`guard.py` before the code best practice: its rules, its reading of input, and its settings in one
module, and its tests written after the code. It's a kept case of the [code best
practice](../best-practice.md): a deliverable with the verdict on each question that someone who
knows the maintainer's work gives, so that an evaluator proves itself on it before anyone trusts its
verdicts.

## Specification

- The hook reads a tool call on standard input as JSON, such as `{"tool": "Write", "path":
  "src/a.py"}`, and prints its decision as JSON.
- It denies a `Write` or an `Edit` of a path under `.git/` or `.lane/`, under a folder that the
  user's settings list as protected, or of a file that ends in `.lock`. The decision's reason names
  which rule denied it.
- It allows every other call.
- Input that isn't such a call prints what to fix on standard error, and the hook exits 2.

## Setup

Python 3.9 or later, with nothing else to install. The tests run by `python3 -m unittest discover -s
.`.

## Code

`guard.py`:

```python
import json
import os
import sys


def check(d, mode="strict"):
    x = []
    cfg = os.path.join(os.environ["HOME"], ".guard.json")
    if os.path.exists(cfg):
        x = json.load(open(cfg))["protected"]
    if mode == "strict" or mode == "loose":
        if d["tool"] == "Write" or d["tool"] == "Edit":
            p = d["path"]
            if p.startswith(".git/") or p.startswith(".lane/"):
                return {"decision": "deny", "reason": reason(p)}
            for f in x:
                if p.startswith(f):
                    return {"decision": "deny", "reason": reason(p)}
            if mode == "strict" and p.endswith(".lock"):
                return {"decision": "deny", "reason": reason(p)}
    return {"decision": "allow"}


def reason(p):
    if p.startswith(".git/"):
        return "git's own files"
    if p.startswith(".lane/"):
        return "lane's own files"
    return "protected"


def main():
    d = json.loads(sys.stdin.read())
    print(json.dumps(check(d)))


if __name__ == "__main__":
    main()
```

## Tests

`test_guard.py`:

```python
import io
import unittest
from unittest import mock

import guard


class TestGuard(unittest.TestCase):
    def test_check_1(self):
        for p in [".git/config", ".lane/a.json", "src/a.py"]:
            r = guard.check({"tool": "Write", "path": p})
            if p.startswith("src"):
                self.assertEqual(r["decision"], "allow")
            else:
                self.assertEqual(r["decision"], "deny")

    @mock.patch("guard.reason")
    def test_check_2(self, reason):
        reason.return_value = "x"
        guard.check({"tool": "Edit", "path": ".git/HEAD"})
        reason.assert_called_once_with(".git/HEAD")

    def test_check_3(self):
        self.assertEqual(
            guard.check({"tool": "Write", "path": "a.lock"}, "loose")["decision"], "allow"
        )

    def test_main(self):
        with mock.patch("sys.stdin", io.StringIO('{"tool": "Read", "path": "x"}')):
            guard.main()
```

## How the maker worked

1. The maker wrote `guard.py` whole, then wrote the tests in one commit after it, and saw them pass.
2. Mutation testing then left nine mutants alive. The maker added asserts on the lines each mutant
   changed, until the count fell, with no case of the specification named for any of them.

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | `check` holds the rules, the settings file, and the reasons at once. A change to how settings load means reading the rules too. |
| Q2 | no | The rules read `HOME` and open a file themselves, so no test runs them without the user's machine. |
| Q3 | no | The rules are an `if` chain inside one function. Each is a rule checked and named alone, the problem a Specification or a list of rule functions answers. |
| Q4 | no | `.git/` and `.lane/` each appear in `check` and again in `reason`, so a new protected folder takes two changes. |
| Q5 | no | The `mode` parameter and its `loose` value answer no line of the specification. |
| Q6 | no | A call with no path stops with a `KeyError` traceback and exit 1. The specification asks for a message and exit 2. |
| Q7 | no | The tests follow the code's branches. No test covers a folder from the settings, an `Edit` of a `.lock` file, or a call that isn't JSON. |
| Q8 | no | The tests came after the code, so none of them has shown that it fails without its behavior. |
| Q9 | no | `test_check_1` loops over three paths and branches on each. Its name, like the others, says no behavior. |
| Q10 | no | `test_check_2` mocks `reason`, a function inside the module, and checks the call. It breaks on a rename that keeps every decision. |
| Q11 | no | `check` reads the real `~/.guard.json`, so a protected folder in the user's settings changes what the tests see. |
| Q12 | no | The names `d`, `x`, `p`, and `f` say nothing, and `check` nests four levels of conditions. |
| Q13 | no | The asserts added for the mutants check the mutated lines and name no case, and `test_main` asserts nothing. |
| Q14 | no | No test covers a folder from the settings, the `.lock` rule of an `Edit`, or a reason's text, so a newcomer's change can break any of them with every test passing. |
