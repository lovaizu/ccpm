# Changelog

## [Unreleased]

### Added

- The hands_off lane stops a subagent running a command its step says not to run, in the forms the AI writes, such as `git -C notes commit` or `cd notes && git commit`, and tells it `<plugin>: Do not run <commands>.` — the subagent goes back to its step instead of looking for another way round the refusal.
- The lanes you approve are written into your plugin word for word, the sentence at the end of its step and one hook for each subagent in `hooks/hooks.json`, your other hooks left as they were, with lane's code in `hooks/lane/` — what your subagent is told on a drift is the sentence its step says.
- A lane whose step no longer says its sentence stops the subagent's calls and says to run `lane:up` again — a step you changed is not held to what it no longer says.
- Without Python 3.9 or later run as `python3`, each hook stops the calls it watches and asks for Python to be installed — a lane is never left unkept with no one told.
