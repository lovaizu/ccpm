# lane

lane is a Claude Code plugin that adds checks to your plugin, so that the subagents of your plugin
follow the steps and the order that you set.

The lane plugin is for a person or an AI who builds a Claude Code plugin. In that plugin, subagents
do the work in numbered steps. With the lane plugin, the subagents of your plugin follow their steps
every time your plugin runs. You do not write the code for the checks. One subagent, the
orchestrator, starts the other subagents. With the lane plugin, the orchestrator starts them in the
order that you set, every time your plugin runs. You do not write a script that controls this order.

A rule has two parts: a sentence in a step, and a check of that sentence. The lane plugin calls a
rule a "lane". The check runs on each tool call that the sentence is about, such as a command that
the subagent runs. The check also runs when the subagent ends its work. A violation is a tool call
or an end of work that does not agree with the sentence. When the check finds a violation, the check
stops that tool call or that end of work. Then the check shows the sentence to the subagent again. A
usual hook only refuses the tool call. That hook does not show the step to the subagent. So the
subagent looks for another way to do the same thing. A subagent that sees the sentence of its own
step goes back to the step. The lane plugin writes and tests each type of check one time. It writes
these checks in one script. It copies this script into your plugin. This README calls this script
the check script. For the order, you write a flow. A flow is the order in which the orchestrator
starts the other subagents. The check script tells the orchestrator which subagent to start next.
Until the orchestrator starts that subagent, the check script stops all other actions of the
orchestrator.

**Non-goals**

- The check script checks only the subagents that have rules. It does not check the main
  conversation, a skill, or a subagent without rules. A hook in a skill continues to run until the
  session ends. For this reason, the lane plugin does not add rules to skills. The orchestrator of a
  flow must be a subagent.
- The lane plugin is not a security boundary. Some actions, such as a merge, must be blocked in
  every case. Use the branch protection of GitHub or the permission rules of Claude Code to block
  them.
- The check script sees only the tool calls and the end of work of a subagent. It does not see what
  the subagent thinks. A step such as "Compare each option" cannot have a rule.
- The check script does not read every form of a shell command. For some commands, the check script
  cannot decide which file the command uses. Then the check script stops the tool call. It asks the
  subagent to give the path of the file.
- The check script does not choose the next subagent from the results of a run. A flow is a fixed
  order that you set. The flow goes back to an earlier subagent only when a subagent gives an answer
  that you name, such as the word `more`.
- The check script reads some texts that your plugin writes, such as a list of items that a subagent
  must answer. The check script reads each such text in one format only. The documents of the lane
  plugin describe that format. Your plugin can write the text in another format. In that case, you
  write an adapter. An adapter is a small script that converts the other format into the format that
  the check script reads. You also write test cases for the adapter. Each test case has an input for
  the adapter, and the output that the adapter must give for that input. The lane plugin runs the
  adapter on its test cases before it adds the rules. The adapter does not decide what is a
  violation. The check script decides it.

## Requirements

- Claude Code, on the computer where you build your plugin, and on each computer where your plugin
  runs.
- Python 3.9 or later, on the same computers. The command `python3` must start Python. The script
  `lay.py` of the lane plugin runs on Python. The check script in your plugin also runs on Python.
  If Python is missing, the check script stops each tool call that a rule is about. Then the check
  script tells the subagent to install Python.
- A plugin with subagents. In the file of each subagent, the steps are a numbered list under the
  heading `## Steps`.

## Installation

The lane plugin is in the GitHub repository `lovaizu/ccpm`. This repository is a marketplace of
Claude Code plugins. Add this marketplace, and then install the lane plugin:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install lane@ccpm
```

Then the command `claude plugin list --json` shows `lane@ccpm`. The `installPath` of `lane@ccpm` is
the folder of the lane plugin. Claude Code installs each version in a new folder. So, read
`installPath` again after each update. The script `lay.py` is in the `scripts` folder of that
folder. The lane plugin is ready when this script shows its usage:

```console
$ python3 <installPath>/scripts/lay.py
usage: lay.py print <proposal>
       lay.py write <proposal>
       lay.py up <plugin>
```

## Walkthrough

In this walkthrough, you add two rules to one step of a subagent. Then the walkthrough shows one run
of the plugin with these rules.

The example plugin is `changelog`. It writes the changelog of a project, the file `CHANGELOG.md`.
The skill `/changelog:changelog` starts the subagent `lead`, the orchestrator. `lead` starts the
subagent `writer`. `writer` writes the new entries. Then `lead` starts the subagent `reviewer`.
`reviewer` compares the entries with the commits of the project. The skill shows the entries to you.
After you say OK, the skill commits `CHANGELOG.md`. The file `agents/writer.md` contains step 3 of
`writer`:

```markdown
3. Write the new entries into `CHANGELOG.md`.
```

At this step, `writer` must not write any other file. It also must not commit. You write these two
rules in a JSON file. This file is the proposal. You save the proposal as
`.lane/20261101-changelog/changelog.json` at the root of the repository. The plugin is in the folder
`changelog` at the same root:

```json
{"plugin": "changelog",
 "subagents": [{"name": "writer", "steps": [{"step": 3, "lanes": [
  {"lane": "write_only", "takes": ["CHANGELOG.md"]},
  {"lane": "hands_off", "takes": ["git commit", "git push"]}]}]}]}
```

Each rule has a type, such as `write_only`. The values of the rule are in `takes`. You run `lay.py`
from the root of the repository. The command `lay.py print` shows the step with the new sentences:

```console
$ python3 <installPath>/scripts/lay.py print .lane/20261101-changelog/changelog.json
Lanes on step 3 of writer, each hook acting in writer alone:
  write: Write only `CHANGELOG.md`.              hook write_only
  run:   Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`. Do not run `git commit` or `git push`.
```

You approve this output. Then the command `lay.py write` adds the rules from the same file:

```console
$ python3 <installPath>/scripts/lay.py write .lane/20261101-changelog/changelog.json
Wrote step 3 of writer into agents/writer.md.
Wrote the hooks of writer into hooks/hooks.json.
Wrote the lanes laid into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
Removed the proposal .lane/20261101-changelog/changelog.json.
Removed its folder <the repository>/.lane/20261101-changelog.
```

Later, a person or an AI runs `/changelog:changelog`. The request asks for a changelog entry about
the new export feature. The request also asks for a commit of `CHANGELOG.md`. `lead` gives the
request to `writer` without a change. `writer` reads the changelog and the commits. `writer` writes
the entries into `CHANGELOG.md`. The check script allows this tool call. Then `writer` tries the
export feature. It runs `greet.sh --csv` in a temporary folder. In the command, the name of this
folder is `$d`. The command writes the file `greet.csv` in `$d`. The check script cannot decide
which folder `$d` is. So the check script stops the tool call. `writer` gets this message:

```
changelog: Write only `CHANGELOG.md`.
`$d/greet.csv`, `$d`: lane cannot tell which file is named here, so this lane could not be checked; name each file by its path, without `$`, a backquote or a `cd` lane cannot follow
```

`writer` does not run the command again. `writer` ends its work without a commit. It says that its
instructions forbid a commit. If `writer` runs `git commit`, the check script stops the tool call.
Then `writer` gets this message:

```
changelog: Do not run `git commit` or `git push`.
```

`lead` has no rules, so the check script does not check `lead`. In this run, `lead` itself made the
commit after `reviewer` answered. You had not read the entries yet. To stop this commit, add the
same `hands_off` rule to a step of `lead`.

After an update of the lane plugin, run `lay.py up <the folder of your plugin>` before your next
proposal. This command updates the check script in your plugin to the new version. It also shows
each rule that your plugin has. A new proposal gives rules for some subagents. For each of these
subagents, the new proposal replaces all of the old rules. So, the new proposal must also contain
each old rule that you want to keep.

## How it works

![How lane works](how-it-works.svg)

The check script runs from the copy in the folder `hooks/lane/` of your plugin. So the users of your
plugin do not need the lane plugin. `lay.py` and the check script use the same code to make each
sentence. So, on a violation, the subagent gets the same words that are in its step. The
orchestrator is also a subagent with a rule. The check script finds the next subagent from the flow
and from the answers of the subagents.

## Documentation

- [The lanes](docs/lanes.md) describes each type of rule, its sentence, and the tool calls that its
  check stops. It also describes the full form of the proposal and of adapters. In this document,
  the name of the check script is "the guard".
- [The flow](docs/flow.md) describes the form of a flow and the messages that the orchestrator gets.
  It also describes how the check script reads the answer of each subagent.
- [The changelog](CHANGELOG.md) lists the changes in each version of the lane plugin.

## Development

[The development folder of the lane plugin](../../dev/lane/README.md) holds its UX, its
architecture, and its tests.

## License

[MIT License](../../LICENSE)
