# Lane

Lane is a Claude Code plugin that your plugin depends on, which gives your plugin's AI the step it
leaves, as it leaves it.

In development: Lane's rebuild as a plugin that others depend on isn't released.

Lane is for you when you build a Claude Code plugin whose skill and subagents must keep the steps
you give them. With it, your AI notices at once each step it leaves.

## Non-goals

- Lane doesn't check work outside your plugin: it checks only a run of a skill of a plugin that
  gives it rules.
- Lane doesn't write your rules: you write them, from your steps, in your plugin's
  `lane/rules.json`.
- Lane doesn't guard security: hold what must never happen with branch protection or Claude Code's
  permission rules.
- Lane doesn't judge how well a step was done beyond your own check: add a review subagent for
  that.
- Lane doesn't make the AI go back to its step: that rests on your steps and the model.

## Requirements

- macOS or Linux: `uname` shows it.
- Claude Code 2.1.328 or later, where your plugin runs: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- A plugin that Claude Code takes as valid: `claude plugin validate <your plugin's folder>` shows
  `✔ Validation passed`.

## Installation

Name Lane among the dependencies of your plugin's `.claude-plugin/plugin.json`:

```json
"dependencies": [{ "name": "lane", "marketplace": "ccpm" }]
```

Allow the marketplace `ccpm` in your marketplace's `.claude-plugin/marketplace.json`:

```json
"allowCrossMarketplaceDependenciesOn": ["ccpm"]
```

Have each user of your plugin add `ccpm` before they install your plugin, as Claude Code installs
a dependency only from a marketplace they've added:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install <your plugin>@<your marketplace>
```

The install then lists `lane` among the dependencies it installed.

## Walkthrough

The walkthrough comes with Lane's first release: a run of a plugin that writes `CHANGELOG.md`
entries, its writer stopped as it writes another file, and its reviewer's result moving the run.

## How it works

Lane gives an AI that leaves a step of your plugin the step's own sentence, so that it notices at
once.

![How Lane works, from your plugin's rules to each move it checks](images/how-it-works.svg)

### "A hook that only refuses leaves the AI to find another way."

When Lane stops a call, the AI gets the sentence of the step it left and what to do instead.

### "The AI says it did the step, but did it?"

A step, an item of its checklist, a read, or a result counts only from the AI's own call: a Read
itself, or a run of one of Lane's commands that your step names. A reply never counts.

### "Each check is code to write and test."

You give each rule a type of Lane's and its values, such as the files a step may write. The type
makes both the check and the sentence the AI reads.

### "The main conversation starts the wrong subagent, or stops while one is due."

Your routes say which subagent starts after each result. Lane gives the main conversation each
start due, and stops any other start, and its end while a start is due.

### "A run that stops starts over."

Lane keeps a record of the run's starts and results, so the run goes on after `/compact`. In a new
conversation, it goes on from the results your plugin keeps, through an adapter of yours.

### "Does it check other work in the same conversation?"

No. Lane checks only your skill's run, from its call until its routes start no more.

## Documentation

- [Changelog](CHANGELOG.md): for you when you update Lane, the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
