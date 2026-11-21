# How Lane finds a plugin it serves, and how the plugin names Lane's commands

The question this answers is for `dev/lane/architecture.md` N10, how a plugin gets Lane: Lane is
installed beside the plugin, and its hooks read the rules that the plugin holds.

Each answer was found on Claude Code 2.1.328 with two plugins loaded by `--plugin-dir`: `a`, whose
hook wrote each input it got and its environment to a log on UserPromptSubmit, PreToolUse, and
PostToolUse, and `b`, with one skill, `hi`. The runs were `claude -p "say hi using the b:hi skill"`
and `claude -p "/b:hi"`, each with `--model claude-opus-5-5`.

## What does a hook of one plugin get that names another plugin's skill?

Only the skill's name, `b:hi`. PreToolUse and PostToolUse of the Skill call give
`"tool_input":{"skill":"b:hi"}`, and PostToolUse also `"tool_response":{"success":true,"commandName":"b:hi"}`.
A typed command gives UserPromptSubmit `"prompt":"/b:hi"`. No field and no variable of the
environment names `b`'s folder: `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` name `a`'s own.
`~/.claude/plugins/installed_plugins.json` lists no plugin loaded by `--plugin-dir`.

## Where can the hook read the folder of the plugin whose skill runs?

In the conversation's transcript, at `transcript_path` of each hook's input. Once the skill
expands, by the Skill tool or by a typed command, the transcript holds a user message whose text
opens `Base directory for this skill: <b's folder>/skills/hi`. Both runs printed it by
`grep -o "Base directory for this skill[^\"]*" <transcript_path>`. The transcript's form isn't
documented, so a contract test of Lane's double of Claude Code holds it on each new version.

## How does a plugin's step name a command of Lane's, whose folder it doesn't know?

By the command's name alone: Claude Code puts the `bin/` folder of each plugin it loads on the
path of the Bash tool. With `a` holding an executable `bin/lane-hello`,
`claude -p "Run the shell command: lane-hello ; then print what it printed, word for word." --plugin-dir a`
printed `lane-hello ran from <a's folder>/bin/lane-hello`.
