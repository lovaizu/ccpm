# Hooks and check scripts (ccpm)

How a plugin here builds its hooks, and the scripts it runs to check its own output.

## Structure

- **Follow the official hook best practice** (plugin-dev's `hook-development`).
- **Put each check in its own named file, and one entry file per hook event**, as the official
  `hookify` does (e.g. `pretooluse.py`).
  - Rationale: each check can then be read, fixed and tested on its own.

## Language

- **Write them in Python 3 with the standard library only, running on 3.9.**
  - Rationale: with many checks, bash is weak to maintain and test. python3 comes with git in the Mac
    developer tools, so wherever git is there, python3 is too; on Linux and Windows it is no less
    common than jq. TypeScript is not used, since Node.js may not be on the user's machine.
- **When python3 is missing, stop and tell the user to install it; never skip the check.**
  - Rationale: a skipped check goes unnoticed, so no one learns the rule is not being kept.
- **State in the plugin's README that Python 3.9 or later is needed.**

## Tests

- **Write the tests with the standard `unittest`, in the plugin's own `tests/`** (e.g. `rn/tests/`),
  as the official `security-guidance` and `code-modernization` plugins do.
- **Feed in the JSON a hook would receive, and check both a case it stops and a case it lets
  through.**
  - Rationale: a check that never stops anything looks the same as one that works.
