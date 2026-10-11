# Plugin rules (ccpm)

How a plugin in this marketplace is written and tested, checked for structure, registered and
released.

Source: facts confirmed in the official docs (plugins-reference / plugin-marketplaces) and the
official plugins.

## 1. Order of work

- **Write the README and the design before any code or prompt, and have the user sign off the
  design.**
  - Rationale: the code is derived from the documents; code written first stands on a measure no one
    has settled.
- **Write and fix each document with its writ essentials open (`doc.md` with `readme.md` or
  `design.md`).**
  - Rationale: the first user reads only once, so a fix made without them is checked by nothing.
- **Have each document read once, as its reader would, by a first user who does not know the
  discussion, and settle each finding by fixing the decision or principle it comes from.**
  - Rationale: a reading after every fix turns each finding into a patch, and the document drifts
    from its aim while every reading passes.
- **Keep each document to the simplest mechanism that serves the purpose; add no special path for a
  case an existing check already stops.**
  - Rationale: every special path is one more thing for users to learn and builders to keep right.
- **When a document or prompt needs something its essentials file does not ask, add the question to
  that file, whichever plugin is being built, and make the work again against it.**
  - Rationale: what is written with the essentials open is made right as it is written; a gap left
    in them is met again by every plugin made with them.
- **Put each prompt through writ's `prompt.md`, by running it, before the plugin's trials.**
  - Rationale: a prompt is known by what the AI does with it; a trial on unchecked prompts finds the
    prompts' slips, not whether the plugin keeps its promises.

## 2. Code and tests

- **Keep a plugin's README for its users, and its design and all its builders need in
  `dev/<plugin>/`.**
  - Rationale: the README is read by people deciding to use the plugin, and installing copies the
    plugin's folder, so what only builders need stays out of both.
- **Put a `README.md` in each folder where a visitor picks where to go next: the repository root,
  `dev/`, and each `dev/<plugin>/`; put none deeper.** The root leads users to each plugin's README
  and builders to `dev/`; `dev/` lists each plugin's folder and links these rules; `dev/<plugin>/`
  links the design and says how to run the tests and trials, once they exist.
  - Rationale: GitHub shows a folder's README when it is opened, so a visitor finds the way by
    opening folders; a README further down repeats its parent's and drifts from it.
- **Write what the plugin runs on its users' machines in Python 3 with the standard library only, on
  3.9 or later, and say so in its README.** A script that only calls an existing tool may be sh.
  - Rationale: what the plugin makes can be wrong, so it is held by tests; python3 is wherever git
    is, and Node.js may not be.
- **Keep what the plugin's agents read and write as data in JSON, handled with `jq`, and say so in
  its README.**
  - Rationale: an agent reads or changes only the part it needs instead of the whole file, with a
    tool it already knows; the official hooks docs and plugins use `jq` the same way, and a model is
    less likely to overwrite JSON wrongly than Markdown.
- **When python3 or jq is missing, stop and say how to install it.**
  - Rationale: a skipped check goes unnoticed.
- **Put each hook check in its own named file, one entry file per hook event**, as the official
  `hookify` does.
  - Rationale: each check is read, fixed and tested on its own.
- **Keep tests in `dev/<plugin>/tests/` with `unittest`, outside the plugin.** Feed in what the code
  would receive, and check a case it stops as well as one it lets through.
  - Rationale: installing copies the plugin's whole folder; a check that never stops anything looks
    the same as one that works.
- **Write each test before the code it checks, run it and see it fail, then write the code until it
  passes.**
  - Rationale: a test written after the code is fitted to what the code does, not to what it must
    do; a test never seen failing may check nothing.
- **Name each test by what must happen, as one sentence, and mark its body `# Given`, `# When`,
  `# Then`.**
  - Rationale: a test whose Then checks nothing stands out.
- **Have the tests run every line the plugin runs itself, and delete a line no test has a reason to
  run.** `# pragma: no cover`, with its reason beside it, only where whether a line runs depends on
  an environment the tests cannot make. CI counts the lines on every push and fails on any not run.
- **Keep the code that runs the plugin as its user would in `dev/<plugin>/trials/`, out of the line
  count, and run it on the models the plugin's agents name, never a smaller one.**
  - Rationale: CI cannot start Claude Code, so each run is its own check; a smaller model's slips
    are not the plugin's.
- **Judge a trial from the JSONL of every conversation and agent it started, not from its outcome
  alone.**
  - Rationale: the outcome shows that something went wrong, the records show where.
- **Change a prompt or a document after a run only for a cause confirmed in the records and traced
  to what the README and design say it should be; never to fit what one run did.**
  - Rationale: what an AI does varies from run to run; a line added for one run's slip meets a
    different slip in the next, and the additions never settle.
- **Run a trial that needs a real GitHub repository in the private `lovaizu/rn-try`, one
  at a time.**
  - Rationale: pull requests and pushes a run makes stay out of every repository people use, and
    two runs at once would mix in it.

## 3. Structure check

- **Pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate
  <marketplace-root> --strict`.**
  - Rationale: a malformed manifest fails for every user at install, before any behavior is reached.

## 4. Register

- **Add every plugin to `.claude-plugin/marketplace.json`** — one entry under `plugins` with `name`,
  `description`, `source` (e.g. `./rn`), and `category`. This is what Claude Code reads to install it.
- **List every plugin in the root `README.md`** with a link to its own README (e.g.
  `[rn](./rn/README.md)`) and a one-line description. This is the human entry point.
- **Change the two together** when a plugin is added, renamed, or removed.
  - Rationale: a plugin counts as shipped only once both the machine and a human reader can reach it.

## 5. Release

### Version number

- **Write `version` in exactly one place: `plugin.json`, and always set it** (semver, e.g. `0.1.0`).
  - Rationale: when both are set, `plugin.json` wins over the marketplace entry, so a second copy is
    meaningless; `claude plugin validate --strict` fails when it is unset. Users receive an update only
    when it is bumped.
- **Bump only on an explicit release instruction**, not on merge to `main`. Until then, user-facing
  changes wait under CHANGELOG's `## [Unreleased]`.
- **Decide the increment by the largest change, from the user's side:** major for a breaking change
  (on `0.x`, minor instead), minor for a new or changed user-visible behavior, patch for no behavior
  change.

### CHANGELOG

- **Keep `CHANGELOG.md` in the plugin root**, in [Keep a Changelog](https://keepachangelog.com)
  format: `## [Unreleased]` on top while changes are pending, then one `## [x.y.z] - YYYY-MM-DD` per
  release, grouped under `Added` / `Changed` / `Fixed` / `Removed` as they apply.
- **Write an entry for every change a user would notice**, as one line: `<what changed> — <why it
  helps the user>`. Typos, refactors, internal docs and formatting get none.
- **On a release, rename `## [Unreleased]` to the version and date, and leave no empty
  `## [Unreleased]` behind**; it is re-created when the next user-facing change lands.

### Who does what

1. **Assistant** — bumps `version` in `plugin.json`, finalizes `CHANGELOG.md`, commits, and pushes.
2. **Assistant** — asks the user to merge the pull request to `main`; never merges it itself and never
   uses `--admin`.
   - Rationale: `main` is protected, and only the user can clear its required review.
3. **User** — merges, and says so.
4. **Assistant** — tags `main` and publishes the GitHub Release.

### Tags and GitHub Releases

- **Tag each release on `main`** as `<plugin>--v<version>` (e.g. `rn--v0.2.0`), created with
  `claude plugin tag --push` from the plugin directory.
  - Rationale: this is Claude Code's own form: a plugin that depends on another with a version range
    resolves it against these tags, and the prefix lets each plugin version independently. The
    command also validates the plugin and refuses a tag that already exists.
- **Publish a GitHub Release** for that tag, with the CHANGELOG's matching section as the notes.
- **Read release timing from tags and Releases, not from merge commits.**
