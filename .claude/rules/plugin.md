# Plugin rules (ccpm)

How a plugin in this marketplace is built, step by step in the order the work is done. Each step
names the checklists in `rn/checklists/` to open while doing it; a checklist says what
the work must be, and this file says how the work goes.

When a step's work needs something its checklist does not ask, add the question to that checklist,
whichever plugin is being built, and make the work again against it.

- Rationale: what is made with the checklist open is made right as it is made; a gap left in a
  checklist is met again by every plugin made with it.

Work made before a rule or a checklist changed is read against the new one before it is committed.

- Rationale: work made earlier was checked against what the rules said then; committed unread, it
  brings back what the change was made to stop.

Source: facts confirmed in the official docs (plugins-reference / plugin-marketplaces, prompting
best practices / skill authoring best practices) and the official plugins.

## Steps

### 1. Write the README

**Write `<plugin>/README.md` with `usability.md` and `readme.md` open, and have the user agree to it
before anything else is made.**

- Rationale: everything after is built to what the README promises the user; built first, it would
  stand on a measure no one has settled.

### 2. Write the design

**Write `dev/<plugin>/design.md` on [how a plugin works](../../dev/architecture.md), with `usability.md`
and `design.md` open, and have the user agree to it.**
Beside it, put `dev/<plugin>/README.md`, which links the design and says how to run the tests and
trials once they exist; `dev/README.md` lists each plugin's folder and links these rules, and the
root `README.md` leads users to each plugin's README and builders to `dev/`. Put no README deeper.

- Rationale: installing copies the plugin's folder, so what only builders need stays in `dev/`;
  GitHub shows a folder's README when it is opened, so a visitor finds the way by opening folders,
  and a README further down repeats its parent's and drifts from it.

**Design the plugin to take in what is general and leave to the user's project only what is its
own; where the user meets a general need the plugin lacks, it asks them to help improve it and
whether it may open an issue to its makers, and opens one only on their yes.** The issue holds the
need and its points alone, never the user's source or anything of their project.

- Rationale: the plugins are open source, so a need met once improves the plugin for every user;
  what is general needs nothing of a project, so a project's detail in the issue shows the need was
  not drawn general, and the user's work stays theirs unless they choose to share.

### 3. Have the README and the design read once

**Have a first user who does not know the discussion read the README and the design once, as their
readers would, and settle each finding by fixing the decision or principle it comes from.**

- Rationale: a reading after every fix turns each finding into a patch, and the documents drift
  from their aim while every reading passes.

### 4. List the units

**List the units to build. A unit is the smallest slice through which the user meets one or more of
the key results in the UX, from start to end. The first unit moves one key result by the
thinnest path.**

- Rationale: a unit run end to end shows early whether the plugin keeps its promise, and the first
  shows soonest whether the user would choose it at all.

### 5. Build each unit

**For each unit, in order, do a to e.**

a. **Write its tests in `dev/<plugin>/tests/` with `unittest` and `code.md` open, run them and
   see them fail.**
   - Rationale: a test written after the code is fitted to what the code does, not to what it must
     do.

b. **Write the code with `code.md` open until the tests pass.** What runs on users' machines is
   Python 3, 3.9 or later, with the standard library only, and the README says so; a script that
   only calls an existing tool may be sh. CI counts the lines and branches on every push and fails
   on any not run; it breaks the code with Cosmic Ray and fails on any break no test catches, and
   runs property tests with Hypothesis, on new inputs each time. Each check runs on Python 3.9 and
   the newest, Cosmic Ray and Hypothesis on the newest alone. Before each push,
   `dev/githooks/pre-push` runs the checks on what the push changes: the tests of each plugin it
   changes, the property tests on few inputs, and the mutants on the lines it changes; and stops the
   push on a failure. CI runs them whole: every plugin's tests, the property tests on many inputs,
   and every mutant, each plugin's in a job of its own, all at once. CI's `tests` job runs on every
   push and skips the checks on a push that changes only what no check reads, such as the session
   records and the decisions, where the commit before it passed.
   - Rationale: python3 is wherever git is while Node.js may not be; a skipped check goes unnoticed;
     users run 3.9, and the two tools need newer versions only to test, not to run; a check left to
     be run by hand is forgotten and found only by CI after the push, and checking what a change
     touches takes seconds to a minute where checking the whole takes long, which CI does on every
     push anyway; `main` takes a pull request only when `tests` has passed, so it always runs, and
     passes on only what was checked.

   **Look first for what the plugins already share and use it.** Code more than one plugin needs,
   such as how a hook reads a command, is kept once in the plugin whose job it is, with its tests
   in that plugin's `dev/<plugin>/tests/`, and each other plugin takes it through a relative
   symbolic link; what the tests share, such as a repository made once and copied for each test,
   is kept beside that code's tests, as lane's `dev/lane/testing.py`.
   `dev/check.sh` fails on lines copied between any two files, but a test's expected value written
   out again. A plugin's whole test run takes seconds, and the time each check takes is read on
   every run.
   - Rationale: installing copies the target of a link within the marketplace into the plugin, so
     each plugin carries the shared code while it is written, tested and fixed in one place; a copy
     is fixed in one file and left wrong in the other; a test that takes its expected value from the
     code checks the code against itself; mutation testing runs the tests once for each mutant, so a
     slow test run makes every change wait.

c. **Write each prompt, a skill or an agent, with `usability.md` and `prompt.md` open, and run it to see
   that the AI does what its Role and Steps say.**
   - Rationale: a prompt is known by what the AI does with it; a trial on unchecked prompts finds
     the prompts' slips, not whether the plugin keeps its promises.

d. **Lay the lanes the prompts' steps call for with lane's `lane:up`, with `prompt.md` open.** A
   check no lane holds is added to lane as a lane of its own, with `code.md` open, in its own named
   file, with one entry file per hook event, as the official `hookify` does.
   - Rationale: each check is written and tested once, in lane, and each plugin takes lane's code
     through a link; a check kept in a plugin of its own reads the AI's calls apart from lane's and
     drifts from it; each check is read, fixed and tested on its own.

e. **Try the unit as its user, by the design's Verification**, with the code that runs it kept in
   `dev/<plugin>/trials/`, out of the line count. A trial that needs a real GitHub repository runs
   in `lovaizu/playground`, one at a time, on a branch of its own, and the branch, its pull requests
   and whatever else it made there are removed when it ends.
   - Rationale: CI cannot start Claude Code, so each run is its own check; pull requests and pushes
     a run makes stay out of every repository people use, `main` there takes nothing but through a
     reviewed pull request, and two runs at once, or one left behind, would mix with the next.

**Change a prompt or a document after a trial only for a cause confirmed in the records and traced
to what the README and the design say it should be.**

- Rationale: what an AI does varies from run to run; a line added for one run's slip meets a
  different slip in the next, and the additions never settle.

### 6. Check the whole

**Try the plugin as its user from start to end, and check every story and how close every key
result of the UX came, by the design's Verification.** Settle what it finds at the unit its cause lies in, then check the whole again.

- Rationale: each unit was checked on its own; what lies between units, and key results that show only
  over the whole, such as the time a whole run takes, show only here.

### 7. Check the structure

**Pass both `claude plugin validate <plugin-path> --strict` and `claude plugin validate
<marketplace-root> --strict`.**

- Rationale: a malformed manifest fails for every user at install, before any behavior is reached.

### 8. Release

**Release only on an explicit instruction from the user**, not on merge to `main`. Until then,
user-facing changes wait under CHANGELOG's `## [Unreleased]`.

- Rationale: users receive an update only when the version is bumped, so the user decides when it
  reaches them.

On the first release, and whenever a plugin is renamed or removed, **register it**: add one entry
under `plugins` in `.claude-plugin/marketplace.json` with `name`, `description`, `source` (e.g.
`./rn`) and `category`, and list it in the root `README.md` with a link to its README and a one-line
description. Change the two together.

- Rationale: Claude Code installs from the marketplace entry and people find the plugin from the
  root README; a plugin counts as shipped only once both can reach it.

**Write `version` in exactly one place, `plugin.json`, and always set it** (semver, e.g. `0.1.0`).
Decide the increment by the largest change from the user's side: major for a breaking change (on
`0.x`, minor instead), minor for a new or changed user-visible behavior, patch for no behavior
change.

- Rationale: when both are set, `plugin.json` wins over the marketplace entry, so a second copy is
  meaningless; `claude plugin validate --strict` fails when it is unset.

**Keep `CHANGELOG.md` in the plugin root** in [Keep a Changelog](https://keepachangelog.com)
format: one `## [x.y.z] - YYYY-MM-DD` per release, grouped under `Added` / `Changed` / `Fixed` /
`Removed` as they apply, with one line for every change a user would notice, written as `<what
changed> — <why it helps the user>`. Typos, refactors, internal docs and formatting get none. On a
release, rename `## [Unreleased]` to the version and date, and leave no empty `## [Unreleased]`
behind; it is made again when the next user-facing change lands.

- Rationale: the user reads what changed for them and why, in the same place for every plugin.

Who does what:

1. The assistant bumps `version` in `plugin.json`, finalizes `CHANGELOG.md`, makes the final check
   in `final-check.md`, commits and pushes.
2. The assistant asks the user to merge the pull request to `main`; it never merges it itself and
   never uses `--admin`.
   - Rationale: `main` is protected, and only the user can clear its required review.
3. The user merges, and says so.
4. The assistant tags `main` as `<plugin>--v<version>` (e.g. `rn--v0.2.0`) with `claude plugin tag
   --push` from the plugin directory, and publishes a GitHub Release for that tag with the
   CHANGELOG's matching section as the notes.
   - Rationale: this is Claude Code's own form: a plugin that depends on another with a version
     range resolves it against these tags, and the prefix lets each plugin version independently;
     the command also validates the plugin and refuses a tag that already exists. Release timing is
     read from tags and Releases, not from merge commits.
