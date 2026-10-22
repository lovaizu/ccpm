# Changelog

## [Unreleased]

### Added

- The hands_off lane stops a subagent running a command its step says not to run, in the forms the AI writes, such as `git -C notes commit` or `cd notes && git commit`, and tells it `<plugin>: Do not run <commands>.` — the subagent goes back to its step instead of looking for another way round the refusal.
- The start_with lane stops each call a subagent makes before it has run the script its step says to run first, and tells it `<plugin>: First run <script>.` — the subagent begins from what the script gives it, not from what it looked for on its own.
- The read_only lane stops a subagent reading a file beside the inputs its step names, by the Read or Grep tool or by `cat`, `head`, `tail`, `sed` or `grep`, and tells it `<plugin>: Read only <input>.` — it works from what its step gives it, not from what it happened to find.
- The read_whole lane stops a subagent writing while it has read only part of an input its step names, read from what it has done since it started, and tells it `<plugin>: Read <input> to its end.` — it does not act on the first part of a long input alone.
- The write_only lane stops a subagent writing any file but the outputs its step names, with Write, Edit or NotebookEdit, or in the folder it works in with a command, such as a redirect, `tee`, `cp`, `mv` or `sed -i`, and tells it `<plugin>: Write only <output>.` — the rest of your project stays as it was, and the subagent goes back to writing what its step names.
- The lanes you approve are written into your plugin word for word, the sentence at the end of its step and one hook for each subagent in `hooks/hooks.json`, your other hooks left as they were, with lane's code in `hooks/lane/` — what your subagent is told on a drift is the sentence its step says.
- A lane whose step no longer says its sentence stops the subagent's calls and says to run `lane:up` again — a step you changed is not held to what it no longer says.
- Without Python 3.9 or later run as `python3`, each hook stops the calls it watches and asks for Python to be installed — a lane is never left unkept with no one told.
