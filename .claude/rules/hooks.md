# Hooks and check scripts (ccpm)

How a plugin here builds its hooks and the scripts it runs to check its own output, and keeps its roles apart.

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

## Keep roles apart by their definitions, not by hooks

- **Keep a checking role from what it must not see by how the role is defined:** start it as a
  separate subagent that does not carry over the conversation, set `omitClaudeMd`, hand it only the
  work and its purpose, and take the tool that calls other agents away from the producing role, so the
  producing role cannot call the checking role.
  - Rationale: the checking role (the first user) is there to use the work as its user would, without
    knowing how it was made. A subagent can be called by anyone, from the conversation, a user, a
    forked skill or another subagent, so watching every way it can be called with hooks grows tangled;
    a plugin's settings cannot restrict it either. A definition holds however it is called.
- **Leave to hooks only the mechanical rules a definition cannot hold**, such as a file's form, a
  name, matching IDs, a commit's form, or a push left undone.
