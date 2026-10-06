# Plugin rules (ccpm)

How a plugin in this marketplace is built, checked, registered and released, in that order.

Source: facts confirmed in the official docs (plugins-reference / plugin-marketplaces / skills / hooks /
sub-agents at code.claude.com/docs) and the official plugins (plugin-dev, hookify, security-guidance,
code-modernization).

## 1. Build

### Hooks and scripts

- **Follow the official hook best practice** (plugin-dev's `hook-development`).
- **Put each check in its own named file, and one entry file per hook event**, as the official
  `hookify` does (e.g. `pretooluse.py`). This also holds for a script a plugin runs to check its own
  output.
  - Rationale: each check can then be read, fixed and tested on its own.
- **Write what the plugin makes itself in Python 3 with the standard library only, running on 3.9.
  A script that only calls an existing tool, with no logic of its own, may be sh.**
  - Rationale: what the plugin makes itself can be wrong, so it must be held by tests, and bash is
    weak to maintain and test. An existing tool is tested by its makers, so a script that only calls
    it adds little risk of its own. python3 comes with git in the Mac developer tools, so wherever
    git is there, python3 is too; on Linux and Windows it is no less common than jq. TypeScript is
    not used, since Node.js may not be on the user's machine.
- **When python3 is missing, stop and tell the user to install it; never skip the check.**
  - Rationale: a skipped check goes unnoticed, so no one learns the rule is not being kept.
- **State in the plugin's README that Python 3.9 or later is needed.**
- **Write the tests with the standard `unittest`, in `dev/<plugin>/tests/`** (e.g. `dev/rn/tests/`),
  outside the plugin's directory. **Feed in the JSON a hook would receive, and check both a case it
  stops and a case it lets through.**
  - Rationale: a check that never stops anything looks the same as one that works. Installing a
    plugin copies its whole directory, so what only its makers use is kept out of it and never
    reaches the user.
- **Name each test by what must happen, as one sentence (e.g. `test_first_user_reading_git_history_is_blocked`),
  as the official plugins do, and mark its body with `# Given`, `# When` and `# Then`.**
  - Rationale: each test then reads as a situation, an action and what must follow, so a reader sees
    what it guards without tracing the code, and a test whose Then checks nothing stands out.
- **Have the tests run every line the plugin makes itself, and delete a line no test has a reason to
  run.**
  - Rationale: a line no test runs is either not needed, and only adds what can break, or needed and
    left unguarded.
- **Leave a line out of the count with `# pragma: no cover` only when whether it runs depends on
  timing or on an environment the tests cannot make, such as a race between processes or another OS,
  and write the reason beside it.**
  - Rationale: a line left out is no longer counted, so it passes unnoticed; kept to lines that truly
    cannot be run, the count still shows every other gap.
- **Leave to hooks only the mechanical rules an agent's definition cannot hold**, such as a file's
  form, a name, matching IDs, a commit's form, or a push left undone.
- **Have a hook act only in the conversation that runs its plugin and on the agents that conversation
  started, and judge only what was written; never have it decide whether a conversation goes on, or
  rest on how Claude Code runs an agent.**
  - Rationale: other sessions work in the same repository, and a hook that takes them for its own
    breaks work it was never given. Whether to go on is a judgment, and how agents run changes with
    Claude Code; a hook sees neither.

### Making and checking work

- **A plugin that makes work and checks it by use builds on pith: its generator makes, and `/pith:up`
  has pith's first user use the result; the plugin keeps only its own viewpoints for its kinds of
  work and what it does with pith's result.** How a check runs, who judges, and the result file are
  in [pith's design](../../pith/docs/design.md).
  - Rationale: a second copy of how work is checked grows apart from the first, and an improvement
    made once in pith then reaches every plugin.
- **Build from the README's story: for each step, what the user gets there and the least the plugin
  needs to give it. Add nothing a step does not need.**
  - Rationale: a part no step needs still costs the user a wait or a read on every run, and stands
    between them and what they came for.
- **Instruct every role by the purpose and intent of its work. Keep exact steps only where a slip
  breaks something and the purpose cannot tell how, such as the form of a handoff.**
  - Rationale: a step is followed even where it misses, while a purpose fits cases no one foresaw;
    where a slip breaks a handoff, the purpose alone leaves too much room.
- **Fix a fault met in use at its cause, by sharpening a purpose or a viewpoint; add a step or a hook
  only where no purpose can hold it.**
  - Rationale: steps added one per fault come to stand between the user and what the README promised.
- **Start a first user once for a work. Confirm a fix by doing again what the first user did where
  the More was found, and seeing that it no longer happens; do not start a first user again.**
  - Rationale: each new first user brings fresh small remarks, so checking again after every fix never
    ends and keeps the user waiting each round. What the first user reported is concrete, so whether it
    still happens is seen by repeating it, which needs no one ignorant of the discussion.
- **Fix a More only when the receiver cannot carry through their purpose with it; leave any other with
  its reason.**
  - Rationale: fixing what does not stand in the receiver's way spends the user's time on what they did
    not choose the work for, and every fix can break what already serves them.
- **When a More shows something no viewpoint asked, add it as a viewpoint of that session, in its own
  rules, so every maker after it aims at it; at the end, propose it for the plugin's viewpoint files.**
  - Rationale: the viewpoints then grow from what use showed, and a session is not held back waiting
    for the plugin to change.
- **Give the user only what they decide: what the plugin proposes and why, how close the work has come
  to each thing they would choose it for, and each point that is theirs. Keep every Good and More in a
  file they can read when they want.**
  - Rationale: what grows with the work checked is either read whole, spending the time the plugin was
    meant to save, or not read at all.
- **Wait for each agent a role starts before going on; when Claude Code runs it in the background, end
  the turn and go on when its result arrives. Never poll, and never hold the wait with a hook.**
  - Rationale: how Claude Code runs agents changes, and a turn that goes on before a result arrives
    acts on work that is not there yet.

## 2. Check

### Validation: use it as its user would

- **Check every plugin with `/pith:up`, using pith's essentials for a plugin
  (`pith/references/essentials/plugin.md`) and for its skills and agents (`prompt.md`): run its
  README's story end to end as its user would, and set what the user got and what they spent beside
  the version users have now.**
  - Rationale: what the user gets and spends shows only across the whole path; each part can work
    while the whole costs the user hours.
- **Judge a round not by whether every More is gone, but by what the plugin is to its user: for what
  the user meets as new, by whether each attractive quality has come close enough to put it to real
  use; for what they meet as the same plugin changed, by whether it improved what it set out to
  without making worse what worked before. Report, for each attractive quality, how much closer it
  came than the round before, together with that verdict.**
  - Rationale: aiming at no More never ends, since every fix and every new first user brings fresh
    small remarks. When to stop is the user's call, and they make it quickest from whether the plugin
    can be used now, or whether anything got worse.
- **Keep the code that runs this validation in the repository, in `dev/<plugin>/trials/` apart from
  the tests: the whole story, and one scene per attractive quality from the state just before the
  moment the user gets it to the first result that shows whether they got it.**
  - Rationale: a trial put together on the spot guesses at how the last one ran and is lost with the
    session; kept in the repository, it runs the same way each time and is fixed along with the
    plugin. A scene checks a change quickly; the whole story judges the round.
- **Write the trials as the plugin's own code is written, but leave them out of the line count.**
  - Rationale: a trial starts Claude Code, which CI cannot run, and each run is read by whoever
    checks it, so the run itself is its check.
- **Check by script, every time, whatever a script can decide.**
  - Rationale: it costs nothing to run and gives the same answer every time.

### Tests

- **CI runs every plugin's tests on every push, counting which lines they run, and fails when any
  line is not run.**
  - Rationale: tests run by hand are skipped when they matter most, and a gap shown only as a number
    is left as it is; a failing run makes the missing test or the needless line get dealt with.

### Structure check

- **Pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate
  <marketplace-root> --strict`.**
  - Rationale: a malformed manifest fails for every user at install, before any behavior is reached.

## 3. Register

- **Add every plugin to `.claude-plugin/marketplace.json`** — one entry under `plugins` with `name`,
  `description`, `source` (e.g. `./rn`), and `category`. This is what Claude Code reads to install it.
- **List every plugin in the root `README.md`** with a link to its own README (e.g.
  `[rn](./rn/README.md)`) and a one-line description. This is the human entry point.
- **Change the two together** when a plugin is added, renamed, or removed.
  - Rationale: a plugin counts as shipped only once both the machine and a human reader can reach it.

## 4. Release

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
